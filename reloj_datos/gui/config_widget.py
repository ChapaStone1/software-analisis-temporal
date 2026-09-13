"""
gui/config_widget.py

Sección 7.3 - Totales por Franja Horaria (Configurable): el usuario
elige 4, 3 o 2 franjas, y desde qué hora arranca la primera (por
defecto 00:00). El Reloj de Datos en sí no cambia de disposición por
esto; solo las sumatorias por franja y los gráficos.

Sección 8.4 - Análisis de Modalidades y Análisis de Delitos (ambos
opcionales, mismo motor de conteo/ranking): casilla para activar cada
uno, separador configurable (solo para modalidades, ya que delitos no
combina valores en una misma celda) y cantidad a graficar. Usan
directamente las columnas "Modalidad" y "DelitoCOP" ya elegidas en la
pestaña "2. Columnas" — acá no se vuelve a pedir cuál es la columna.

También incluye el título/subtítulo del Reloj de Datos y un botón para
disparar la generación del análisis sin tener que ir al menú.
"""
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from ..i18n import tr
from ..processing.color_scale import COLORES_RELOJ
from .idioma_bus import idioma_bus


class AnalisisConteoWidget(QGroupBox):
    """
    Bloque reutilizable para un análisis de conteo/ranking (Modalidades
    o Delitos): activar/desactivar, separador opcional y cantidad a
    graficar. La columna a analizar NO se elige acá: se usa la que ya
    se mapeó en la pestaña "2. Columnas".
    """

    def __init__(self, clave_titulo: str, incluir_separador: bool, parent=None):
        super().__init__("", parent)
        self._clave_titulo = clave_titulo
        form = QFormLayout(self)

        self.check_habilitado = QCheckBox("")
        form.addRow(self.check_habilitado)

        self.input_separador: Optional[QLineEdit] = None
        self._label_separador = None
        if incluir_separador:
            self.input_separador = QLineEdit(",")
            self.input_separador.setEnabled(False)
            self.input_separador.setMaximumWidth(60)
            self._label_separador = QLabel(tr("config.separador"))
            form.addRow(self._label_separador, self.input_separador)

        self._label_top = QLabel(tr("config.cantidad_graficar"))
        self.spin_top = QSpinBox()
        self.spin_top.setRange(0, 500)
        self.spin_top.setValue(20)
        self.spin_top.setSpecialValueText(tr("config.todas"))
        self.spin_top.setEnabled(False)
        form.addRow(self._label_top, self.spin_top)

        self.check_habilitado.toggled.connect(self.spin_top.setEnabled)
        if self.input_separador is not None:
            self.check_habilitado.toggled.connect(self.input_separador.setEnabled)

        self.retranslate()

    def retranslate(self) -> None:
        titulo = tr(self._clave_titulo)
        self.setTitle(titulo)
        self.check_habilitado.setText(tr("config.realizar", titulo=titulo.lower()))
        if self._label_separador is not None:
            self._label_separador.setText(tr("config.separador"))
        self._label_top.setText(tr("config.cantidad_graficar"))
        self.spin_top.setSpecialValueText(tr("config.todas"))

    def habilitado(self) -> bool:
        return self.check_habilitado.isChecked()

    def separador(self) -> Optional[str]:
        if self.input_separador is None:
            return None
        return self.input_separador.text() or ","

    def top(self) -> Optional[int]:
        valor = self.spin_top.value()
        return None if valor == 0 else valor

    def a_dict(self) -> dict:
        datos = {"habilitado": self.habilitado(), "top": self.spin_top.value()}
        if self.input_separador is not None:
            datos["separador"] = self.input_separador.text()
        return datos

    def aplicar_dict(self, datos: dict) -> None:
        self.check_habilitado.setChecked(bool(datos.get("habilitado", False)))
        if "top" in datos:
            self.spin_top.setValue(int(datos["top"]))
        if self.input_separador is not None and "separador" in datos:
            self.input_separador.setText(datos["separador"])


