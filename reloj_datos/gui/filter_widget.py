"""
gui/filter_widget.py

Sección 3 - Filtros.
Filtro temporal (fecha/hora desde - hasta) y hasta 3 filtros por columna
independientes (Filtro 1, Filtro 2, Filtro 3), cada uno sobre la columna
que el usuario elija, con selección de uno o varios valores y un campo
de búsqueda: escribir parte de un valor (por ejemplo "moto") deja
tildados exactamente los valores que lo contienen ("MOTOS(ROBO)",
"MOTOCHORROS", etc.) y destilda el resto, no es solo una lupa visual.
Al abrir una columna, todos sus valores aparecen tildados por defecto.

Cada filtro es un widget independiente con su propio estado, así que
usar varios al mismo tiempo (por ejemplo, modalidad + dependencia +
delito) funciona sin que uno pise al otro.

También expone a_dict()/aplicar_dict() para guardar y volver a cargar
esta configuración desde un archivo (ver gui/config_profile.py).
"""
from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QDateTime
from PySide6.QtWidgets import (
    QComboBox,
    QDateTimeEdit,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..data.filters import EventFilter
from ..i18n import tr
from .idioma_bus import idioma_bus


class FilterSlotWidget(QGroupBox):
    """Un único filtro por columna: elegís la columna y después los valores."""

    def __init__(self, titulo: str, parent=None):
        super().__init__(titulo, parent)
        layout = QVBoxLayout(self)

        self.combo_columna = QComboBox()
        self.combo_columna.addItem(tr("filtros.sin_columna"))
        layout.addWidget(self.combo_columna)

        self.input_busqueda = QLineEdit()
        self.input_busqueda.setPlaceholderText(tr("filtros.buscar_placeholder"))
        self.input_busqueda.textChanged.connect(self._filtrar_valores_visibles)
        layout.addWidget(self.input_busqueda)

        self.lista_valores = QListWidget()
        # Alto mínimo pensado para mostrar cómodamente 6 registros sin
        # scrollear; QListWidget ya trae su propia barra de scroll
        # vertical automática para cuando hay más valores que no entran.
        self.lista_valores.setMinimumHeight(170)
        self.lista_valores.setMaximumHeight(260)
        layout.addWidget(self.lista_valores)

        self._dataframe = None
        self.combo_columna.currentTextChanged.connect(self._refrescar_valores)

    def retranslate_placeholder(self) -> None:
        if self.combo_columna.count() > 0:
            self.combo_columna.setItemText(0, tr("filtros.sin_columna"))
        self.input_busqueda.setPlaceholderText(tr("filtros.buscar_placeholder"))

    def cargar_dataframe(self, df) -> None:
        self._dataframe = df
        columna_previa = self.combo_columna.currentText()
        era_sin_columna = self.combo_columna.currentIndex() == 0

        self.combo_columna.blockSignals(True)
        self.combo_columna.clear()
        self.combo_columna.addItem(tr("filtros.sin_columna"))
        self.combo_columna.addItems(list(df.columns))
        if era_sin_columna:
            self.combo_columna.setCurrentIndex(0)
        else:
            indice = self.combo_columna.findText(columna_previa)
            self.combo_columna.setCurrentIndex(indice if indice >= 0 else 0)
        self.combo_columna.blockSignals(False)

        self._refrescar_valores(self.combo_columna.currentText())

    def _refrescar_valores(self, columna: str) -> None:
        self.input_busqueda.clear()
        self.lista_valores.clear()
        if self._dataframe is None or not columna or columna == tr("filtros.sin_columna"):
            return
        if columna not in self._dataframe.columns:
            return
        valores_unicos = sorted({str(v) for v in self._dataframe[columna].unique() if str(v) != ""})
        for valor in valores_unicos:
            item = QListWidgetItem(valor)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked)  # todo seleccionado por defecto
            self.lista_valores.addItem(item)

    def _filtrar_valores_visibles(self, texto: str) -> None:
        """
        Al escribir un texto de búsqueda, deja tildados SOLO los valores
        que lo contienen (y destilda + oculta el resto): escribir "moto"
        selecciona exactamente "MOTOS(ROBO)", "MOTOCHORROS", etc., no
        solo los muestra. Si se borra la búsqueda, se vuelven a ver
        todos los valores tal como quedaron tildados hasta ese momento.
        """
        texto = texto.strip().lower()
        if not texto:
            for i in range(self.lista_valores.count()):
                self.lista_valores.item(i).setHidden(False)
            return
        for i in range(self.lista_valores.count()):
            item = self.lista_valores.item(i)
            coincide = texto in item.text().lower()
            item.setHidden(not coincide)
            item.setCheckState(Qt.Checked if coincide else Qt.Unchecked)

    def columna_seleccionada(self) -> Optional[str]:
        texto = self.combo_columna.currentText()
        return None if texto in ("", tr("filtros.sin_columna")) else texto

    def valores_seleccionados(self) -> List[str]:
        return [
            self.lista_valores.item(i).text()
            for i in range(self.lista_valores.count())
            if self.lista_valores.item(i).checkState() == Qt.Checked
        ]

    def es_restrictivo(self) -> bool:
        """True si hay una columna elegida y el usuario destildó al menos
        un valor (o sea, el filtro realmente recorta algo)."""
        if not self.columna_seleccionada():
            return False
        return len(self.valores_seleccionados()) < self.lista_valores.count()

    def descripcion(self) -> str:
        columna = self.columna_seleccionada()
        seleccionados = self.valores_seleccionados()
        if len(seleccionados) <= 5:
            valores_texto = ", ".join(seleccionados)
        else:
            valores_texto = tr("filtros.n_valores", n=len(seleccionados), total=self.lista_valores.count())
        return f"{columna}: {valores_texto}"

    # --- Guardar / cargar configuración ---

    def a_dict(self) -> dict:
        return {"columna": self.columna_seleccionada(), "valores": self.valores_seleccionados()}

    def aplicar_dict(self, datos: dict, columnas_disponibles: List[str]) -> bool:
        """Aplica una configuración guardada. Devuelve False (y deja el
        filtro en "sin columna") si la columna guardada no existe en el
        archivo actualmente importado."""
        columna = datos.get("columna")
        if not columna:
            self.combo_columna.setCurrentIndex(0)
            return True
        if columna not in columnas_disponibles:
            self.combo_columna.setCurrentIndex(0)
            return False

        self.combo_columna.setCurrentText(columna)  # dispara _refrescar_valores (todo tildado)
        valores_guardados = set(datos.get("valores", []))
        for i in range(self.lista_valores.count()):
            item = self.lista_valores.item(i)
            item.setCheckState(Qt.Checked if item.text() in valores_guardados else Qt.Unchecked)
        return True


class FilterWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        self.grupo_temporal = QGroupBox(tr("filtros.grupo_temporal"))
        self.grupo_temporal.setCheckable(True)
        self.grupo_temporal.setChecked(False)
        form_temporal = QFormLayout(self.grupo_temporal)
        self._label_desde = QLabel(tr("filtros.desde"))
        self.datetime_desde = QDateTimeEdit(QDateTime.currentDateTime().addMonths(-1))
        self.datetime_desde.setCalendarPopup(True)
        self.datetime_desde.setDisplayFormat("dd/MM/yyyy HH:mm")
        self._label_hasta = QLabel(tr("filtros.hasta"))
        self.datetime_hasta = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_hasta.setCalendarPopup(True)
        self.datetime_hasta.setDisplayFormat("dd/MM/yyyy HH:mm")
        form_temporal.addRow(self._label_desde, self.datetime_desde)
        form_temporal.addRow(self._label_hasta, self.datetime_hasta)
        layout.addWidget(self.grupo_temporal)

        self.filtro1 = FilterSlotWidget(tr("filtros.filtro_n", n=1))
        self.filtro2 = FilterSlotWidget(tr("filtros.filtro_n", n=2))
        self.filtro3 = FilterSlotWidget(tr("filtros.filtro_n", n=3))
        layout.addWidget(self.filtro1)
        layout.addWidget(self.filtro2)
        layout.addWidget(self.filtro3)
        layout.addStretch(1)

        idioma_bus.idioma_cambiado.connect(self.retranslate)

    def retranslate(self) -> None:
        self.grupo_temporal.setTitle(tr("filtros.grupo_temporal"))
        self._label_desde.setText(tr("filtros.desde"))
        self._label_hasta.setText(tr("filtros.hasta"))
        self.filtro1.setTitle(tr("filtros.filtro_n", n=1))
        self.filtro2.setTitle(tr("filtros.filtro_n", n=2))
        self.filtro3.setTitle(tr("filtros.filtro_n", n=3))
        for slot in (self.filtro1, self.filtro2, self.filtro3):
            slot.retranslate_placeholder()

    def cargar_dataframe(self, df) -> None:
        self.filtro1.cargar_dataframe(df)
        self.filtro2.cargar_dataframe(df)
        self.filtro3.cargar_dataframe(df)

    def obtener_filtro(self, atributo_de_columna: Dict[str, str]) -> EventFilter:
        """
        atributo_de_columna: mapea nombre de columna del archivo -> nombre
        de atributo del Event (para poder filtrar por columnas opcionales
        que se guardaron como 'extra').
        """
        fecha_desde = None
        fecha_hasta = None
        if self.grupo_temporal.isChecked():
            fecha_desde = self.datetime_desde.dateTime().toPython()
            fecha_hasta = self.datetime_hasta.dateTime().toPython()

        filtros_columna: Dict[str, List[str]] = {}
        for slot in (self.filtro1, self.filtro2, self.filtro3):
            columna = slot.columna_seleccionada()
            if not columna:
                continue
            atributo = atributo_de_columna.get(columna, columna)
            filtros_columna[atributo] = slot.valores_seleccionados()

        return EventFilter(
            fecha_hora_desde=fecha_desde,
            fecha_hora_hasta=fecha_hasta,
            filtros_columna=filtros_columna,
        )

    def descripcion_filtros(self) -> str:
        """
        Arma un texto legible con los filtros efectivamente aplicados
        (para mostrar en pantalla y en las exportaciones), o cadena vacía
        si no se aplicó ningún filtro.
        """
        partes: List[str] = []
        if self.grupo_temporal.isChecked():
            formato = "%d/%m/%Y %H:%M"
            desde = self.datetime_desde.dateTime().toPython().strftime(formato)
            hasta = self.datetime_hasta.dateTime().toPython().strftime(formato)
            partes.append(tr("filtros.descripcion_fecha", desde=desde, hasta=hasta))

        for slot in (self.filtro1, self.filtro2, self.filtro3):
            if slot.es_restrictivo():
                partes.append(slot.descripcion())

        if not partes:
            return ""
        return tr("filtros.descripcion_prefijo") + " " + " · ".join(partes)

    # --- Guardar / cargar configuración ---

    def a_dict(self) -> dict:
        formato = "%Y-%m-%dT%H:%M:%S"
        return {
            "temporal": {
                "activo": self.grupo_temporal.isChecked(),
                "desde": self.datetime_desde.dateTime().toPython().strftime(formato),
                "hasta": self.datetime_hasta.dateTime().toPython().strftime(formato),
            },
            "filtro_1": self.filtro1.a_dict(),
            "filtro_2": self.filtro2.a_dict(),
            "filtro_3": self.filtro3.a_dict(),
        }

    def aplicar_dict(self, datos: dict, columnas_disponibles: List[str]) -> List[str]:
        """Aplica una configuración de filtros guardada. Devuelve la
        lista de columnas que ya no existen en el archivo actual (si
        alguna)."""
        columnas_faltantes: List[str] = []

        temporal = datos.get("temporal", {})
        self.grupo_temporal.setChecked(bool(temporal.get("activo", False)))
        formato = "%Y-%m-%dT%H:%M:%S"
        if temporal.get("desde"):
            try:
                self.datetime_desde.setDateTime(QDateTime.fromString(temporal["desde"], "yyyy-MM-ddTHH:mm:ss"))
            except Exception:  # noqa: BLE001
                pass
        if temporal.get("hasta"):
            try:
                self.datetime_hasta.setDateTime(QDateTime.fromString(temporal["hasta"], "yyyy-MM-ddTHH:mm:ss"))
            except Exception:  # noqa: BLE001
                pass

        for slot, clave in ((self.filtro1, "filtro_1"), (self.filtro2, "filtro_2"), (self.filtro3, "filtro_3")):
            datos_slot = datos.get(clave, {})
            columna = datos_slot.get("columna")
            if columna and not slot.aplicar_dict(datos_slot, columnas_disponibles):
                columnas_faltantes.append(columna)

        return columnas_faltantes
