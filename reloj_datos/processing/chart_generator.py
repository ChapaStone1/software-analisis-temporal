"""
processing/chart_generator.py

Sección 8 - Gráficos automáticos.
Arma una lista de figuras A4 verticales, una por hoja del informe:

  - Página 1: título + subtítulo + rango de fechas + estadísticas +
    el Reloj de Datos con las franjas horarias integradas + el gráfico
    por franja horaria (aprovecha el espacio libre que deja la matriz).
    Esta página SIEMPRE tiene la misma disposición, generen o no los
    análisis opcionales, para que la matriz nunca se vea "estirada".
  - Página 2: el gráfico por día de la semana, solo.
  - Una página por cada análisis de conteo habilitado (modalidades,
    delitos, dependencia, zona), con su tabla y su gráfico apilados
    (tabla arriba, gráfico abajo) para que ninguno de los dos quede
    apretado, sin importar cuántos ítems tengan.

Todas las páginas llevan número de página ("Página X de Y", con Y ya
sabiendo cuántas páginas hay en total) y la firma del software al pie.

Nota técnica: guardar_png/guardar_pdf adjuntan explícitamente el canvas
de matplotlib correspondiente (Agg o PDF) antes de exportar, en vez de
depender de la detección automática de backend. Esto evita conflictos
cuando la misma figura convive con el backend interactivo de Qt que usa
la interfaz gráfica (causa habitual de errores intermitentes al exportar
PDF/PNG desde una app con GUI).
"""
from typing import List, Optional, Sequence, Tuple

from matplotlib.figure import Figure
import matplotlib.patches as mpatches

from ..branding import FIRMA_EXPORTACION
from ..i18n import tr
from .color_scale import color_reloj_hex, color_reloj_rgb
from .franjas_horarias import ResultadoFranja
from .modalidad_analyzer import ItemRanking
from .reloj_figure import ASPECTO_CELDA, GradientesReloj, _ANCHO_ETIQUETA, _ANCHO_TOTAL, _TOTAL_FILAS, dibujar_reloj_matriz
from .reloj_matrix import RelojMatrix, dias_semana

# (título de la sección, ranking, nombre de columna para la tabla)
SeccionRanking = Tuple[str, List[ItemRanking], str]

# Tamaño A4 vertical, en pulgadas.
_ANCHO_A4 = 8.27
_ALTO_A4 = 11.69

# Cuántos ítems como máximo se dibujan en la tabla/gráfico de cada
# página de ranking. El Excel exportado siempre lleva el ranking
# completo; esto es solo un límite razonable para que la imagen no
# quede microscópica si alguien pide "Todas" con cientos de categorías.
_MAX_ITEMS_RANKING_PAGINA = 25

# Cantidad de ítems que se muestran en el "Top N" de cada análisis
# dentro del resumen ejecutivo (más corto que en su propia página
# dedicada, porque acá conviven varios en una sola hoja).
_TOP_N_RESUMEN = 3

# Márgenes (en fracción de la hoja) usados para dibujar el Reloj de Datos
# en la página 1. Se definen acá (y no solo dentro de figura_pagina_reloj)
# porque _alto_matriz_fraccion() los necesita para calcular cuánto lugar
# ocupa realmente la matriz, y así saber cuánto queda libre debajo para
# el gráfico por franja horaria.
_TOP_RELOJ = 0.895
_LEFT_RELOJ = 0.045
_RIGHT_RELOJ = 0.97
_BOTTOM_RELOJ = 0.045


def _alto_matriz_fraccion() -> float:
    """Fracción de la altura de la hoja que ocupa la matriz del Reloj de
    Datos, dado el ancho disponible y la proporción fija de sus celdas
    (ver ASPECTO_CELDA en reloj_figure.py)."""
    ancho_disponible_in = (_RIGHT_RELOJ - _LEFT_RELOJ) * _ANCHO_A4
    ancho_datos_unidades = _ANCHO_TOTAL + _ANCHO_ETIQUETA
    ancho_columna_in = ancho_disponible_in / ancho_datos_unidades
    alto_matriz_in = ancho_columna_in * ASPECTO_CELDA * _TOTAL_FILAS
    return alto_matriz_in / _ALTO_A4


