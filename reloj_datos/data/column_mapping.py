"""
data/column_mapping.py

Sección 2.2 - Selección de columnas.
ColumnMapping guarda qué columna del archivo corresponde a cada dato
requerido (obligatorio) u opcional. EventBuilder usa ese mapeo para
transformar cada fila del DataFrame en un objeto Event.

Nota sobre formatos reales de CSV/Excel policiales:
Es muy común que la columna de "fecha" ya venga como un datetime completo
con la hora en cero (ej. "2026-09-01 00:00:00") y que la hora real esté
en una columna aparte (ej. "10:00:00"). El parseo de abajo separa
explícitamente la parte de FECHA y la parte de HORA de cada columna
antes de combinarlas, en vez de pegar los dos textos crudos, que es lo
que rompía el parseo.
"""
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta
from typing import List, Optional, Tuple

import pandas as pd

from ..models.event import Event

# Formatos de fecha (sin hora) que se intentan antes del parser flexible.
FORMATOS_SOLO_FECHA = [
    "%Y-%m-%d",
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%m/%d/%Y",
]

# Formatos de hora (sin fecha) que se intentan antes del parser flexible.
FORMATOS_SOLO_HORA = [
    "%H:%M:%S",
    "%H:%M",
]

# Opciones de formato de fecha que se pueden elegir a mano desde la
# pestaña "2. Columnas" (etiqueta a mostrar, formato strptime), para
# cuando la detección automática no da con el formato real del archivo.
OPCIONES_FORMATO_FECHA: List[Tuple[str, str]] = [
    ("AAAA-MM-DD (2026-09-01)", "%Y-%m-%d"),
    ("DD/MM/AAAA (01/09/2026)", "%d/%m/%Y"),
    ("MM/DD/AAAA (09/01/2026)", "%m/%d/%Y"),
    ("DD-MM-AAAA (01-09-2026)", "%d-%m-%Y"),
    ("MM-DD-AAAA (09-01-2026)", "%m-%d-%Y"),
    ("AAAA/MM/DD (2026/09/01)", "%Y/%m/%d"),
    ("DD.MM.AAAA (01.09.2026)", "%d.%m.%Y"),
    ("AAAA.MM.DD (2026.09.01)", "%Y.%m.%d"),
    ("DD-MM-AA (01-09-26)", "%d-%m-%y"),
    ("MM/DD/AA (09/01/26)", "%m/%d/%y"),
    ("AAAAMMDD (20260901)", "%Y%m%d"),
]

# Opciones de formato de hora, mismo criterio que las de fecha.
OPCIONES_FORMATO_HORA: List[Tuple[str, str]] = [
    ("HH:MM:SS (14:30:00)", "%H:%M:%S"),
    ("HH:MM (14:30)", "%H:%M"),
    ("HH:MM:SS AM/PM (02:30:00 PM)", "%I:%M:%S %p"),
    ("HH:MM AM/PM (02:30 PM)", "%I:%M %p"),
    ("HH.MM.SS (14.30.00)", "%H.%M.%S"),
    ("HH-MM-SS (14-30-00)", "%H-%M-%S"),
    ("HHMMSS (143000)", "%H%M%S"),
    ("HHMM (1430)", "%H%M"),
]


@dataclass
class ColumnMapping:
    """Mapeo entre columnas del archivo importado y campos del evento."""

    # Obligatorias (Sección 2.2)
    fecha_inicio: str
    hora_inicio: str
    fecha_fin: str
    hora_fin: str

    # Opcionales
    id_evento: Optional[str] = None
    dependencia: Optional[str] = None
    modalidad: Optional[str] = None
    tipo_delito: Optional[str] = None
    zona: Optional[str] = None
    delito: Optional[str] = None
    observaciones: Optional[str] = None
    columnas_extra: List[str] = field(default_factory=list)

    # Si el usuario tilda "Elegir manualmente la configuración de fecha
    # y hora", acá quedan los formatos strptime elegidos (por ejemplo
    # "%d/%m/%Y" y "%H:%M:%S"). Se prueban ANTES que los formatos
    # automáticos, para los casos en los que la detección automática no
    # da con el formato real del archivo.
    formato_fecha_manual: Optional[str] = None
    formato_hora_manual: Optional[str] = None

    def es_completo(self) -> bool:
        """Verifica que todas las columnas obligatorias estén definidas."""
        return all([
            self.fecha_inicio, self.hora_inicio, self.fecha_fin, self.hora_fin,
            self.dependencia, self.modalidad, self.zona, self.delito,
        ])


