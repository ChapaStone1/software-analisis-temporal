"""
gui/results_widget.py

Muestra los resultados generados en pantalla, como una serie de páginas
apiladas (igual que en el PDF exportado): el Reloj de Datos, el gráfico
por día, y una página por cada análisis de conteo habilitado. La
cantidad de páginas es variable. También tiene su propio botón para
exportar directamente a PDF.
"""
from typing import List, Optional, Sequence

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget

from ..processing.chart_generator import ChartGenerator, SeccionRanking
from ..processing.franjas_horarias import ResultadoFranja
from ..processing.reloj_matrix import RelojMatrix
from ..i18n import tr
from .chart_canvas import ChartCanvas
from .idioma_bus import idioma_bus


class ResultsWidget(QWidget):
    exportar_pdf_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout_externo = QVBoxLayout(self)
        layout_externo.setContentsMargins(0, 0, 0, 0)

        fila_superior = QHBoxLayout()
        self.resumen_label = QLabel(tr("resultados.pendiente"))
        self.resumen_label.setContentsMargins(10, 8, 10, 4)
        fila_superior.addWidget(self.resumen_label, stretch=1)

        self.boton_exportar_pdf = QPushButton(tr("resultados.exportar_pdf"))
        self.boton_exportar_pdf.clicked.connect(self.exportar_pdf_solicitado.emit)
        fila_superior.addWidget(self.boton_exportar_pdf)
        layout_externo.addLayout(fila_superior)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        layout_externo.addWidget(self._scroll, stretch=1)

        self._contenedor = QWidget()
        self._layout_contenedor = QVBoxLayout(self._contenedor)
        self._scroll.setWidget(self._contenedor)

        # Lista de bloques de widgets por página (cada bloque = [etiqueta, canvas, separador]).
        self._bloques_paginas: List[List[QWidget]] = []

        self.reloj: Optional[RelojMatrix] = None
        self.franjas: List[ResultadoFranja] = []
        self.secciones_ranking: List[SeccionRanking] = []
        self._ultimos_datos_resumen = None
        self._figuras_actuales: List = []

        idioma_bus.idioma_cambiado.connect(self.retranslate)

    def retranslate(self) -> None:
        self.boton_exportar_pdf.setText(tr("resultados.exportar_pdf"))
        if self._ultimos_datos_resumen is None:
            self.resumen_label.setText(tr("resultados.pendiente"))
        else:
            n, ex, er = self._ultimos_datos_resumen
            self.resumen_label.setText(tr("resultados.resumen", n=n, ex=ex, er=er))
        for indice, bloque in enumerate(self._bloques_paginas, start=1):
            etiqueta_widget = bloque[0]
            etiqueta_widget.setText(tr("resultados.pagina_n", n=indice, total=len(self._bloques_paginas)))

    def actualizar(
        self,
        reloj: RelojMatrix,
        franjas: List[ResultadoFranja],
        secciones_ranking: Optional[Sequence[SeccionRanking]],
        titulo: str,
        subtitulo: str,
        descripcion_rango: str,
        excluidos_24h: int,
        errores_parseo: int,
        descripcion_filtros: str = "",
        color_reloj: str = "rojo",
        incluir_resumen_ejecutivo: bool = False,
    ) -> None:
        self.reloj = reloj
        self.franjas = franjas
        self.secciones_ranking = list(secciones_ranking or [])

        resumen = tr("resultados.resumen", n=reloj.eventos_procesados, ex=excluidos_24h, er=errores_parseo)
        self._ultimos_datos_resumen = (reloj.eventos_procesados, excluidos_24h, errores_parseo)
        self.resumen_label.setText(resumen)

        figuras = ChartGenerator.figuras_informe_completo(
            reloj, franjas, titulo, descripcion_rango, self.secciones_ranking, subtitulo=subtitulo,
            total_eventos=reloj.eventos_procesados, excluidos_24h=excluidos_24h,
            descripcion_filtros=descripcion_filtros, color_reloj=color_reloj,
            incluir_resumen_ejecutivo=incluir_resumen_ejecutivo,
        )
        self._figuras_actuales = figuras

        # Saca todas las páginas mostradas anteriormente.
        for bloque in self._bloques_paginas:
            for widget in bloque:
                self._layout_contenedor.removeWidget(widget)
                widget.setParent(None)
                widget.deleteLater()
        self._bloques_paginas = []

        for indice, figura in enumerate(figuras, start=1):
            etiqueta = tr("resultados.pagina_n", n=indice, total=len(figuras))
            self._bloques_paginas.append(self._agregar_pagina(figura, etiqueta))

    def _agregar_pagina(self, figura, etiqueta: str) -> List[QWidget]:
        titulo_pagina = QLabel(etiqueta)
        titulo_pagina.setStyleSheet("font-weight: bold; color: #555; padding: 8px 4px 2px 4px;")
        self._layout_contenedor.addWidget(titulo_pagina)

        canvas = ChartCanvas(figura)
        # Tamaño FIJO (no solo mínimo) según las pulgadas reales de la
        # figura: así el canvas nunca se estira ni se achica según el
        # ancho de la ventana, y siempre se ve igual que en el PDF
        # exportado. El scroll de abajo/derecha se encarga del resto.
        dpi = 100
        ancho_pulgadas, alto_pulgadas = figura.get_size_inches()
        canvas.setFixedSize(int(ancho_pulgadas * dpi), int(alto_pulgadas * dpi))
        self._layout_contenedor.addWidget(canvas, 0, Qt.AlignmentFlag.AlignLeft)

        separador = QFrame()
        separador.setFrameShape(QFrame.Shape.HLine)
        separador.setStyleSheet("color: #ccc;")
        self._layout_contenedor.addWidget(separador)

        return [titulo_pagina, canvas, separador]

    def figuras_completas(self) -> List:
        return self._figuras_actuales