def _acortar(texto: str, largo: int) -> str:
    return texto if len(texto) <= largo else texto[: largo - 1] + "…"


def _encabezado(fig: Figure, titulo: str, subtitulo: str, descripcion_rango: str,
                 total_eventos: Optional[int], excluidos_24h: int, descripcion_filtros: str = "") -> None:
    y_cursor = 0.978
    fig.text(0.5, y_cursor, titulo, ha="center", fontsize=15, fontweight="bold")
    y_cursor -= 0.021
    if subtitulo:
        fig.text(0.5, y_cursor, subtitulo, ha="center", fontsize=10, color="#333333")
        y_cursor -= 0.017
    if descripcion_rango:
        fig.text(0.5, y_cursor, descripcion_rango, ha="center", fontsize=8.5, color="#444444")
        y_cursor -= 0.015
    if total_eventos is not None:
        texto_stats = tr("reloj.eventos_stats", n=total_eventos, ex=excluidos_24h)
        fig.text(0.5, y_cursor, texto_stats, ha="center", fontsize=8, color="#666666")
        y_cursor -= 0.015
    if descripcion_filtros:
        fig.text(0.5, y_cursor, descripcion_filtros, ha="center", fontsize=7.5, color="#777777")


def _pie_de_pagina(fig: Figure, numero: int, total: int) -> None:
    fig.text(0.5, 0.014, FIRMA_EXPORTACION, ha="center", fontsize=6.5, color="#888888", style="italic")
    fig.text(0.97, 0.014, tr("reloj.pagina_de", n=numero, total=total), ha="right", fontsize=7, color="#888888")


