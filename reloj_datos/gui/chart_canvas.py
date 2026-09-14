"""
gui/chart_canvas.py

Envoltorio simple para mostrar figuras de matplotlib dentro de widgets Qt.
"""
from __future__ import annotations

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class ChartCanvas(FigureCanvasQTAgg):
    """
    Envoltorio de un único gráfico. Cuando hay que mostrar un gráfico
    nuevo, el llamador reemplaza esta instancia dentro de su layout
    (más simple y robusto que reciclar la figura interna de matplotlib).
    """

    def __init__(self, figura: Figure | None = None, parent=None):
        figura = figura if figura is not None else Figure(figsize=(6, 3.5))
        super().__init__(figura)
        if parent is not None:
            self.setParent(parent)
