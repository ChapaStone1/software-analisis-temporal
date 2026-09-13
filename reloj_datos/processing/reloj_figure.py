"""
processing/reloj_figure.py

Construye la representación visual completa del "Reloj de Datos": la
matriz de 7x24 coloreada con gradiente continuo (blanco -> rojo), más
el bloque de totales por franja horaria integrado debajo (tal como en
la planilla de referencia). Se arma como una única figura de matplotlib
para poder reutilizarla igual en pantalla, PDF y PNG.
"""
from dataclasses import dataclass
from typing import List, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
from matplotlib.figure import Figure

from .color_scale import ColorGradient
from .franjas_horarias import ResultadoFranja
from .reloj_matrix import RelojMatrix, dias_semana
from ..i18n import tr

_ROJO_FUERTE_DEFECTO = (192, 0, 0)

_COLOR_HEADER = "#333333"
_COLOR_TEXTO_HEADER = "white"
_COLOR_BORDE = "#999999"


def _formatear(valor: float) -> str:
    """Una sola cifra decimal (no dos): ocupa menos ancho y en una matriz
    de frecuencias relativas no hace falta más precisión que esa."""
    if not valor:
        return ""
    texto = f"{valor:.1f}".rstrip("0").rstrip(".")
    return texto if texto else "0"


def _celda(ax, x0, x1, y0, y1, texto="", color_fondo="white", color_texto="black",
           bold=False, fontsize=6.5, alineacion="center"):
    rect = mpatches.Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=color_fondo,
                               edgecolor=_COLOR_BORDE, linewidth=0.4)
    ax.add_patch(rect)
    if texto:
        ax.text(
            (x0 + x1) / 2 if alineacion == "center" else x0 + 0.15,
            (y0 + y1) / 2,
            texto,
            ha=alineacion,
            va="center",
            fontsize=fontsize,
            color=color_texto,
            fontweight="bold" if bold else "normal",
        )


@dataclass
class GradientesReloj:
    """Agrupa los gradientes de color usados en cada bloque del reloj."""

    matriz: ColorGradient
    totales_dia: ColorGradient
    totales_hora: ColorGradient
    franjas: ColorGradient

    @classmethod
    def desde_datos(cls, reloj: RelojMatrix, franjas: List[ResultadoFranja],
                     color_alto: Optional[tuple] = None) -> "GradientesReloj":
        color_alto = color_alto or _ROJO_FUERTE_DEFECTO

        g_matriz = ColorGradient(color_alto=color_alto)
        g_matriz.calcular_rango(reloj.matriz.flatten().tolist())

        g_dia = ColorGradient(color_alto=color_alto)
        g_dia.calcular_rango(reloj.total_por_dia().tolist())

        g_hora = ColorGradient(color_alto=color_alto)
        g_hora.calcular_rango(reloj.total_por_hora().tolist())

        g_franja = ColorGradient(color_alto=color_alto)
        g_franja.calcular_rango([f.valor for f in franjas])

        return cls(matriz=g_matriz, totales_dia=g_dia, totales_hora=g_hora, franjas=g_franja)


# Ancho de la columna de etiquetas (días / "FREC" / "%") a la izquierda.
# Las columnas FREC y % son más anchas que una columna de hora normal
# (1 unidad) porque tienen que entrar valores como "23.4" o "100%" en
# negrita sin desbordar ni pisar la columna de al lado.
_ANCHO_ETIQUETA = 4.2
_NUM_HORAS = 24
_ANCHO_COL_FREC = 1.9
_ANCHO_COL_PCT = 1.5
_COL_FREC = _NUM_HORAS
_COL_PCT = _COL_FREC + _ANCHO_COL_FREC
_ANCHO_TOTAL = _COL_PCT + _ANCHO_COL_PCT

_FILA_HEADER = 0
_FILA_DIA_INICIO = 1
_FILA_TOTAL_HORA = _FILA_DIA_INICIO + 7  # 8
_FILA_FRANJA_FREC = _FILA_TOTAL_HORA + 1  # 9
_FILA_FRANJA_PCT = _FILA_FRANJA_FREC + 1  # 10
_FILA_FRANJA_LABEL = _FILA_FRANJA_PCT + 1  # 11
_TOTAL_FILAS = _FILA_FRANJA_LABEL + 1  # 12