class ChartGenerator:
    @staticmethod
    def figura_pagina_reloj(
        reloj: RelojMatrix,
        franjas: List[ResultadoFranja],
        titulo: str,
        descripcion_rango: str,
        subtitulo: str = "",
        total_eventos: Optional[int] = None,
        excluidos_24h: int = 0,
        descripcion_filtros: str = "",
        numero_pagina: int = 1,
        total_paginas: int = 2,
        color_reloj: str = "rojo",
    ) -> Figure:
        """
        Página 1: el Reloj de Datos con las franjas horarias integradas,
        siempre con el mismo tamaño de celda (nunca se ve "estirado").
        Como esa matriz ocupa poco más de un tercio de la hoja, el resto
        del espacio se aprovecha para el gráfico por franja horaria,
        directamente relacionado con las franjas que ya se ven arriba.

        color_reloj: nombre de uno de los colores de
        processing.color_scale.COLORES_RELOJ (por defecto "rojo").
        """
        gradientes = GradientesReloj.desde_datos(reloj, franjas, color_alto=color_reloj_rgb(color_reloj))

        fig = Figure(figsize=(_ANCHO_A4, _ALTO_A4))

        _encabezado(fig, titulo, subtitulo, descripcion_rango, total_eventos, excluidos_24h, descripcion_filtros)

        ax_reloj = fig.add_axes([_LEFT_RELOJ, _BOTTOM_RELOJ, _RIGHT_RELOJ - _LEFT_RELOJ,
                                  _TOP_RELOJ - _BOTTOM_RELOJ])
        dibujar_reloj_matriz(ax_reloj, reloj, franjas, gradientes, factor_fuente=1.0)

        # --- Gráfico por franja horaria, en el espacio que la matriz deja libre ---
        alto_matriz_frac = _alto_matriz_fraccion()
        borde_inferior_matriz = _TOP_RELOJ - alto_matriz_frac
        alto_grafico_frac = min(3.2 / _ALTO_A4, borde_inferior_matriz - _BOTTOM_RELOJ - 0.03)

        if alto_grafico_frac > 0.08:
            top_grafico = borde_inferior_matriz - 0.05
            bottom_grafico = top_grafico - alto_grafico_frac
            ax_franja = fig.add_axes([0.22, bottom_grafico, 0.56, alto_grafico_frac])
            etiquetas = [f.etiqueta for f in franjas]
            valores = [f.valor for f in franjas]
            posiciones = range(len(etiquetas))
            ax_franja.bar(posiciones, valores, color=color_reloj_hex(color_reloj), width=0.55)
            ax_franja.set_xticks(list(posiciones))
            ax_franja.set_xticklabels(etiquetas, fontsize=7.5, rotation=15)
            ax_franja.set_xlim(-0.75, len(etiquetas) - 0.25)
            ax_franja.set_title(tr("graficos.por_franja"), fontsize=10.5)
            ax_franja.tick_params(axis="y", labelsize=7.5)

        _pie_de_pagina(fig, numero_pagina, total_paginas)
        return fig

    @staticmethod
    def figura_pagina_dia(
        reloj: RelojMatrix,
        titulo: str,
        subtitulo: str = "",
        numero_pagina: int = 2,
        total_paginas: int = 2,
    ) -> Figure:
        """Página dedicada al gráfico por día de la semana, sola: así
        nunca compite por espacio con ningún otro contenido."""
        fig = Figure(figsize=(_ANCHO_A4, _ALTO_A4))

        fig.text(0.5, 0.965, tr("graficos.titulo", titulo=titulo), ha="center", fontsize=14, fontweight="bold")
        if subtitulo:
            fig.text(0.5, 0.945, subtitulo, ha="center", fontsize=10, color="#333333")

        # Gráfico con proporción prolija (más ancho que alto, como
        # cualquier gráfico de barras convencional), centrado en la hoja.
        ax_dia = fig.add_axes([0.10, 0.32, 0.82, 0.34])
        dias = dias_semana()
        posiciones_dia = range(len(dias))
        ax_dia.bar(posiciones_dia, reloj.total_por_dia(), color="#4472C4", width=0.55)
        ax_dia.set_xticks(list(posiciones_dia))
        ax_dia.set_xticklabels(dias, fontsize=11, rotation=20)
        ax_dia.set_xlim(-0.75, len(dias) - 0.25)
        ax_dia.set_title(tr("graficos.por_dia"), fontsize=14, pad=14)
        ax_dia.tick_params(axis="y", labelsize=10)

        _pie_de_pagina(fig, numero_pagina, total_paginas)
        return fig

    @staticmethod
    def figura_pagina_ranking(
        nombre_seccion: str,
        ranking: List[ItemRanking],
        nombre_columna: str,
        titulo: str,
        subtitulo: str = "",
        numero_pagina: int = 1,
        total_paginas: int = 1,
    ) -> Figure:
        """
        Página dedicada a UN análisis de conteo (modalidades, delitos,
        dependencia o zona): la tabla arriba y el gráfico abajo,
        apilados (no lado a lado) y cada uno con toda una franja de la
        hoja para sí, para que ni los nombres largos ni una lista de
        muchos ítems se corten o se superpongan.
        """
        fig = Figure(figsize=(_ANCHO_A4, _ALTO_A4))

        y_cursor = 0.965
        fig.text(0.5, y_cursor, tr("graficos.titulo", titulo=titulo), ha="center", fontsize=14, fontweight="bold")
        y_cursor -= 0.02
        if subtitulo:
            fig.text(0.5, y_cursor, subtitulo, ha="center", fontsize=10, color="#333333")
            y_cursor -= 0.018
        fig.text(0.5, y_cursor, nombre_seccion, ha="center", fontsize=12.5, fontweight="bold", color="#333333")

        items = ranking[:_MAX_ITEMS_RANKING_PAGINA]
        recortado = len(ranking) > len(items)

        # --- Tabla, arriba ---
        ax_tabla = fig.add_axes([0.08, 0.535, 0.86, 0.36])
        ax_tabla.axis("off")
        filas_tabla = [
            [str(it.posicion), _acortar(it.modalidad, 44), str(it.frecuencia), f"{it.porcentaje:.1f}%"]
            for it in items
        ]
        tabla = ax_tabla.table(
            cellText=filas_tabla,
            colLabels=[tr("tabla.pos"), nombre_columna, tr("tabla.frec"), tr("tabla.pct")],
            colWidths=[0.08, 0.72, 0.1, 0.1],
            cellLoc="center",
            bbox=[0, 0, 1, 1],  # confina la tabla exactamente a su propio eje, sin desbordar
        )
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(8)
        for (_fila_celda, col_celda), celda in tabla.get_celld().items():
            if col_celda == 1:
                celda.set_text_props(ha="left")
                celda.PAD = 0.02

        # --- Gráfico, abajo ---
        top_grafico = items[::-1]
        etiquetas = [_acortar(it.modalidad, 38) for it in top_grafico]

        # El margen izquierdo se ajusta al largo real de las etiquetas:
        # con nombres cortos (por ejemplo, códigos de zona) no hace
        # falta tanto lugar, pero con nombres largos (modalidades,
        # delitos, dependencias) hay que dejarles más espacio para que
        # no queden pegados al borde del gráfico.
        largo_max = max((len(e) for e in etiquetas), default=0)
        margen_izquierdo = min(0.42, max(0.14, 0.05 + largo_max * 0.0075))
        ancho_grafico = 0.94 - margen_izquierdo

        ax_chart = fig.add_axes([margen_izquierdo, 0.07, ancho_grafico, 0.40])
        posiciones_rank = range(len(etiquetas))
        ax_chart.barh(list(posiciones_rank), [it.frecuencia for it in top_grafico],
                      color="#70AD47", height=0.65)
        ax_chart.set_yticks(list(posiciones_rank))
        ax_chart.set_yticklabels(etiquetas, fontsize=8)
        ax_chart.set_title(nombre_seccion, fontsize=11)
        ax_chart.tick_params(axis="x", labelsize=8)

        if recortado:
            fig.text(
                0.5, 0.045,
                tr("graficos.ranking_recortado", n=_MAX_ITEMS_RANKING_PAGINA, total=len(ranking)),
                ha="center", fontsize=7, color="#888888", style="italic",
            )

        _pie_de_pagina(fig, numero_pagina, total_paginas)
        return fig

    @staticmethod
    def figura_pagina_resumen_ejecutivo(
        reloj: RelojMatrix,
        franjas: List[ResultadoFranja],
        titulo: str,
        descripcion_rango: str,
        secciones_ranking: Optional[Sequence[SeccionRanking]] = None,
        subtitulo: str = "",
        total_eventos: Optional[int] = None,
        excluidos_24h: int = 0,
        descripcion_filtros: str = "",
        color_reloj: str = "rojo",
        numero_pagina: int = 1,
        total_paginas: int = 1,
    ) -> Figure:
        """
        Página de resumen ejecutivo: los indicadores clave (eventos
        analizados, día/hora/franja pico, y el ítem principal de cada
        análisis de conteo habilitado) en tarjetas, más los gráficos por
        franja horaria y por día de la semana, y un "Top 3" de cada
        análisis habilitado. Pensada como la última hoja del informe,
        para un vistazo rápido sin tener que recorrer todas las páginas.
        """
        secciones_validas = [(n, r, c) for n, r, c in (secciones_ranking or []) if r]
        color_hex = color_reloj_hex(color_reloj)

        fig = Figure(figsize=(_ANCHO_A4, _ALTO_A4))

        _encabezado(
            fig, tr("graficos.titulo_resumen", titulo=titulo), subtitulo, descripcion_rango,
            total_eventos, excluidos_24h, descripcion_filtros,
        )

        # --- Indicadores clave a mostrar en tarjetas ---
        dia_pico = reloj.nombre_dia(reloj.dia_maximo())
        hora_pico = reloj.hora_maxima()
        franja_pico = max(franjas, key=lambda f: f.valor) if franjas else None

        indicadores = [
            (tr("resumen.eventos_analizados"), str(total_eventos if total_eventos is not None else reloj.eventos_procesados), "#333333"),
            (tr("resumen.dia_pico"), dia_pico, color_hex),
            (tr("resumen.hora_pico"), tr("resumen.hora_formato", h=hora_pico), color_hex),
        ]
        if franja_pico is not None:
            indicadores.append((tr("resumen.franja_pico"), franja_pico.etiqueta, color_hex))
        for _nombre_seccion, ranking, nombre_columna in secciones_validas:
            indicadores.append((
                tr("resumen.principal", nombre=nombre_columna.upper()),
                _acortar(ranking[0].modalidad, 18),
                "#4472C4",
            ))

        # --- Presupuesto vertical dinámico ---
        # En vez de reservar un alto fijo para cada bloque (tarjetas,
        # gráficos principales, "Top 3"), se calcula cuánto necesita
        # cada uno según la cantidad real de tarjetas y de análisis
        # habilitados, y si entre todos no entran en el espacio
        # disponible de la hoja, se reducen proporcionalmente. Así
        # nunca se superponen, sin importar si hay 0 o 4 análisis
        # habilitados a la vez.
        filas_tarjetas = -(-len(indicadores) // 3)  # redondeo hacia arriba
        n_secciones = len(secciones_validas)
        columnas_top3 = 2 if n_secciones > 1 else 1
        filas_top3 = -(-n_secciones // columnas_top3) if n_secciones else 0

        top_contenido = 0.895 if not descripcion_filtros else 0.87
        margen_inferior = 0.05  # deja aire sobre la firma/pie de página
        alto_disponible = top_contenido - margen_inferior

        alto_tarjeta_deseado = 0.072
        alto_graficos_deseado = 0.20
        alto_fila_top3_deseado = 0.155
        separadores = 0.02 * (2 if n_secciones else 1)  # entre bloques

        alto_necesario = (
            filas_tarjetas * alto_tarjeta_deseado
            + alto_graficos_deseado
            + filas_top3 * alto_fila_top3_deseado
            + separadores
        )
        escala = min(1.0, alto_disponible / alto_necesario) if alto_necesario > 0 else 1.0

        alto_tarjeta = alto_tarjeta_deseado * escala
        alto_graficos = alto_graficos_deseado * escala
        alto_fila_top3 = alto_fila_top3_deseado * escala
        separador = 0.02 * escala
        fuente_escala = min(1.0, 0.75 + 0.25 * escala)  # las fuentes achican menos que el espacio

        # --- Tarjetas de indicadores clave ---
        alto_tarjetas = alto_tarjeta * filas_tarjetas
        ax_tarjetas = fig.add_axes([0.05, top_contenido - alto_tarjetas, 0.90, alto_tarjetas])
        ax_tarjetas.set_xlim(0, 3)
        ax_tarjetas.set_ylim(0, filas_tarjetas)
        ax_tarjetas.invert_yaxis()
        ax_tarjetas.axis("off")
        for i, (titulo_tarjeta, valor, color) in enumerate(indicadores):
            col, fila = i % 3, i // 3
            rect = mpatches.FancyBboxPatch(
                (col + 0.05, fila + 0.06), 0.9, 0.85,
                boxstyle="round,pad=0.02", facecolor="#F5F5F5", edgecolor="#DDDDDD",
            )
            ax_tarjetas.add_patch(rect)
            ax_tarjetas.text(col + 0.5, fila + 0.28, titulo_tarjeta, ha="center",
                              fontsize=7 * fuente_escala, color="#777777")
            ax_tarjetas.text(col + 0.5, fila + 0.64, valor, ha="center",
                              fontsize=11 * fuente_escala, fontweight="bold", color=color)

        borde_inferior_tarjetas = top_contenido - alto_tarjetas - separador

        # --- Gráficos por franja y por día, lado a lado ---
        # Dentro de la fila que les toca, se reserva a mano una porción
        # arriba (para el título del gráfico) y otra abajo (para las
        # etiquetas rotadas del eje X), porque matplotlib dibuja esas
        # dos cosas AFUERA del rectángulo del eje: si no se les deja
        # lugar explícitamente, invaden la fila de al lado.
        bottom_graficos = borde_inferior_tarjetas - alto_graficos
        frac_titulo_grafico = 0.16
        frac_etiquetas_grafico = 0.32
        alto_eje_grafico = alto_graficos * (1 - frac_titulo_grafico - frac_etiquetas_grafico)
        top_eje_grafico = borde_inferior_tarjetas - alto_graficos * frac_titulo_grafico
        bottom_eje_grafico = top_eje_grafico - alto_eje_grafico

        ax_franja = fig.add_axes([0.08, bottom_eje_grafico, 0.40, alto_eje_grafico])
        etiquetas_f = [f.etiqueta for f in franjas]
        ax_franja.bar(etiquetas_f, [f.valor for f in franjas], color=color_hex, width=0.6)
        ax_franja.set_title(tr("graficos.por_franja"), fontsize=9 * fuente_escala, pad=4)
        ax_franja.tick_params(axis="x", labelsize=6 * fuente_escala, rotation=15)
        ax_franja.tick_params(axis="y", labelsize=7 * fuente_escala)

        ax_dia = fig.add_axes([0.55, bottom_eje_grafico, 0.40, alto_eje_grafico])
        dias = dias_semana()
        ax_dia.bar(dias, reloj.total_por_dia(), color="#4472C4", width=0.6)
        ax_dia.set_title(tr("graficos.por_dia"), fontsize=9 * fuente_escala, pad=4)
        ax_dia.tick_params(axis="x", labelsize=6 * fuente_escala, rotation=30)
        ax_dia.tick_params(axis="y", labelsize=7 * fuente_escala)

        # --- Top 3 de cada análisis habilitado ---
        if secciones_validas:
            ancho_celda = (0.86 / columnas_top3) - 0.04
            espacio_top3_top = bottom_graficos - separador

            # Igual que arriba: se reserva una porción de cada fila para
            # el título (arriba del eje) y se deja un respiro entre
            # filas para que no se toquen los bordes.
            frac_titulo_top3 = 0.24
            frac_respiro_top3 = 0.08
            alto_eje_top3 = alto_fila_top3 * (1 - frac_titulo_top3 - frac_respiro_top3)

            for indice, (nombre_seccion, ranking, _nombre_columna) in enumerate(secciones_validas):
                col, fila = indice % columnas_top3, indice // columnas_top3
                left = 0.08 + col * (ancho_celda + 0.06)
                techo_fila = espacio_top3_top - fila * alto_fila_top3
                top_eje = techo_fila - alto_fila_top3 * frac_titulo_top3
                bottom_eje = top_eje - alto_eje_top3

                top3 = ranking[:_TOP_N_RESUMEN][::-1]
                etiquetas = [_acortar(it.modalidad, 16) for it in top3]

                # Igual que en la página de ranking: el margen izquierdo
                # DENTRO de esta celda se reserva según el largo real de
                # las etiquetas, para que no invadan la columna vecina
                # (acá el espacio es angosto, por eso el límite de 16
                # caracteres arriba es más chico que en la página dedicada).
                largo_max = max((len(e) for e in etiquetas), default=0)
                margen_frac = min(0.60, max(0.30, 0.08 + largo_max * 0.021))
                ax_left = left + ancho_celda * margen_frac
                ax_width = ancho_celda * (1 - margen_frac)

                ax_top = fig.add_axes([ax_left, bottom_eje, ax_width, alto_eje_top3])
                posiciones_top3 = range(len(etiquetas))
                ax_top.barh(list(posiciones_top3), [it.frecuencia for it in top3], color="#70AD47", height=0.55)
                ax_top.set_yticks(list(posiciones_top3))
                ax_top.set_yticklabels(etiquetas)
                ax_top.set_title(
                    tr("resumen.top_n", n=_TOP_N_RESUMEN, nombre=nombre_seccion), fontsize=8 * fuente_escala, pad=3,
                )
                ax_top.tick_params(labelsize=6.5 * fuente_escala)

        _pie_de_pagina(fig, numero_pagina, total_paginas)
        return fig

    @staticmethod
    def figuras_informe_completo(
        reloj: RelojMatrix,
        franjas: List[ResultadoFranja],
        titulo: str,
        descripcion_rango: str,
        secciones_ranking: Optional[Sequence[SeccionRanking]] = None,
        subtitulo: str = "",
        total_eventos: Optional[int] = None,
        excluidos_24h: int = 0,
        descripcion_filtros: str = "",
        color_reloj: str = "rojo",
        incluir_resumen_ejecutivo: bool = False,
    ) -> List[Figure]:
        """
        Devuelve la lista completa de páginas del informe, en orden:
        [reloj, por día, 1 página por cada análisis de conteo habilitado,
        resumen ejecutivo (si está habilitado, siempre al final)].
        La cantidad de páginas es variable (2 como mínimo, sin techo),
        según cuántos análisis opcionales estén activos.
        """
        secciones_validas = [(n, r, c) for n, r, c in (secciones_ranking or []) if r]
        total_paginas = 2 + len(secciones_validas) + (1 if incluir_resumen_ejecutivo else 0)

        paginas = [
            ChartGenerator.figura_pagina_reloj(
                reloj, franjas, titulo, descripcion_rango, subtitulo=subtitulo,
                total_eventos=total_eventos, excluidos_24h=excluidos_24h, descripcion_filtros=descripcion_filtros,
                numero_pagina=1, total_paginas=total_paginas, color_reloj=color_reloj,
            ),
            ChartGenerator.figura_pagina_dia(
                reloj, titulo, subtitulo=subtitulo, numero_pagina=2, total_paginas=total_paginas,
            ),
        ]

        for indice, (nombre_seccion, ranking, nombre_columna) in enumerate(secciones_validas):
            paginas.append(
                ChartGenerator.figura_pagina_ranking(
                    nombre_seccion, ranking, nombre_columna, titulo, subtitulo=subtitulo,
                    numero_pagina=3 + indice, total_paginas=total_paginas,
                )
            )

        if incluir_resumen_ejecutivo:
            paginas.append(
                ChartGenerator.figura_pagina_resumen_ejecutivo(
                    reloj, franjas, titulo, descripcion_rango, secciones_validas, subtitulo=subtitulo,
                    total_eventos=total_eventos, excluidos_24h=excluidos_24h, descripcion_filtros=descripcion_filtros,
                    color_reloj=color_reloj, numero_pagina=total_paginas, total_paginas=total_paginas,
                )
            )

        return paginas

    @staticmethod
    def guardar_png(fig: Figure, filepath: str) -> None:
        from matplotlib.backends.backend_agg import FigureCanvasAgg

        FigureCanvasAgg(fig)
        fig.savefig(filepath, dpi=150, bbox_inches="tight")

    @staticmethod
    def guardar_pdf(fig: Figure, filepath: str) -> None:
        """Guarda una única figura como PDF de 1 página (se mantiene por compatibilidad)."""
        ChartGenerator.guardar_pdf_multiple([fig], filepath)

    @staticmethod
    def guardar_pdf_multiple(figuras: List[Figure], filepath: str) -> None:
        """Guarda una lista de figuras como un PDF de varias páginas (una por figura)."""
        from matplotlib.backends.backend_pdf import PdfPages

        with PdfPages(filepath) as pdf:
            for fig in figuras:
                pdf.savefig(fig, bbox_inches="tight")
