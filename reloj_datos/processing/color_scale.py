"""
processing/color_scale.py

Sección 6 - Colores automáticos.
Escala de color CONTINUA: blanco para las horas de menor frecuencia y
un rojo cada vez más intenso para las de mayor frecuencia (a pedido del
usuario, reemplaza la escala discreta de 3 niveles usada originalmente).

Se usa una instancia de ColorGradient por cada "familia" de valores que
se quiera colorear de forma independiente: la matriz principal, los
totales por día, los totales por hora y los totales por franja horaria
-tal como se ve en la planilla de referencia, donde cada bloque tiene
su propia escala de color relativa a sus propios valores.
"""
from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Tuple

RGB = Tuple[int, int, int]

_BLANCO: RGB = (255, 255, 255)
_ROJO_FUERTE: RGB = (192, 0, 0)

# Colores disponibles para pintar el Reloj de Datos (además del rojo
# por defecto), elegibles desde la pestaña "4. Configuración". La
# clave es lo que se guarda/traduce; el valor es el color "fuerte" del
# gradiente (el otro extremo siempre es blanco).
COLORES_RELOJ: Dict[str, RGB] = {
    "rojo": (192, 0, 0),
    "azul": (0, 82, 165),
    "verde": (0, 128, 55),
    "naranja": (214, 110, 0),
    "morado": (108, 40, 160),
    "gris": (70, 70, 70),
    "turquesa": (0, 130, 130),
}


def color_reloj_rgb(nombre: str) -> RGB:
    return COLORES_RELOJ.get(nombre, _ROJO_FUERTE)


def color_reloj_hex(nombre: str) -> str:
    r, g, b = color_reloj_rgb(nombre)
    return f"#{r:02X}{g:02X}{b:02X}"


@dataclass
class ColorGradient:
    color_bajo: RGB = _BLANCO
    color_alto: RGB = _ROJO_FUERTE
    valor_min: Optional[float] = None
    valor_max: Optional[float] = None

    def calcular_rango(self, valores: Iterable[float]) -> None:
        positivos = [v for v in valores if v and v > 0]
        if not positivos:
            self.valor_min = 0.0
            self.valor_max = 0.0
            return
        self.valor_min = min(positivos)
        self.valor_max = max(positivos)

    def _fraccion(self, valor: float) -> float:
        if not valor or valor <= 0 or not self.valor_max:
            return 0.0
        rango = self.valor_max - self.valor_min
        if rango <= 0:
            return 1.0  # todos los valores positivos son iguales -> color pleno
        frac = (valor - self.valor_min) / rango
        return max(0.0, min(1.0, frac))

    def color_rgb(self, valor: float) -> RGB:
        if not valor or valor <= 0:
            return _BLANCO
        frac = self._fraccion(valor)
        r0, g0, b0 = self.color_bajo
        r1, g1, b1 = self.color_alto
        r = round(r0 + (r1 - r0) * frac)
        g = round(g0 + (g1 - g0) * frac)
        b = round(b0 + (b1 - b0) * frac)
        return (r, g, b)

    def color_hex(self, valor: float) -> str:
        r, g, b = self.color_rgb(valor)
        return f"#{r:02X}{g:02X}{b:02X}"
