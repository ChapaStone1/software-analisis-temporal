"""
processing/time_distributor.py

Sección 4 - Procesamiento de los datos.
Distribuye cada evento entre todas las horas (y días) que involucra,
incluyendo eventos que cruzan la medianoche y horarios parciales.

Regla de cálculo (definida por el usuario):
- Cada evento aporta un total de 1 (una ocurrencia) al Reloj de Datos.
- Si el evento es puntual (misma fecha/hora de inicio y fin), ese 1 se
  asigna completo a la hora en la que ocurrió.
  Ejemplo: un hecho a las 12:00 -> suma 1 a la celda de las 12:00.
- Si el evento tiene una duración que abarca más de una hora de reloj,
  el 1 se reparte proporcionalmente entre esas horas según el tiempo
  real que el evento ocupó en cada una.
  Ejemplo: un evento de 11:20 a 12:40 (40 min en la hora 11 + 40 min en
  la hora 12, sobre 80 min totales) reparte 0,5 a las 11hs y 0,5 a las
  12hs.
"""
from dataclasses import dataclass
from datetime import timedelta
from typing import List, Tuple

from ..models.event import Event

# (día_semana 0=Lunes..6=Domingo, hora 0..23, fracción del evento asignada)
Segmento = Tuple[int, int, float]


@dataclass
class TimeDistributor:
    def distribuir(self, evento: Event) -> List[Segmento]:
        # Evento puntual: 1 ocurrencia completa en su única hora.
        if evento.es_puntual():
            return [(evento.inicio.weekday(), evento.inicio.hour, 1.0)]

        duracion_total = evento.duracion_horas
        if duracion_total <= 0:
            return []

        segmentos_crudos: List[Segmento] = []
        cursor = evento.inicio
        fin = evento.fin

        while cursor < fin:
            inicio_hora_reloj = cursor.replace(minute=0, second=0, microsecond=0)
            siguiente_hora_reloj = inicio_hora_reloj + timedelta(hours=1)
            limite_segmento = min(siguiente_hora_reloj, fin)

            duracion_segmento_horas = (limite_segmento - cursor).total_seconds() / 3600.0
            dia_semana = cursor.weekday()
            hora = cursor.hour

            if duracion_segmento_horas > 0:
                segmentos_crudos.append((dia_semana, hora, duracion_segmento_horas))

            cursor = limite_segmento

        # Normalizamos: la suma de todos los segmentos de este evento da 1.
        return [
            (dia, hora, duracion_parcial / duracion_total)
            for dia, hora, duracion_parcial in segmentos_crudos
        ]