# Proporción física (alto/ancho) de cada celda de una hora. Con esto se
# evita que la matriz se vea "estirada": en vez de rellenar todo el alto
# disponible de la página, cada celda mantiene un tamaño prolijo y el
# resto de la hoja queda libre para otro contenido (ver chart_generator).
ASPECTO_CELDA = 1.15


def _tramos_contiguos(horas: List[int]) -> List[List[int]]:
    """
    Divide una lista de horas (0-23) en tramos contiguos EN EL EJE FIJO
    (sin dar la vuelta), para poder dibujar la franja horaria como 1 o 2
    rectángulos separados bajo la matriz de 00 a 23, sin reordenar esa
    matriz. Por ejemplo, [19,20,21,22,23,0,1,...,6] se separa en
    [19..23] y [0..6]: son el mismo grupo horario, pero como el eje va
    de 0 a 23 en línea recta, tienen que dibujarse como 2 rectángulos.
    """
    if not horas:
        return []
    tramos = [[horas[0]]]
    for h in horas[1:]:
        if h == tramos[-1][-1] + 1:
            tramos[-1].append(h)
        else:
            tramos.append([h])
    return tramos


def _formatear_total(valor: float) -> str:
    texto = f"{valor:.1f}".rstrip("0").rstrip(".")
    return texto if texto else "0"


