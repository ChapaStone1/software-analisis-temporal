"""
resources.py

Resuelve rutas a archivos estáticos (el ícono de la app y los PDF de
documentación) tanto en modo desarrollo como una vez compilado con
PyInstaller, siempre que la carpeta "assets" se empaquete junto al
código (ver build_windows.bat y build_linux.sh).
"""
import os

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def ruta_icono_png() -> str:
    return os.path.join(_BASE_DIR, "assets", "icon.png")


def ruta_icono_ico() -> str:
    return os.path.join(_BASE_DIR, "assets", "icon.ico")


def ruta_documentacion(idioma: str) -> str:
    """
    Ruta al PDF de documentación para el idioma dado. Solo hay
    documentación en español e inglés; para portugués (que no tiene
    PDF propio) se devuelve la versión en inglés.
    """
    nombre = "documentacion_es.pdf" if idioma == "es" else "documentation_en.pdf"
    return os.path.join(_BASE_DIR, "assets", "docs", nombre)
