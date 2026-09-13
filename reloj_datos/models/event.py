"""
models/event.py

Modelo de dominio que representa un evento importado desde Excel/CSV.
Un evento queda definido por su fecha/hora de inicio y de finalización,
más un conjunto de atributos opcionales usados por los filtros y el
análisis de modalidades (Sección 2, 3 y 4 del requerimiento).
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class Event:
    """Representa un único evento/registro temporal."""

    inicio: datetime
    fin: datetime
    id_evento: Optional[str] = None
    dependencia: Optional[str] = None
    modalidad: Optional[str] = None
    tipo_delito: Optional[str] = None
    zona: Optional[str] = None
    delito: Optional[str] = None
    observaciones: Optional[str] = None
    # Cualquier otra columna que el usuario haya seleccionado como "opcional"
    extra: Dict[str, Any] = field(default_factory=dict)

    @property
    def duracion_horas(self) -> float:
        """Duración total del evento, en horas (puede tener fracción)."""
        return (self.fin - self.inicio).total_seconds() / 3600.0

    def es_puntual(self) -> bool:
        """
        Evento sin duración (hora de inicio == hora de fin), típico de
        registros donde solo se conoce el momento del hecho. Cuenta como
        1 ocurrencia en esa hora, en vez de una duración de 0 (o de 24 hs
        si se confundiera con un cruce de medianoche).
        """
        return self.inicio == self.fin

    def excede_24_horas(self) -> bool:
        """Regla de negocio: eventos de más de 24 hs no se soportan (Sección 4)."""
        return self.duracion_horas > 24.0

    def es_valido(self) -> bool:
        """Un evento es válido si fin >= inicio y no excede las 24 hs."""
        return self.fin >= self.inicio and not self.excede_24_horas()

    def valor_atributo(self, nombre: str) -> Optional[str]:
        """
        Devuelve el valor de un atributo del evento, ya sea uno de los
        campos "fijos" (dependencia, modalidad, etc.) o una columna
        "extra" seleccionada como opcional al mapear columnas.
        """
        if hasattr(self, nombre):
            return getattr(self, nombre)
        return self.extra.get(nombre)