def dibujar_reloj_matriz(
    ax, reloj: RelojMatrix, franjas: List[ResultadoFranja], gradientes: GradientesReloj,
    factor_fuente: float = 1.0,
) -> None:
    """Dibuja la matriz completa (7x24 + FREC/% + totales + franjas) en el eje dado.

    factor_fuente permite achicar (o agrandar) todas las tipografías de
    forma proporcional.

    Las columnas de horas (00 a 23) del reloj en sí siempre se dibujan en
    orden natural, sin importar la hora de inicio elegida para las
    franjas: lo único que puede variar es en qué tramo horario cae cada
    franja del bloque de abajo (que incluso puede partirse en 2 tramos
    si esa franja cruza la medianoche).

    El eje mantiene una proporción fija (ASPECTO_CELDA) en vez de
    estirarse para llenar todo el espacio que le dieron: así las celdas
    siempre se ven prolijas, y si sobra lugar en la hoja, queda en
    blanco (o se aprovecha para otro contenido, según decida quien
    arma la página completa).
    """
    f = factor_fuente
    ax.set_xlim(-_ANCHO_ETIQUETA, _ANCHO_TOTAL)
    ax.set_ylim(0, _TOTAL_FILAS)
    ax.invert_yaxis()
    ax.axis("off")
    ax.set_aspect(ASPECTO_CELDA, adjustable="box", anchor="N")

    # --- Encabezado de horas ---
    for hora in range(_NUM_HORAS):
        _celda(ax, hora, hora + 1, _FILA_HEADER, _FILA_HEADER + 1, f"{hora:02d}",
               color_fondo=_COLOR_HEADER, color_texto=_COLOR_TEXTO_HEADER, bold=True, fontsize=6.5 * f)
    _celda(ax, _COL_FREC, _COL_FREC + _ANCHO_COL_FREC, _FILA_HEADER, _FILA_HEADER + 1, tr("reloj.frec"),
           color_fondo=_COLOR_HEADER, color_texto=_COLOR_TEXTO_HEADER, bold=True, fontsize=6.5 * f)
    _celda(ax, _COL_PCT, _COL_PCT + _ANCHO_COL_PCT, _FILA_HEADER, _FILA_HEADER + 1, tr("reloj.pct"),
           color_fondo=_COLOR_HEADER, color_texto=_COLOR_TEXTO_HEADER, bold=True, fontsize=6.5 * f)
    _celda(ax, -_ANCHO_ETIQUETA, 0, _FILA_HEADER, _FILA_HEADER + 1, "",
           color_fondo=_COLOR_HEADER)

    # --- Filas de días ---
    total_general = reloj.total_general()
    total_por_dia = reloj.total_por_dia()
    for dia in range(7):
        fila = _FILA_DIA_INICIO + dia
        _celda(ax, -_ANCHO_ETIQUETA, 0, fila, fila + 1, dias_semana()[dia], bold=True,
               fontsize=7 * f, alineacion="left")
        for hora in range(_NUM_HORAS):
            valor = reloj.matriz[dia][hora]
            color = gradientes.matriz.color_hex(valor)
            _celda(ax, hora, hora + 1, fila, fila + 1, _formatear(valor), color_fondo=color, fontsize=6.5 * f)

        valor_dia = total_por_dia[dia]
        color_dia = gradientes.totales_dia.color_hex(valor_dia)
        pct_dia = (valor_dia / total_general * 100.0) if total_general else 0.0
        _celda(ax, _COL_FREC, _COL_FREC + _ANCHO_COL_FREC, fila, fila + 1, _formatear_total(valor_dia),
               color_fondo=color_dia, bold=True, fontsize=7 * f)
        _celda(ax, _COL_PCT, _COL_PCT + _ANCHO_COL_PCT, fila, fila + 1, f"{pct_dia:.0f}%", color_fondo=color_dia,
               bold=True, fontsize=7 * f)

    # --- Fila de totales por hora ---
    total_por_hora = reloj.total_por_hora()
    fila_total = _FILA_TOTAL_HORA
    _celda(ax, -_ANCHO_ETIQUETA, 0, fila_total, fila_total + 1, "")
    for hora in range(_NUM_HORAS):
        valor = total_por_hora[hora]
        color = gradientes.totales_hora.color_hex(valor)
        _celda(ax, hora, hora + 1, fila_total, fila_total + 1, _formatear_total(valor), color_fondo=color,
               bold=True, fontsize=6.5 * f)
    _celda(ax, _COL_FREC, _COL_FREC + _ANCHO_COL_FREC, fila_total, fila_total + 1,
           _formatear_total(total_general), bold=True, fontsize=7 * f)
    _celda(ax, _COL_PCT, _COL_PCT + _ANCHO_COL_PCT, fila_total, fila_total + 1, "100%", bold=True, fontsize=7 * f)

    # --- Bloque de franjas horarias (integrado debajo del reloj) ---
    fila_frec = _FILA_FRANJA_FREC
    fila_pct = _FILA_FRANJA_PCT
    fila_label = _FILA_FRANJA_LABEL

    _celda(ax, -_ANCHO_ETIQUETA, 0, fila_frec, fila_frec + 1, tr("reloj.frec"), bold=True, alineacion="left", fontsize=7 * f)
    _celda(ax, -_ANCHO_ETIQUETA, 0, fila_pct, fila_pct + 1, tr("reloj.pct"), bold=True, alineacion="left", fontsize=7 * f)
    _celda(ax, -_ANCHO_ETIQUETA, 0, fila_label, fila_label + 1, "")

    for franja in franjas:
        color = gradientes.franjas.color_hex(franja.valor)
        for tramo in _tramos_contiguos(franja.horas):
            x0 = min(tramo)
            x1 = max(tramo) + 1
            _celda(ax, x0, x1, fila_frec, fila_frec + 1, _formatear_total(franja.valor), color_fondo=color, bold=True, fontsize=8 * f)
            _celda(ax, x0, x1, fila_pct, fila_pct + 1, f"{franja.porcentaje:.0f}%", color_fondo=color, bold=True, fontsize=8 * f)
            _celda(ax, x0, x1, fila_label, fila_label + 1, franja.etiqueta.upper(), color_fondo="#EFEFEF", fontsize=6 * f)

    # Relleno gris de las columnas FREC/% para las 3 filas de franjas (no aplica ahí)
    for fila in (fila_frec, fila_pct, fila_label):
        _celda(ax, _COL_FREC, _ANCHO_TOTAL, fila, fila + 1, "", color_fondo="white")