class ConfigWidget(QWidget):
    generar_solicitado = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.grupo_titulo = QGroupBox(tr("config.grupo_titulo"))
        form_titulo = QFormLayout(self.grupo_titulo)
        self._label_titulo = QLabel(tr("config.titulo_a_mostrar"))
        self.input_titulo = QLineEdit(tr("reloj.titulo_defecto"))
        form_titulo.addRow(self._label_titulo, self.input_titulo)
        self._label_subtitulo = QLabel(tr("config.subtitulo"))
        self.input_subtitulo = QLineEdit("")
        self.input_subtitulo.setPlaceholderText(tr("config.subtitulo_placeholder"))
        form_titulo.addRow(self._label_subtitulo, self.input_subtitulo)

        self._label_color = QLabel(tr("config.color_reloj"))
        self.combo_color = QComboBox()
        self._claves_color = list(COLORES_RELOJ.keys())
        for clave in self._claves_color:
            self.combo_color.addItem(tr(f"color.{clave}"))
        form_titulo.addRow(self._label_color, self.combo_color)

        layout.addWidget(self.grupo_titulo)

        self.grupo_franjas = QGroupBox(tr("config.grupo_franjas"))
        form_franjas = QFormLayout(self.grupo_franjas)

        self._label_hora_inicio = QLabel(tr("config.hora_inicio_franjas"))
        self.combo_hora_inicio = QComboBox()
        self.combo_hora_inicio.addItems([f"{h:02d}:00" for h in range(24)])
        self.combo_hora_inicio.currentIndexChanged.connect(self._actualizar_etiquetas_franjas)
        form_franjas.addRow(self._label_hora_inicio, self.combo_hora_inicio)

        self.radio_4 = QRadioButton()
        self.radio_3 = QRadioButton()
        self.radio_2 = QRadioButton()
        self.radio_4.setChecked(True)
        self.grupo_botones_franja = QButtonGroup(self)
        for boton, valor in ((self.radio_4, 4), (self.radio_3, 3), (self.radio_2, 2)):
            self.grupo_botones_franja.addButton(boton, valor)
            form_franjas.addRow(boton)

        layout.addWidget(self.grupo_franjas)
        self._actualizar_etiquetas_franjas()

        self.analisis_modalidades = AnalisisConteoWidget("config.modalidades_titulo", incluir_separador=True)
        layout.addWidget(self.analisis_modalidades)

        self.analisis_delitos = AnalisisConteoWidget("config.delitos_titulo", incluir_separador=False)
        layout.addWidget(self.analisis_delitos)

        self.analisis_dependencia = AnalisisConteoWidget("config.dependencia_titulo", incluir_separador=False)
        layout.addWidget(self.analisis_dependencia)

        self.analisis_zona = AnalisisConteoWidget("config.zona_titulo", incluir_separador=False)
        layout.addWidget(self.analisis_zona)

        self.check_resumen_ejecutivo = QCheckBox(tr("config.resumen_ejecutivo"))
        layout.addWidget(self.check_resumen_ejecutivo)

        layout.addStretch(1)

        fila_boton = QHBoxLayout()
        self.boton_generar = QPushButton(tr("config.generar_boton"))
        self.boton_generar.setStyleSheet(
            "font-weight: bold; font-size: 15px; padding: 14px 28px; border-radius: 6px;"
        )
        self.boton_generar.clicked.connect(self.generar_solicitado.emit)
        fila_boton.addStretch(1)
        fila_boton.addWidget(self.boton_generar)
        layout.addLayout(fila_boton)

        idioma_bus.idioma_cambiado.connect(self.retranslate)

    def retranslate(self) -> None:
        self.grupo_titulo.setTitle(tr("config.grupo_titulo"))
        self._label_titulo.setText(tr("config.titulo_a_mostrar"))
        self._label_subtitulo.setText(tr("config.subtitulo"))
        self.input_subtitulo.setPlaceholderText(tr("config.subtitulo_placeholder"))
        self._label_color.setText(tr("config.color_reloj"))
        indice_color = self.combo_color.currentIndex()
        self.combo_color.blockSignals(True)
        self.combo_color.clear()
        for clave in self._claves_color:
            self.combo_color.addItem(tr(f"color.{clave}"))
        self.combo_color.setCurrentIndex(indice_color)
        self.combo_color.blockSignals(False)

        self.grupo_franjas.setTitle(tr("config.grupo_franjas"))
        self._label_hora_inicio.setText(tr("config.hora_inicio_franjas"))
        self._actualizar_etiquetas_franjas()

        self.analisis_modalidades.retranslate()
        self.analisis_delitos.retranslate()
        self.analisis_dependencia.retranslate()
        self.analisis_zona.retranslate()
        self.check_resumen_ejecutivo.setText(tr("config.resumen_ejecutivo"))
        self.boton_generar.setText(tr("config.generar_boton"))

    def _actualizar_etiquetas_franjas(self) -> None:
        """Actualiza el texto de cada opción para mostrar en qué horas
        queda esa franja según la hora de inicio elegida, por ejemplo
        '4 franjas de 6 horas (07-13-19-01)'."""
        hora_inicio = self.hora_inicio_franjas()
        for boton, cantidad in ((self.radio_4, 4), (self.radio_3, 3), (self.radio_2, 2)):
            horas_por_franja = 24 // cantidad
            inicios = [(hora_inicio + i * horas_por_franja) % 24 for i in range(cantidad)]
            rango = "-".join(f"{h:02d}" for h in inicios)
            boton.setText(tr("config.franjas_n_horas", n=cantidad, h=horas_por_franja, rango=rango))

    def cantidad_franjas(self) -> int:
        return self.grupo_botones_franja.checkedId()

    def hora_inicio_franjas(self) -> int:
        return self.combo_hora_inicio.currentIndex()

    def titulo_reloj(self) -> str:
        return self.input_titulo.text().strip() or tr("reloj.titulo_defecto")

    def subtitulo_reloj(self) -> str:
        return self.input_subtitulo.text().strip()

    def color_reloj(self) -> str:
        indice = self.combo_color.currentIndex()
        if 0 <= indice < len(self._claves_color):
            return self._claves_color[indice]
        return "rojo"

    def resumen_ejecutivo_habilitado(self) -> bool:
        return self.check_resumen_ejecutivo.isChecked()

    # --- Guardar / cargar configuración ---

    def a_dict(self) -> dict:
        return {
            "titulo": self.input_titulo.text(),
            "subtitulo": self.input_subtitulo.text(),
            "color": self.color_reloj(),
            "cantidad_franjas": self.cantidad_franjas(),
            "hora_inicio_franjas": self.hora_inicio_franjas(),
            "analisis_modalidades": self.analisis_modalidades.a_dict(),
            "analisis_delitos": self.analisis_delitos.a_dict(),
            "analisis_dependencia": self.analisis_dependencia.a_dict(),
            "analisis_zona": self.analisis_zona.a_dict(),
            "resumen_general": self.resumen_ejecutivo_habilitado(),
        }

    def aplicar_dict(self, datos: dict) -> None:
        if datos.get("titulo"):
            self.input_titulo.setText(datos["titulo"])
        if "subtitulo" in datos:
            self.input_subtitulo.setText(datos["subtitulo"])
        if datos.get("color") in self._claves_color:
            self.combo_color.setCurrentIndex(self._claves_color.index(datos["color"]))
        indice_hora = datos.get("hora_inicio_franjas")
        if isinstance(indice_hora, int) and 0 <= indice_hora < 24:
            self.combo_hora_inicio.setCurrentIndex(indice_hora)
        cantidad = datos.get("cantidad_franjas")
        if cantidad is not None:
            boton = self.grupo_botones_franja.button(cantidad)
            if boton is not None:
                boton.setChecked(True)
        if "analisis_modalidades" in datos:
            self.analisis_modalidades.aplicar_dict(datos["analisis_modalidades"])
        if "analisis_delitos" in datos:
            self.analisis_delitos.aplicar_dict(datos["analisis_delitos"])
        if "analisis_dependencia" in datos:
            self.analisis_dependencia.aplicar_dict(datos["analisis_dependencia"])
        if "analisis_zona" in datos:
            self.analisis_zona.aplicar_dict(datos["analisis_zona"])
        if "resumen_general" in datos:
            self.check_resumen_ejecutivo.setChecked(bool(datos["resumen_general"]))
