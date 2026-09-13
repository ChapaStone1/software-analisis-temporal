"""
gui/sidebar_nav.py

Reemplazo de QTabWidget para tener una navegación ubicada a la
izquierda (como pestañas verticales) pero con el texto siempre
horizontal. Dibujar texto horizontal sobre una QTabBar nativa en
posición West/East depende de trucos de bajo nivel sobre el estilo
visual de Qt, que se comportan de forma distinta (y a veces se rompen
por completo, con texto superpuesto o ilegible) según el tema del
sistema operativo. Este widget evita ese problema de raíz: usa una
QListWidget común (que siempre dibuja texto horizontal) como menú de
navegación a la izquierda, y un QStackedWidget a la derecha con las
páginas reales. Expone el mismo subconjunto de métodos de QTabWidget
que usa el resto de la aplicación (addTab, setCurrentWidget,
setTabEnabled, count, removeTab), para no tener que tocar el resto del
código que ya lo usa.

Cada página se envuelve automáticamente en un QScrollArea: así, si la
ventana se achica (o una pestaña tiene muchos controles, como
Configuración con varios análisis habilitados), aparece una barra de
scroll en vez de que los controles se corten o se superpongan.
"""
from typing import List, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QListWidget, QListWidgetItem, QScrollArea, QStackedWidget, QWidget


class SidebarNav(QWidget):
    currentChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._lista = QListWidget()
        self._lista.setFixedWidth(190)
        self._lista.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self._lista.setStyleSheet(
            """
            QListWidget {
                background-color: #F2F2F2;
                border: none;
                border-right: 1px solid #D0D0D0;
                outline: 0;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 12px 14px;
                color: #222222;
            }
            QListWidget::item:selected {
                background-color: #FFFFFF;
                color: #C00000;
                font-weight: bold;
                border-left: 4px solid #C00000;
            }
            QListWidget::item:disabled {
                color: #AAAAAA;
            }
            """
        )
        layout.addWidget(self._lista)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack, 1)

        # Widget "de verdad" que se agregó en cada índice (antes de
        # envolverlo en su QScrollArea), para poder resolver
        # setCurrentWidget() aunque lo que esté en el stack sea el scroll.
        self._paginas: List[QWidget] = []

        self._lista.currentRowChanged.connect(self._al_cambiar_fila)

    def _al_cambiar_fila(self, fila: int) -> None:
        if fila < 0:
            return
        item = self._lista.item(fila)
        if item is not None and not (item.flags() & Qt.ItemFlag.ItemIsEnabled):
            return
        self._stack.setCurrentIndex(fila)
        self.currentChanged.emit(fila)

    # --- Subconjunto de la API de QTabWidget usado por el resto de la app ---

    def addTab(self, widget: QWidget, texto: str) -> int:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(widget)

        self._stack.addWidget(scroll)
        self._paginas.append(widget)

        item = QListWidgetItem(texto)
        self._lista.addItem(item)
        indice = self._lista.count() - 1
        if indice == 0:
            self._lista.setCurrentRow(0)
        return indice

    def setCurrentWidget(self, widget: QWidget) -> None:
        indice = self._indice_de(widget)
        if indice is not None:
            self._lista.setCurrentRow(indice)

    def _indice_de(self, widget: QWidget) -> Optional[int]:
        for indice, pagina in enumerate(self._paginas):
            if pagina is widget:
                return indice
        return None

    def setTabText(self, indice: int, texto: str) -> None:
        item = self._lista.item(indice)
        if item is not None:
            item.setText(texto)

    def setTabEnabled(self, indice: int, habilitado: bool) -> None:
        item = self._lista.item(indice)
        if item is None:
            return
        if habilitado:
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
        else:
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled & ~Qt.ItemFlag.ItemIsSelectable)

    def count(self) -> int:
        return self._lista.count()

    def removeTab(self, indice: int) -> None:
        scroll = self._stack.widget(indice)
        if scroll is not None:
            self._stack.removeWidget(scroll)
        item = self._lista.takeItem(indice)
        del item
        if 0 <= indice < len(self._paginas):
            del self._paginas[indice]
