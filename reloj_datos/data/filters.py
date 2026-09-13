"""
data/filters.py

Sección 3 - Filtros.
Permite filtrar los eventos por un rango temporal (fecha/hora desde - hasta)
y por cualquier columna del archivo importado, con selección múltiple
de valores.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from ..models.event import Event


@dataclass
class EventFilter:
    """Agrupa el filtro temporal y los filtros por columna."""

    fecha_hora_desde: Optional[datetime] = None
    fecha_hora_hasta: Optional[datetime] = None
    # nombre de atributo -> lista de valores permitidos (OR entre ellos)
    filtros_columna: Dict[str, List[str]] = field(default_factory=dict)

    def aplicar(self, eventos: List[Event]) -> List[Event]:
        resultado = []
        for evento in eventos:
            if not self._pasa_filtro_temporal(evento):
                continue
            if not self._pasa_filtros_columna(evento):
                continue
            resultado.append(evento)
        return resultado

    def _pasa_filtro_temporal(self, evento: Event) -> bool:
        # Se incluye el evento si su rango se superpone con el rango del filtro.
        if self.fecha_hora_desde and evento.fin < self.fecha_hora_desde:
            return False
        if self.fecha_hora_hasta and evento.inicio > self.fecha_hora_hasta:
            return False
        return True

    def _pasa_filtros_columna(self, evento: Event) -> bool:
        for atributo, valores_permitidos in self.filtros_columna.items():
            if not valores_permitidos:
                continue
            valor_evento = evento.valor_atributo(atributo)
            if valor_evento not in valores_permitidos:
                return False
        return True
