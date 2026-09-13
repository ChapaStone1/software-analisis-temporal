"""
gui/idioma_bus.py

Un único objeto Qt con una señal que se emite cuando el usuario cambia
el idioma. Cada widget con textos visibles se conecta a esta señal y,
al recibirla, vuelve a fijar todos sus textos llamando a tr() de nuevo
(patrón "retranslate"), sin necesidad de reiniciar la aplicación.
"""
from PySide6.QtCore import QObject, Signal


class _IdiomaBus(QObject):
    idioma_cambiado = Signal(str)


idioma_bus = _IdiomaBus()
