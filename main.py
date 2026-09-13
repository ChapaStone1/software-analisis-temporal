"""
main.py

Punto de entrada de la aplicación "Software de Análisis Temporal".
Ejecutar con:  python main.py
"""
import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from reloj_datos.branding import NOMBRE_APP
from reloj_datos.gui.main_window import MainWindow
from reloj_datos.i18n import establecer_idioma
from reloj_datos.resources import ruta_icono_png
from reloj_datos.settings import cargar_idioma_guardado


def main() -> None:
    app = QApplication(sys.argv)
    app.setApplicationName(NOMBRE_APP)
    app.setOrganizationName("EPSD Bahía Blanca - Seccion CePAID")
    app.setWindowIcon(QIcon(ruta_icono_png()))

    # El idioma elegido la última vez queda guardado (ver settings.py)
    # y se aplica antes de crear cualquier ventana o texto.
    establecer_idioma(cargar_idioma_guardado())

    ventana = MainWindow()
    ventana.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
