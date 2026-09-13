"""
export/pdf_exporter.py

Sección 9 - Exportación (PDF).
Exporta un PDF de 2 páginas: página 1 con el Reloj de Datos (matriz +
franjas integradas), página 2 con los gráficos y los rankings de
conteo habilitados (modalidades, delitos). Ambas páginas llevan número
de página y la firma del software al pie.
"""
from typing import List, Optional, Sequence

from ..processing.chart_generator import ChartGenerator, SeccionRanking
from ..processing.franjas_horarias import ResultadoFranja
from ..processing.reloj_matrix import RelojMatrix


class PDFExporter:
    def exportar(
        self,
        filepath: str,
        reloj: RelojMatrix,
        titulo: str,
        descripcion_rango: str,
        franjas: List[ResultadoFranja],
        secciones_ranking: Optional[Sequence[SeccionRanking]] = None,
        subtitulo: str = "",
        total_eventos: Optional[int] = None,
        excluidos_24h: int = 0,
        descripcion_filtros: str = "",
        color_reloj: str = "rojo",
        incluir_resumen_ejecutivo: bool = False,
    ) -> None:
        figuras = ChartGenerator.figuras_informe_completo(
            reloj, franjas, titulo, descripcion_rango, secciones_ranking,
            subtitulo=subtitulo, total_eventos=total_eventos, excluidos_24h=excluidos_24h,
            descripcion_filtros=descripcion_filtros, color_reloj=color_reloj,
            incluir_resumen_ejecutivo=incluir_resumen_ejecutivo,
        )
        ChartGenerator.guardar_pdf_multiple(figuras, filepath)
