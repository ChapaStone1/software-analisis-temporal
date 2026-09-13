"""
export/image_exporter.py

Sección 9 - Exportación (Imagen PNG).
Como el informe tiene varias páginas (reloj, por día, un ranking por
cada análisis habilitado, y el resumen general si está activado), la
exportación a PNG genera un archivo por página, numerado a partir del
nombre elegido (por ejemplo "DataClock_2026..._pagina1_reloj.png").
"""
from pathlib import Path
from typing import List, Tuple

from matplotlib.figure import Figure

from ..processing.chart_generator import ChartGenerator


class ImageExporter:
    @staticmethod
    def exportar(figura: Figure, filepath: str) -> None:
        """Guarda una única figura (uso puntual, por ejemplo desde la GUI)."""
        ChartGenerator.guardar_png(figura, filepath)

    @staticmethod
    def exportar_paginas(figuras: List[Figure], filepath_base: str) -> List[str]:
        """
        Guarda cada figura como un PNG separado, numerado, a partir de
        una ruta base (por ejemplo 'reloj_de_datos.png' se convierte en
        'reloj_de_datos_pagina1_reloj.png', 'reloj_de_datos_pagina2_graficos.png').
        Devuelve la lista de rutas efectivamente escritas.
        """
        base = Path(filepath_base)
        nombre = base.stem
        extension = base.suffix or ".png"
        carpeta = base.parent

        etiquetas = ["reloj", "graficos"]
        rutas: List[str] = []
        for indice, figura in enumerate(figuras, start=1):
            etiqueta = etiquetas[indice - 1] if indice - 1 < len(etiquetas) else str(indice)
            ruta = carpeta / f"{nombre}_pagina{indice}_{etiqueta}{extension}"
            ChartGenerator.guardar_png(figura, str(ruta))
            rutas.append(str(ruta))
        return rutas
