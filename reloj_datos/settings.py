"""
settings.py

Guarda preferencias del usuario que tienen que sobrevivir a cerrar y
volver a abrir el programa (por ahora, el idioma elegido). Usa
QSettings, el mecanismo estándar de Qt para esto: en Windows lo guarda
en el Registro, en Linux en un archivo .ini dentro de
~/.config/EPSD Bahía Blanca - CePAID/, sin que la app tenga que
preocuparse por dónde ni cómo.
"""
from PySide6.QtCore import QSettings

from .i18n import IDIOMA_POR_DEFECTO, IDIOMAS_DISPONIBLES

_CLAVE_IDIOMA = "idioma"


def _settings() -> QSettings:
    # Usa el nombre de organización/aplicación ya fijados en main.py
    # (QApplication.setOrganizationName/setApplicationName). Si por
    # algún motivo QSettings() se llama antes de crear el QApplication,
    # igual funciona: solo que quedaría en una ubicación genérica.
    return QSettings()


def cargar_idioma_guardado() -> str:
    idioma = _settings().value(_CLAVE_IDIOMA, IDIOMA_POR_DEFECTO)
    if idioma not in IDIOMAS_DISPONIBLES:
        return IDIOMA_POR_DEFECTO
    return idioma


def guardar_idioma(idioma: str) -> None:
    if idioma not in IDIOMAS_DISPONIBLES:
        return
    _settings().setValue(_CLAVE_IDIOMA, idioma)