class EventBuilder:
    """Construye una lista de Event a partir de un DataFrame + ColumnMapping."""

    def __init__(self, mapping: ColumnMapping) -> None:
        self.mapping = mapping
        self.eventos: List[Event] = []
        self.errores_parseo: int = 0

    def _extraer_fecha(self, fecha_val: str) -> Optional[date]:
        """
        Devuelve solo la parte de FECHA de un valor, sin importar si ese
        valor viene como "2026-09-01" o como un datetime completo
        "2026-09-01 00:00:00" (caso típico cuando la hora real está en
        otra columna aparte).
        """
        texto = str(fecha_val).strip()
        if not texto:
            return None

        # Si trae un espacio, probablemente sea "fecha hora" completo:
        # nos quedamos con el primer token como candidato a fecha.
        primer_token = texto.split(" ")[0]

        formatos = FORMATOS_SOLO_FECHA
        if self.mapping.formato_fecha_manual:
            formatos = [self.mapping.formato_fecha_manual] + FORMATOS_SOLO_FECHA

        for formato in formatos:
            try:
                return datetime.strptime(primer_token, formato).date()
            except ValueError:
                continue

        # Fallback flexible (soporta también el texto completo con hora)
        try:
            ts = pd.to_datetime(texto, dayfirst=True, errors="raise")
            return ts.date()
        except Exception:  # noqa: BLE001
            return None

    def _extraer_hora(self, hora_val: str) -> Optional[time]:
        """Devuelve solo la parte de HORA de un valor tipo '10:00:00'."""
        texto = str(hora_val).strip()
        if not texto:
            return None

        # Si la columna de "hora" viene como datetime completo, nos
        # quedamos con el último token (la hora propiamente dicha).
        candidato = texto.split(" ")[-1]

        formatos = FORMATOS_SOLO_HORA
        if self.mapping.formato_hora_manual:
            formatos = [self.mapping.formato_hora_manual] + FORMATOS_SOLO_HORA

        for formato in formatos:
            try:
                return datetime.strptime(candidato, formato).time()
            except ValueError:
                continue

        try:
            ts = pd.to_datetime(texto, errors="raise")
            return ts.time()
        except Exception:  # noqa: BLE001
            return None

    def _combinar_fecha_hora(self, fecha_val: str, hora_val: str) -> Optional[datetime]:
        fecha = self._extraer_fecha(fecha_val)
        hora = self._extraer_hora(hora_val)
        if fecha is None or hora is None:
            return None
        return datetime.combine(fecha, hora)

    def construir(self, df: pd.DataFrame) -> List[Event]:
        """
        Recorre el DataFrame y arma la lista de eventos parseados
        correctamente (incluidos los que superan las 24 hs de duración:
        esos NO se descartan acá, porque hacerlo antes de aplicar los
        filtros del usuario contaminaría el conteo de "excluidos" con
        eventos que ni siquiera formaban parte del recorte analizado.
        Quién decide qué hacer con los eventos de más de 24 hs es el
        código que arma el Reloj de Datos, DESPUÉS de filtrar
        (ver Event.excede_24_horas()).
        """
        m = self.mapping
        self.eventos = []
        self.errores_parseo = 0

        # Muchos CSV reales solo traen UNA columna de fecha (sin fecha de
        # finalización separada). En ese caso, si la hora de fin es
        # estrictamente MENOR a la de inicio, asumimos que el evento cruzó
        # la medianoche y sumamos un día a la fecha de fin (Sección 4).
        # Si son iguales, NO es un cruce de medianoche: es un evento
        # puntual (hora única del hecho) y se conserva tal cual.
        misma_columna_fecha = m.fecha_inicio == m.fecha_fin

        for _, fila in df.iterrows():
            inicio = self._combinar_fecha_hora(fila.get(m.fecha_inicio, ""), fila.get(m.hora_inicio, ""))
            fin = self._combinar_fecha_hora(fila.get(m.fecha_fin, ""), fila.get(m.hora_fin, ""))

            if inicio is None or fin is None:
                self.errores_parseo += 1
                continue

            if misma_columna_fecha and fin < inicio:
                fin = fin + timedelta(days=1)

            if fin < inicio:
                self.errores_parseo += 1
                continue

            evento = Event(
                inicio=inicio,
                fin=fin,
                id_evento=self._valor_opcional(fila, m.id_evento),
                dependencia=self._valor_opcional(fila, m.dependencia),
                modalidad=self._valor_opcional(fila, m.modalidad),
                tipo_delito=self._valor_opcional(fila, m.tipo_delito),
                zona=self._valor_opcional(fila, m.zona),
                delito=self._valor_opcional(fila, m.delito),
                observaciones=self._valor_opcional(fila, m.observaciones),
                extra={},
            )
            self.eventos.append(evento)

        return self.eventos

    @staticmethod
    def _valor_opcional(fila: pd.Series, columna: Optional[str]) -> Optional[str]:
        if not columna or columna not in fila:
            return None
        valor = fila[columna]
        return str(valor) if valor != "" else None
