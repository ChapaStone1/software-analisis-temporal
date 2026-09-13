"""
gui/mapping_widget.py

Sección 2.2 - Selección de columnas.
Todas las columnas son obligatorias: fecha/hora de inicio y fin,
dependencia policial, modalidad, zona y DelitoCOP.

Además, opcionalmente, se puede fijar a mano el formato exacto de
fecha y hora del archivo (por si la detección automática no da con el
formato real de algún archivo en particular).
"""
from typing import List, Optional

from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ..data.column_mapping import OPCIONES_FORMATO_FECHA, OPCIONES_FORMATO_HORA, ColumnMapping
from ..i18n import tr
from .idioma_bus import idioma_bus


class MappingWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.grupo_obligatorio = QGroupBox(tr("mapeo.grupo_obligatorias"))
        form = QFormLayout(self.grupo_obligatorio)

        self.combo_fecha_inicio = QComboBox()
        self.combo_hora_inicio = QComboBox()
        self.combo_fecha_fin = QComboBox()
        self.combo_hora_fin = QComboBox()
        self.combo_dependencia = QComboBox()
        self.combo_modalidad = QComboBox()
        self.combo_zona = QComboBox()
        self.combo_delito = QComboBox()

        self._claves = [
            "mapeo.fecha_inicio", "mapeo.hora_inicio", "mapeo.fecha_fin", "mapeo.hora_fin",
            "mapeo.dependencia", "mapeo.modalidad", "mapeo.zona", "mapeo.delito",
        ]
        self._combos = [
            self.combo_fecha_inicio, self.combo_hora_inicio, self.combo_fecha_fin, self.combo_hora_fin,
            self.combo_dependencia, self.combo_modalidad, self.combo_zona, self.combo_delito,
        ]
        self._labels = [QLabel(tr(clave)) for clave in self._claves]
        for label, combo in zip(self._labels, self._combos):
            form.addRow(label, combo)

        layout.addWidget(self.grupo_obligatorio)

        # --- Formato de fecha/hora manual (opcional) ---
        self.grupo_formato = QGroupBox()
        form_formato = QFormLayout(self.grupo_formato)

        self.check_formato_manual = QCheckBox()
        form_formato.addRow(self.check_formato_manual)

        self._label_formato_fecha = QLabel()
        self.combo_formato_fecha = QComboBox()
        for etiqueta, _formato in OPCIONES_FORMATO_FECHA:
            self.combo_formato_fecha.addItem(etiqueta)
        self.combo_formato_fecha.setEnabled(False)
        form_formato.addRow(self._label_formato_fecha, self.combo_formato_fecha)

        self._label_formato_hora = QLabel()
        self.combo_formato_hora = QComboBox()
        for etiqueta, _formato in OPCIONES_FORMATO_HORA:
            self.combo_formato_hora.addItem(etiqueta)
        self.combo_formato_hora.setEnabled(False)
        form_formato.addRow(self._label_formato_hora, self.combo_formato_hora)

        self.check_formato_manual.toggled.connect(self.combo_formato_fecha.setEnabled)
        self.check_formato_manual.toggled.connect(self.combo_formato_hora.setEnabled)

        layout.addWidget(self.grupo_formato)

        self._columnas_actuales: List[str] = []

        layout.addStretch(1)

        idioma_bus.idioma_cambiado.connect(self.retranslate)
        self.retranslate()

    def retranslate(self) -> None:
        self.grupo_obligatorio.setTitle(tr("mapeo.grupo_obligatorias"))
        for label, clave in zip(self._labels, self._claves):
            label.setText(tr(clave))

        self.grupo_formato.setTitle(tr("mapeo.grupo_formato"))
        self.check_formato_manual.setText(tr("mapeo.formato_manual"))
        self._label_formato_fecha.setText(tr("mapeo.formato_fecha"))
        self._label_formato_hora.setText(tr("mapeo.formato_hora"))

    def cargar_columnas(self, columnas: List[str]) -> None:
        self._columnas_actuales = list(columnas)
        for combo in self._combos:
            seleccion_previa = combo.currentText()
            combo.clear()
            combo.addItems(columnas)
            indice = combo.findText(seleccion_previa)
            if indice >= 0:
                combo.setCurrentIndex(indice)

    def columnas_modalidad_disponible(self):
        return self.combo_modalidad.currentText() or None

    def _formato_fecha_elegido(self) -> Optional[str]:
        if not self.check_formato_manual.isChecked():
            return None
        return OPCIONES_FORMATO_FECHA[self.combo_formato_fecha.currentIndex()][1]

    def _formato_hora_elegido(self) -> Optional[str]:
        if not self.check_formato_manual.isChecked():
            return None
        return OPCIONES_FORMATO_HORA[self.combo_formato_hora.currentIndex()][1]

    def obtener_mapping(self) -> ColumnMapping:
        return ColumnMapping(
            fecha_inicio=self.combo_fecha_inicio.currentText(),
            hora_inicio=self.combo_hora_inicio.currentText(),
            fecha_fin=self.combo_fecha_fin.currentText(),
            hora_fin=self.combo_hora_fin.currentText(),
            id_evento=None,
            dependencia=self.combo_dependencia.currentText() or None,
            modalidad=self.combo_modalidad.currentText() or None,
            tipo_delito=None,
            zona=self.combo_zona.currentText() or None,
            delito=self.combo_delito.currentText() or None,
            observaciones=None,
            columnas_extra=[],
            formato_fecha_manual=self._formato_fecha_elegido(),
            formato_hora_manual=self._formato_hora_elegido(),
        )

    # --- Guardar / cargar configuración ---

    def a_dict(self) -> dict:
        return {
            "fecha_inicio": self.combo_fecha_inicio.currentText(),
            "hora_inicio": self.combo_hora_inicio.currentText(),
            "fecha_fin": self.combo_fecha_fin.currentText(),
            "hora_fin": self.combo_hora_fin.currentText(),
            "dependencia": self.combo_dependencia.currentText(),
            "modalidad": self.combo_modalidad.currentText(),
            "zona": self.combo_zona.currentText(),
            "delito": self.combo_delito.currentText(),
            "formato_manual_activo": self.check_formato_manual.isChecked(),
            "formato_fecha_indice": self.combo_formato_fecha.currentIndex(),
            "formato_hora_indice": self.combo_formato_hora.currentIndex(),
        }

    def aplicar_dict(self, datos: dict, columnas_disponibles: List[str]) -> List[str]:
        """Aplica columnas guardadas (ya deben estar cargadas con
        cargar_columnas). Devuelve la lista de nombres de columna
        guardados que ya no existen en el archivo actualmente importado."""
        columnas_faltantes: List[str] = []
        mapa_combos = {
            "fecha_inicio": self.combo_fecha_inicio, "hora_inicio": self.combo_hora_inicio,
            "fecha_fin": self.combo_fecha_fin, "hora_fin": self.combo_hora_fin,
            "dependencia": self.combo_dependencia, "modalidad": self.combo_modalidad,
            "zona": self.combo_zona, "delito": self.combo_delito,
        }
        for clave, combo in mapa_combos.items():
            valor = datos.get(clave)
            if not valor:
                continue
            indice = combo.findText(valor)
            if indice >= 0:
                combo.setCurrentIndex(indice)
            else:
                columnas_faltantes.append(valor)

        self.check_formato_manual.setChecked(bool(datos.get("formato_manual_activo", False)))
        indice_fecha = datos.get("formato_fecha_indice")
        if isinstance(indice_fecha, int) and 0 <= indice_fecha < self.combo_formato_fecha.count():
            self.combo_formato_fecha.setCurrentIndex(indice_fecha)
        indice_hora = datos.get("formato_hora_indice")
        if isinstance(indice_hora, int) and 0 <= indice_hora < self.combo_formato_hora.count():
            self.combo_formato_hora.setCurrentIndex(indice_hora)

        return columnas_faltantes
