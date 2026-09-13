"""
processing/reloj_matrix.py

Secciones 5 y 7 - Generación automática del Reloj de Datos y Totales.
Construye la matriz de 7 días x 24 horas con la frecuencia acumulada,
y expone los totales/porcentajes por día, por hora y los máximos que
el sistema debe resaltar automáticamente.
"""
from typing import List, Tuple

import numpy as np

from ..i18n import tr
from ..models.event import Event
from .time_distributor import TimeDistributor

# Lista fija en español, usada internamente (por ejemplo Event.weekday()).
# Para mostrar en pantalla/exportar, usar siempre dias_semana(), que
# respeta el idioma activo.
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def dias_semana() -> List[str]:
    """Nombres de los 7 días de la semana en el idioma activo (0=lunes)."""
    return tr("reloj.dias")


class RelojMatrix:
    """Matriz de análisis temporal (7 días x 24 horas) - el "Reloj de Datos"."""

    def __init__(self) -> None:
        self.matriz: np.ndarray = np.zeros((7, 24), dtype=float)
        self._distributor = TimeDistributor()
        self.eventos_procesados: int = 0

    def construir(self, eventos: List[Event]) -> np.ndarray:
        self.matriz = np.zeros((7, 24), dtype=float)
        self.eventos_procesados = 0

        for evento in eventos:
            for dia, hora, valor in self._distributor.distribuir(evento):
                self.matriz[dia][hora] += valor
            self.eventos_procesados += 1

        return self.matriz

    # --- Totales (Sección 7.1 y 7.2) ---------------------------------

    def total_por_dia(self) -> np.ndarray:
        return self.matriz.sum(axis=1)

    def total_por_hora(self) -> np.ndarray:
        return self.matriz.sum(axis=0)

    def total_general(self) -> float:
        return float(self.matriz.sum())

    def porcentaje_por_dia(self) -> np.ndarray:
        total = self.total_general()
        if total == 0:
            return np.zeros(7)
        return self.total_por_dia() / total * 100.0

    def porcentaje_por_hora(self) -> np.ndarray:
        total = self.total_general()
        if total == 0:
            return np.zeros(24)
        return self.total_por_hora() / total * 100.0

    # --- Resaltados automáticos (Sección 6) --------------------------

    def celda_maxima(self) -> Tuple[int, int]:
        """Devuelve (día, hora) de la celda con mayor frecuencia."""
        indice = int(np.argmax(self.matriz))
        return divmod(indice, 24)

    def dia_maximo(self) -> int:
        return int(np.argmax(self.total_por_dia()))

    def hora_maxima(self) -> int:
        return int(np.argmax(self.total_por_hora()))

    def nombre_dia(self, indice: int) -> str:
        return dias_semana()[indice]
