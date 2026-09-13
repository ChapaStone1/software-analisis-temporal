"""
processing/franjas_horarias.py

Sección 7.3 - Totales por Franja Horaria (Configurable).
El usuario puede elegir cómo agrupar las 24 horas del día (4 franjas de
6 horas, 3 de 8, o 2 de 12) y, además, desde qué hora arranca el primer
grupo (por defecto 00:00). Por ejemplo, con hora de inicio 07:00 y 2
franjas, los grupos quedan 07:00-18:59 y 19:00-06:59 (la segunda cruza
la medianoche).

El Reloj de Datos (la matriz de 7x24) NUNCA cambia de disposición por
esto: las columnas siguen siendo 00 a 23 en orden natural. Lo único que
cambia con la hora de inicio es cómo se agrupan esas 24 columnas para
calcular los totales por franja (y, en consecuencia, los gráficos).
"""
from dataclasses import dataclass
from typing import List

import numpy as np

_CANTIDADES_VALIDAS = (2, 3, 4)


@dataclass
class ResultadoFranja:
    etiqueta: str
    valor: float
    porcentaje: float
    horas: List[int]


class FranjaHoraria:
    """Calcula los totales agrupados según la configuración elegida (2, 3 o 4 franjas)."""

    def __init__(self, cantidad_franjas: int = 4, hora_inicio: int = 0) -> None:
        if cantidad_franjas not in _CANTIDADES_VALIDAS:
            raise ValueError("La cantidad de franjas debe ser 2, 3 o 4.")
        self.cantidad_franjas = cantidad_franjas
        self.hora_inicio = hora_inicio % 24
        self.definicion = self._construir_definicion()

    def _construir_definicion(self):
        from ..i18n import tr

        tam = 24 // self.cantidad_franjas
        definicion = []
        for i in range(self.cantidad_franjas):
            horas = [(self.hora_inicio + i * tam + k) % 24 for k in range(tam)]
            etiqueta = f"{horas[0]:02d}:00 {tr('config.a_conector')} {horas[-1]:02d}:59"
            definicion.append((etiqueta, horas))
        return definicion

    def calcular(self, total_por_hora: np.ndarray) -> List[ResultadoFranja]:
        total_general = float(np.sum(total_por_hora))
        resultados = []
        for etiqueta, horas in self.definicion:
            valor = float(sum(total_por_hora[h] for h in horas))
            porcentaje = (valor / total_general * 100.0) if total_general else 0.0
            resultados.append(ResultadoFranja(etiqueta, valor, porcentaje, horas))
        return resultados

    def franja_maxima(self, total_por_hora: np.ndarray) -> ResultadoFranja:
        resultados = self.calcular(total_por_hora)
        return max(resultados, key=lambda r: r.valor)

    @staticmethod
    def etiqueta_configuracion(cantidad_franjas: int, hora_inicio: int) -> str:
        """Texto descriptivo tipo '4 franjas de 6 horas (07-13-19-01)',
        usado para mostrar en la interfaz cómo queda la configuración
        elegida antes de generar el análisis."""
        horas_por_franja = 24 // cantidad_franjas
        inicios = [(hora_inicio + i * horas_por_franja) % 24 for i in range(cantidad_franjas)]
        inicios_texto = "-".join(f"{h:02d}" for h in inicios)
        return f"{cantidad_franjas} franjas de {horas_por_franja} horas ({inicios_texto})"
