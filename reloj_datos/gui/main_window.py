"""
gui/main_window.py

Ventana principal de "Software de Análisis Temporal". Une el flujo
completo: importar -> mapear columnas -> filtrar -> configurar ->
generar -> exportar, con menú convencional (Archivo / Generar Análisis /
Exportar / Idioma / Acerca de), título y subtítulo configurables, hasta
cuatro análisis de conteo, descripción del rango de fechas analizado, y
guardar/cargar la configuración completa (columnas + filtros + ajustes)
en un archivo .json. Soporta español, inglés y portugués, sin
reiniciar la app.
"""
import os
from typing import Optional

from PySide6.QtCore import QUrl
from PySide6.QtGui import QAction, QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
)

from ..branding import CREDITOS_ACERCA_DE_HTML, VERSION_APP, nombre_archivo_exportacion
from ..config_profile import aplicar_perfil, cargar_perfil, construir_perfil, guardar_perfil
from ..data.column_mapping import EventBuilder
from ..data.filters import EventFilter
from ..export.excel_exporter import ExcelExporter
from ..export.image_exporter import ImageExporter
from ..export.pdf_exporter import PDFExporter
from ..i18n import establecer_idioma, idioma_actual, tr
from ..processing.chart_generator import ChartGenerator
from ..processing.franjas_horarias import FranjaHoraria
from ..processing.modalidad_analyzer import ModalidadAnalyzer
from ..processing.reloj_matrix import RelojMatrix
from ..resources import ruta_documentacion, ruta_icono_png
from ..settings import guardar_idioma
from .config_widget import ConfigWidget
from .filter_widget import FilterWidget
from .idioma_bus import idioma_bus
from .import_widget import ImportWidget
from .mapping_widget import MappingWidget
from .results_widget import ResultsWidget
from .sidebar_nav import SidebarNav


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(ruta_icono_png()))
        self.resize(1300, 850)

        # Insumos del último análisis generado (se guardan acá para poder
        # regenerar una figura fresca en cada exportación, sin depender
        # de la figura ya embebida en la pantalla de resultados).
        self._reloj = None
        self._franjas = []
        self._secciones_ranking = []
        self._eventos_validos = []
        self._excluidos_24h = 0
        self._errores_parseo = 0
        self._descripcion_rango = ""
        self._descripcion_filtros = ""

        self.import_widget = ImportWidget()
        self.mapping_widget = MappingWidget()
        self.filter_widget = FilterWidget()
        self.config_widget = ConfigWidget()
        self.results_widget = ResultsWidget()

        self.tabs = SidebarNav()
        self.tabs.addTab(self.import_widget, tr("tab.importar"))
        self.tabs.addTab(self.mapping_widget, tr("tab.columnas"))
        self.tabs.addTab(self.filter_widget, tr("tab.filtros"))
        self.tabs.addTab(self.config_widget, tr("tab.configuracion"))
        self._indice_resultados = self.tabs.addTab(self.results_widget, tr("tab.resultados"))
        self.tabs.setTabEnabled(self._indice_resultados, False)
        self.setCentralWidget(self.tabs)

        self._conectar_señales_widgets()

        self._crear_menu()
        self.setStatusBar(QStatusBar())

        idioma_bus.idioma_cambiado.connect(self.retranslate)
        self.retranslate()

    def _conectar_señales_widgets(self) -> None:
        self.import_widget.archivo_cargado.connect(self._al_cargar_archivo)
        self.import_widget.guardar_configuracion_solicitada.connect(self._guardar_configuracion)
        self.import_widget.cargar_configuracion_solicitada.connect(self._cargar_configuracion)
        self.config_widget.generar_solicitado.connect(self._generar_reloj_de_datos)
        self.results_widget.exportar_pdf_solicitado.connect(self._exportar_pdf)

    def retranslate(self) -> None:
        self.setWindowTitle(f"{tr('app.nombre')} — {VERSION_APP}")
        self.tabs.setTabText(0, tr("tab.importar"))
        self.tabs.setTabText(1, tr("tab.columnas"))
        self.tabs.setTabText(2, tr("tab.filtros"))
        self.tabs.setTabText(3, tr("tab.configuracion"))
        self.tabs.setTabText(self._indice_resultados, tr("tab.resultados"))

        self.menu_archivo.setTitle(tr("menu.archivo"))
        self.accion_abrir.setText(tr("menu.archivo.abrir"))
        self.accion_cerrar.setText(tr("menu.archivo.cerrar"))
        self.accion_guardar_config.setText(tr("menu.archivo.guardar_config"))
        self.accion_cargar_config.setText(tr("menu.archivo.cargar_config"))
        self.accion_salir.setText(tr("menu.archivo.salir"))
        self.accion_generar.setText(tr("menu.generar"))
        self.menu_exportar.setTitle(tr("menu.exportar"))
        self.accion_exportar_excel.setText(tr("menu.exportar.excel"))
        self.accion_exportar_pdf.setText(tr("menu.exportar.pdf"))
        self.accion_exportar_png.setText(tr("menu.exportar.png"))
        self.menu_idioma.setTitle(tr("menu.idioma"))
        self.accion_idioma_es.setText(tr("menu.idioma.es"))
        self.accion_idioma_en.setText(tr("menu.idioma.en"))
        self.accion_idioma_pt.setText(tr("menu.idioma.pt"))
        self.accion_acerca.setText(tr("menu.acerca_de"))
        self.accion_docs.setText(tr("menu.docs"))

    # ------------------------------------------------------------------
    # Menú
    # ------------------------------------------------------------------
    def _crear_menu(self) -> None:
        barra_menu = self.menuBar()

        self.menu_archivo = barra_menu.addMenu(tr("menu.archivo"))
        self.accion_abrir = QAction(tr("menu.archivo.abrir"), self)
        self.accion_abrir.triggered.connect(self._abrir_archivo)
        self.menu_archivo.addAction(self.accion_abrir)

        self.accion_cerrar = QAction(tr("menu.archivo.cerrar"), self)
        self.accion_cerrar.triggered.connect(self._cerrar_analisis)
        self.menu_archivo.addAction(self.accion_cerrar)

        self.menu_archivo.addSeparator()

        # Guardar/Cargar configuración quedan habilitados recién cuando
        # hay un archivo importado (ver _al_cargar_archivo).
        self.accion_guardar_config = QAction(tr("menu.archivo.guardar_config"), self)
        self.accion_guardar_config.triggered.connect(self._guardar_configuracion)
        self.accion_guardar_config.setEnabled(False)
        self.menu_archivo.addAction(self.accion_guardar_config)

        self.accion_cargar_config = QAction(tr("menu.archivo.cargar_config"), self)
        self.accion_cargar_config.triggered.connect(self._cargar_configuracion)
        self.accion_cargar_config.setEnabled(False)
        self.menu_archivo.addAction(self.accion_cargar_config)

        self.menu_archivo.addSeparator()

        self.accion_salir = QAction(tr("menu.archivo.salir"), self)
        self.accion_salir.triggered.connect(self.close)
        self.menu_archivo.addAction(self.accion_salir)

        # "Generar Análisis" y "Acerca de" son acciones directas en la
        # barra de menú (un clic ejecuta la acción), no menús desplegables.
        self.accion_generar = QAction(tr("menu.generar"), self)
        self.accion_generar.triggered.connect(self._generar_reloj_de_datos)
        barra_menu.addAction(self.accion_generar)

        self.menu_exportar = barra_menu.addMenu(tr("menu.exportar"))
        self.accion_exportar_excel = QAction(tr("menu.exportar.excel"), self)
        self.accion_exportar_excel.triggered.connect(self._exportar_excel)
        self.menu_exportar.addAction(self.accion_exportar_excel)

        self.accion_exportar_pdf = QAction(tr("menu.exportar.pdf"), self)
        self.accion_exportar_pdf.triggered.connect(self._exportar_pdf)
        self.menu_exportar.addAction(self.accion_exportar_pdf)

        self.accion_exportar_png = QAction(tr("menu.exportar.png"), self)
        self.accion_exportar_png.triggered.connect(self._exportar_png)
        self.menu_exportar.addAction(self.accion_exportar_png)

        self.menu_idioma = barra_menu.addMenu(tr("menu.idioma"))
        self.accion_idioma_es = QAction(tr("menu.idioma.es"), self)
        self.accion_idioma_es.triggered.connect(lambda: self._cambiar_idioma("es"))
        self.menu_idioma.addAction(self.accion_idioma_es)
        self.accion_idioma_en = QAction(tr("menu.idioma.en"), self)
        self.accion_idioma_en.triggered.connect(lambda: self._cambiar_idioma("en"))
        self.menu_idioma.addAction(self.accion_idioma_en)
        self.accion_idioma_pt = QAction(tr("menu.idioma.pt"), self)
        self.accion_idioma_pt.triggered.connect(lambda: self._cambiar_idioma("pt"))
        self.menu_idioma.addAction(self.accion_idioma_pt)

        self.accion_acerca = QAction(tr("menu.acerca_de"), self)
        self.accion_acerca.triggered.connect(self._mostrar_acerca_de)
        barra_menu.addAction(self.accion_acerca)

        self.accion_docs = QAction(tr("menu.docs"), self)
        self.accion_docs.triggered.connect(self._abrir_documentacion)
        barra_menu.addAction(self.accion_docs)

    def _cambiar_idioma(self, idioma: str) -> None:
        if idioma == idioma_actual():
            return
        establecer_idioma(idioma)
        guardar_idioma(idioma)
        idioma_bus.idioma_cambiado.emit(idioma)
        # Si ya había un análisis generado, se vuelve a mostrar en el
        # nuevo idioma sin que el usuario tenga que generar de nuevo.
        if self._reloj is not None:
            self.results_widget.actualizar(
                self._reloj, self._franjas, self._secciones_ranking,
                self.config_widget.titulo_reloj(), self.config_widget.subtitulo_reloj(),
                self._descripcion_rango, self._excluidos_24h, self._errores_parseo,
                descripcion_filtros=self._descripcion_filtros, color_reloj=self.config_widget.color_reloj(),
                incluir_resumen_ejecutivo=self.config_widget.resumen_ejecutivo_habilitado(),
            )

    def _mostrar_acerca_de(self) -> None:
        QMessageBox.about(self, tr("dialogo.acerca_de.titulo"), CREDITOS_ACERCA_DE_HTML)

    def _abrir_documentacion(self) -> None:
        ruta = ruta_documentacion(idioma_actual())
        if not os.path.isfile(ruta):
            QMessageBox.warning(self, tr("menu.docs"), tr("dialogo.docs_no_encontrada", ruta=ruta))
            return
        abierto = QDesktopServices.openUrl(QUrl.fromLocalFile(ruta))
        if not abierto:
            QMessageBox.warning(self, tr("menu.docs"), tr("dialogo.no_se_pudo_abrir", ruta=ruta))

    def _abrir_archivo(self) -> None:
        self.tabs.setCurrentWidget(self.import_widget)

    def _cerrar_analisis(self) -> None:
        respuesta = QMessageBox.question(
            self, tr("dialogo.cerrar_analisis.titulo"), tr("dialogo.cerrar_analisis.texto"),
        )
        if respuesta != QMessageBox.Yes:
            return

        self.import_widget = ImportWidget()
        self.mapping_widget = MappingWidget()
        self.filter_widget = FilterWidget()
        self.config_widget = ConfigWidget()
        self.results_widget = ResultsWidget()

        for _ in range(self.tabs.count()):
            self.tabs.removeTab(0)

        self.tabs.addTab(self.import_widget, tr("tab.importar"))
        self.tabs.addTab(self.mapping_widget, tr("tab.columnas"))
        self.tabs.addTab(self.filter_widget, tr("tab.filtros"))
        self.tabs.addTab(self.config_widget, tr("tab.configuracion"))
        self._indice_resultados = self.tabs.addTab(self.results_widget, tr("tab.resultados"))
        self.tabs.setTabEnabled(self._indice_resultados, False)
        self._conectar_señales_widgets()
        self.accion_guardar_config.setEnabled(False)
        self.accion_cargar_config.setEnabled(False)

        self._reloj = None
        self._franjas = []
        self._secciones_ranking = []
        self._eventos_validos = []
        self._descripcion_rango = ""
        self._descripcion_filtros = ""
        self.statusBar().showMessage(tr("status.analisis_cerrado"), 4000)

    def _al_cargar_archivo(self, ruta: str) -> None:
        columnas = self.import_widget.columnas_disponibles()
        self.mapping_widget.cargar_columnas(columnas)
        self.filter_widget.cargar_dataframe(self.import_widget.dataframe())
        self.accion_guardar_config.setEnabled(True)
        self.accion_cargar_config.setEnabled(True)
        self.statusBar().showMessage(tr("status.archivo_cargado", ruta=ruta), 5000)
        self.tabs.setCurrentWidget(self.mapping_widget)

    # ------------------------------------------------------------------
    # Guardar / cargar configuración (columnas + filtros + ajustes)
    # ------------------------------------------------------------------
    def _guardar_configuracion(self) -> None:
        if self.import_widget.dataframe() is None:
            QMessageBox.information(
                self, tr("dialogo.falta_archivo_config.titulo"), tr("dialogo.falta_archivo_config.texto")
            )
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, tr("dialogo.guardar_config.titulo"), "configuracion_reloj_datos.json", "JSON (*.json)"
        )
        if not ruta:
            return
        try:
            perfil = construir_perfil(self.mapping_widget, self.filter_widget, self.config_widget)
            guardar_perfil(perfil, ruta)
            QMessageBox.information(
                self, tr("dialogo.guardar_config.titulo"), tr("dialogo.guardar_config.ok", ruta=ruta)
            )
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(
                self, tr("dialogo.guardar_config.titulo"), tr("dialogo.guardar_config.error", exc=exc)
            )

    def _cargar_configuracion(self) -> None:
        if self.import_widget.dataframe() is None:
            QMessageBox.information(
                self, tr("dialogo.falta_archivo_config.titulo"), tr("dialogo.falta_archivo_config.texto")
            )
            return
        ruta, _ = QFileDialog.getOpenFileName(self, tr("dialogo.cargar_config.titulo"), "", "JSON (*.json)")
        if not ruta:
            return
        try:
            perfil = cargar_perfil(ruta)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(
                self, tr("dialogo.cargar_config.titulo"), tr("dialogo.cargar_config.error", exc=exc)
            )
            return

        columnas_disponibles = self.import_widget.columnas_disponibles()
        columnas_faltantes = aplicar_perfil(
            perfil, self.mapping_widget, self.filter_widget, self.config_widget, columnas_disponibles
        )
        if columnas_faltantes:
            QMessageBox.warning(
                self, tr("dialogo.cargar_config.columnas_faltantes.titulo"),
                tr("dialogo.cargar_config.columnas_faltantes.texto", columnas=", ".join(columnas_faltantes)),
            )
        else:
            QMessageBox.information(self, tr("dialogo.cargar_config.titulo"), tr("dialogo.cargar_config.ok"))

    def _mapa_columna_a_atributo(self, mapping) -> dict:
        """Traduce nombre de columna del archivo -> nombre de atributo de Event,
        para que el filtro por columnas funcione tanto con campos fijos como extra."""
        resultado = {}
        pares = [
            (mapping.id_evento, "id_evento"),
            (mapping.dependencia, "dependencia"),
            (mapping.modalidad, "modalidad"),
            (mapping.tipo_delito, "tipo_delito"),
            (mapping.zona, "zona"),
            (mapping.delito, "delito"),
        ]
        for columna, atributo in pares:
            if columna:
                resultado[columna] = atributo
        return resultado

    @staticmethod
    def _calcular_descripcion_rango(eventos) -> str:
        """Arma el texto descriptivo del período efectivamente analizado,
        a partir del rango real de los eventos que entraron al cálculo."""
        if not eventos:
            return ""
        minimo = min(e.inicio for e in eventos)
        maximo = max(e.fin for e in eventos)
        formato = "%d/%m/%Y %H:%M"
        return tr("reloj.periodo_analizado", desde=minimo.strftime(formato), hasta=maximo.strftime(formato))

    def _calcular_ranking(self, analisis_widget, eventos, atributo_evento, nombre_error) -> Optional[list]:
        """
        Corre un bloque de análisis de conteo (modalidades, delitos,
        dependencia o zona) si está habilitado, usando la columna que ya
        se mapeó en la pestaña "2. Columnas". Devuelve el ranking, None
        si está deshabilitado, o False si falta mapear la columna
        correspondiente (y ya avisó).
        """
        if not analisis_widget.habilitado():
            return None
        if not atributo_evento:
            nombre_traducido = tr(f"nombre.{nombre_error}")
            QMessageBox.warning(
                self, tr("dialogo.falta_columna.titulo", nombre=nombre_traducido),
                tr("dialogo.falta_columna.texto", nombre=nombre_traducido),
            )
            return False
        analyzer = ModalidadAnalyzer(separador=analisis_widget.separador())
        analyzer.procesar(eventos, atributo_evento)
        return analyzer.ranking(top=analisis_widget.top())

    # ------------------------------------------------------------------
    # Generar análisis
    # ------------------------------------------------------------------
    def _generar_reloj_de_datos(self) -> None:
        df = self.import_widget.dataframe()
        if df is None:
            QMessageBox.warning(self, tr("dialogo.falta_importar.titulo"), tr("dialogo.falta_importar.texto"))
            self.tabs.setCurrentWidget(self.import_widget)
            return

        mapping = self.mapping_widget.obtener_mapping()
        if not mapping.es_completo():
            QMessageBox.warning(
                self, tr("dialogo.columnas_incompletas.titulo"), tr("dialogo.columnas_incompletas.texto"),
            )
            return

        builder = EventBuilder(mapping)
        eventos = builder.construir(df)
        self._errores_parseo = builder.errores_parseo

        atributo_de_columna = self._mapa_columna_a_atributo(mapping)
        filtro: EventFilter = self.filter_widget.obtener_filtro(atributo_de_columna)
        eventos_filtrados = filtro.aplicar(eventos)

        if not eventos_filtrados:
            QMessageBox.information(self, tr("dialogo.sin_resultados.titulo"), tr("dialogo.sin_resultados.texto"))
            return

        # Los excluidos por superar 24 hs se calculan DESPUÉS de filtrar:
        # tienen que ser un recorte del conjunto que el usuario realmente
        # está analizando (según sus filtros), no del archivo completo.
        eventos_validos = [e for e in eventos_filtrados if not e.excede_24_horas()]
        self._excluidos_24h = len(eventos_filtrados) - len(eventos_validos)

        if not eventos_validos:
            QMessageBox.information(self, tr("dialogo.sin_resultados.titulo"), tr("dialogo.sin_resultados.texto"))
            return

        reloj = RelojMatrix()
        reloj.construir(eventos_validos)

        franjero = FranjaHoraria(
            self.config_widget.cantidad_franjas(),
            hora_inicio=self.config_widget.hora_inicio_franjas(),
        )
        franjas = franjero.calcular(reloj.total_por_hora())

        # Los análisis opcionales usan directamente las columnas ya
        # mapeadas en "2. Columnas" (Modalidad / DelitoCOP / Dependencia
        # / Zona), sin volver a pedirlas en Configuración.
        atributo_modalidad = "modalidad" if mapping.modalidad else None
        atributo_delito = "delito" if mapping.delito else None
        atributo_dependencia = "dependencia" if mapping.dependencia else None
        atributo_zona = "zona" if mapping.zona else None

        ranking_modalidades = self._calcular_ranking(
            self.config_widget.analisis_modalidades, eventos_validos, atributo_modalidad, "modalidades"
        )
        if ranking_modalidades is False:
            return
        ranking_delitos = self._calcular_ranking(
            self.config_widget.analisis_delitos, eventos_validos, atributo_delito, "delitos"
        )
        if ranking_delitos is False:
            return
        ranking_dependencia = self._calcular_ranking(
            self.config_widget.analisis_dependencia, eventos_validos, atributo_dependencia, "dependencia"
        )
        if ranking_dependencia is False:
            return
        ranking_zona = self._calcular_ranking(
            self.config_widget.analisis_zona, eventos_validos, atributo_zona, "zona"
        )
        if ranking_zona is False:
            return

        secciones_ranking = [
            (tr("graficos.ranking_modalidades"), ranking_modalidades or [], tr("tabla.modalidad")),
            (tr("graficos.ranking_delitos"), ranking_delitos or [], tr("tabla.delito")),
            (tr("graficos.ranking_dependencia"), ranking_dependencia or [], tr("tabla.dependencia")),
            (tr("graficos.ranking_zona"), ranking_zona or [], tr("tabla.zona")),
        ]

        self._reloj = reloj
        self._franjas = franjas
        self._secciones_ranking = secciones_ranking
        self._eventos_validos = eventos_validos
        self._descripcion_rango = self._calcular_descripcion_rango(eventos_validos)
        self._descripcion_filtros = self.filter_widget.descripcion_filtros()

        self.results_widget.actualizar(
            reloj, franjas, secciones_ranking,
            self.config_widget.titulo_reloj(), self.config_widget.subtitulo_reloj(), self._descripcion_rango,
            self._excluidos_24h, self._errores_parseo,
            descripcion_filtros=self._descripcion_filtros, color_reloj=self.config_widget.color_reloj(),
            incluir_resumen_ejecutivo=self.config_widget.resumen_ejecutivo_habilitado(),
        )

        self.tabs.setTabEnabled(self._indice_resultados, True)
        self.tabs.setCurrentWidget(self.results_widget)
        self.statusBar().showMessage(tr("status.generado_ok"), 5000)

    def _hay_resultados(self) -> bool:
        if self._reloj is None:
            QMessageBox.information(self, tr("dialogo.nada_exportar.titulo"), tr("dialogo.nada_exportar.texto"))
            return False
        return True

    def _construir_figuras_para_exportar(self):
        """Regenera las páginas del informe a partir de los datos del
        último análisis, en vez de reutilizar las figuras ya embebidas
        en la pantalla de resultados (evita conflictos con el canvas de
        Qt al exportar)."""
        return ChartGenerator.figuras_informe_completo(
            self._reloj,
            self._franjas,
            self.config_widget.titulo_reloj(),
            self._descripcion_rango,
            self._secciones_ranking,
            subtitulo=self.config_widget.subtitulo_reloj(),
            total_eventos=self._reloj.eventos_procesados,
            excluidos_24h=self._excluidos_24h,
            descripcion_filtros=self._descripcion_filtros,
            color_reloj=self.config_widget.color_reloj(),
            incluir_resumen_ejecutivo=self.config_widget.resumen_ejecutivo_habilitado(),
        )

    def _preguntar_abrir_archivo(self, ruta: str) -> None:
        respuesta = QMessageBox.question(
            self, tr("dialogo.exportacion_exitosa.titulo"), tr("dialogo.exportacion_exitosa.texto", ruta=ruta),
        )
        if respuesta == QMessageBox.Yes:
            abierto = QDesktopServices.openUrl(QUrl.fromLocalFile(ruta))
            if not abierto:
                QMessageBox.warning(
                    self, tr("dialogo.exportacion_exitosa.titulo"), tr("dialogo.no_se_pudo_abrir", ruta=ruta)
                )

    def _preguntar_abrir_archivo_multiple(self, rutas: list) -> None:
        if not rutas:
            return
        carpeta = os.path.dirname(rutas[0])
        respuesta = QMessageBox.question(
            self, tr("dialogo.exportacion_exitosa.titulo"),
            tr("dialogo.exportacion_exitosa.texto_multiple", n=len(rutas), ruta=carpeta),
        )
        if respuesta == QMessageBox.Yes:
            abierto = QDesktopServices.openUrl(QUrl.fromLocalFile(rutas[0]))
            if not abierto:
                QMessageBox.warning(
                    self, tr("dialogo.exportacion_exitosa.titulo"), tr("dialogo.no_se_pudo_abrir", ruta=rutas[0])
                )

    # ------------------------------------------------------------------
    # Exportación
    # ------------------------------------------------------------------
    def _exportar_excel(self) -> None:
        if not self._hay_resultados():
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "Excel", nombre_archivo_exportacion("xlsx"), "Excel (*.xlsx)"
        )
        if not ruta:
            return
        try:
            ExcelExporter().exportar(
                ruta,
                self._reloj,
                self.config_widget.titulo_reloj(),
                self._descripcion_rango,
                self._franjas,
                self._secciones_ranking,
                subtitulo=self.config_widget.subtitulo_reloj(),
                total_eventos=self._reloj.eventos_procesados,
                excluidos_24h=self._excluidos_24h,
                descripcion_filtros=self._descripcion_filtros,
                color_reloj=self.config_widget.color_reloj(),
                incluir_resumen_ejecutivo=self.config_widget.resumen_ejecutivo_habilitado(),
            )
            self.statusBar().showMessage(tr("status.exportado", ruta=ruta), 5000)
            self._preguntar_abrir_archivo(ruta)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, tr("dialogo.error_exportar.titulo"), tr("dialogo.error_excel", exc=exc))

    def _exportar_pdf(self) -> None:
        if not self._hay_resultados():
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "PDF", nombre_archivo_exportacion("pdf"), "PDF (*.pdf)"
        )
        if not ruta:
            return
        try:
            PDFExporter().exportar(
                ruta,
                self._reloj,
                self.config_widget.titulo_reloj(),
                self._descripcion_rango,
                self._franjas,
                self._secciones_ranking,
                subtitulo=self.config_widget.subtitulo_reloj(),
                total_eventos=self._reloj.eventos_procesados,
                excluidos_24h=self._excluidos_24h,
                descripcion_filtros=self._descripcion_filtros,
                color_reloj=self.config_widget.color_reloj(),
                incluir_resumen_ejecutivo=self.config_widget.resumen_ejecutivo_habilitado(),
            )
            cantidad_paginas = 2 + len([s for s in self._secciones_ranking if s[1]])
            if self.config_widget.resumen_ejecutivo_habilitado():
                cantidad_paginas += 1
            self.statusBar().showMessage(tr("status.exportado_pdf", ruta=ruta, n=cantidad_paginas), 5000)
            self._preguntar_abrir_archivo(ruta)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, tr("dialogo.error_exportar.titulo"), tr("dialogo.error_pdf", exc=exc))

    def _exportar_png(self) -> None:
        if not self._hay_resultados():
            return
        ruta, _ = QFileDialog.getSaveFileName(
            self, "PNG", nombre_archivo_exportacion("png"), "PNG (*.png)"
        )
        if not ruta:
            return
        try:
            figuras = self._construir_figuras_para_exportar()
            rutas = ImageExporter.exportar_paginas(figuras, ruta)
            self.statusBar().showMessage(tr("status.exportado_png", n=len(rutas)), 5000)
            self._preguntar_abrir_archivo_multiple(rutas)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, tr("dialogo.error_exportar.titulo"), tr("dialogo.error_imagen", exc=exc))
