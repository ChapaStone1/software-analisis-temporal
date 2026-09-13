"""
gui/import_widget.py

Sección 2.1 - Importación de datos.
Pestaña donde el usuario elige el archivo Excel/CSV/DBF y ve una vista
previa de los registros antes de continuar. También tiene los botones
para guardar la configuración actual (columnas + filtros + ajustes) o
cargar una guardada antes; ambos quedan habilitados recién cuando se
importó un archivo (para saber, al cargar una configuración, contra
qué columnas reales validarla).
"""
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from ..data.importer import DataImporter, FormatoNoSoportadoError
from ..i18n import tr
from .idioma_bus import idioma_bus


class ImportWidget(QWidget):
    """Emite archivo_cargado(ruta) cuando la importación fue exitosa."""

    archivo_cargado = Signal(str)
    guardar_configuracion_solicitada = Signal()
    cargar_configuracion_solicitada = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.importer = DataImporter()

        layout = QVBoxLayout(self)

        fila_archivo = QHBoxLayout()
        self.label_ruta = QLabel(tr("importar.ninguno"))
        self.boton_examinar = QPushButton(tr("importar.examinar"))
        self.boton_examinar.clicked.connect(self._elegir_archivo)
        fila_archivo.addWidget(self.boton_examinar)
        fila_archivo.addWidget(self.label_ruta, stretch=1)
        layout.addLayout(fila_archivo)

        self.label_info = QLabel("")
        layout.addWidget(self.label_info)

        fila_config = QHBoxLayout()
        self.boton_guardar_config = QPushButton(tr("importar.guardar_config"))
        self.boton_guardar_config.setEnabled(False)
        self.boton_guardar_config.clicked.connect(self.guardar_configuracion_solicitada.emit)
        self.boton_cargar_config = QPushButton(tr("importar.cargar_config"))
        self.boton_cargar_config.setEnabled(False)
        self.boton_cargar_config.clicked.connect(self.cargar_configuracion_solicitada.emit)
        fila_config.addWidget(self.boton_guardar_config)
        fila_config.addWidget(self.boton_cargar_config)
        fila_config.addStretch(1)
        layout.addLayout(fila_config)

        self.tabla_preview = QTableWidget()
        layout.addWidget(self.tabla_preview, stretch=1)

        idioma_bus.idioma_cambiado.connect(self.retranslate)

    def retranslate(self) -> None:
        self.boton_examinar.setText(tr("importar.examinar"))
        self.boton_guardar_config.setText(tr("importar.guardar_config"))
        self.boton_cargar_config.setText(tr("importar.cargar_config"))
        if self.importer.dataframe is None:
            self.label_ruta.setText(tr("importar.ninguno"))
        else:
            df = self.importer.dataframe
            self.label_info.setText(tr("importar.info", n=len(df), c=len(df.columns)))

    def _elegir_archivo(self) -> None:
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            tr("importar.dialogo_titulo"),
            "",
            "Archivos soportados (*.xlsx *.xls *.csv *.dbf);;Todos los archivos (*.*)",
        )
        if not ruta:
            return
        try:
            df = self.importer.cargar(ruta)
        except FormatoNoSoportadoError as exc:
            QMessageBox.warning(self, tr("importar.formato_no_soportado.titulo"), str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            QMessageBox.critical(self, tr("importar.error_titulo"), tr("importar.error_texto", exc=exc))
            return

        self.label_ruta.setText(ruta)
        self.label_info.setText(tr("importar.info", n=len(df), c=len(df.columns)))
        self._mostrar_preview(df)
        self.boton_guardar_config.setEnabled(True)
        self.boton_cargar_config.setEnabled(True)
        self.archivo_cargado.emit(ruta)

    def _mostrar_preview(self, df) -> None:
        preview = df.head(20)
        self.tabla_preview.setRowCount(len(preview))
        self.tabla_preview.setColumnCount(len(preview.columns))
        self.tabla_preview.setHorizontalHeaderLabels(list(preview.columns))
        for fila_idx, (_, fila) in enumerate(preview.iterrows()):
            for col_idx, valor in enumerate(fila):
                self.tabla_preview.setItem(fila_idx, col_idx, QTableWidgetItem(str(valor)))
        self.tabla_preview.resizeColumnsToContents()

    def columnas_disponibles(self):
        return self.importer.columnas()

    def dataframe(self):
        return self.importer.dataframe
