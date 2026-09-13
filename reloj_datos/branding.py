"""
branding.py

Textos de identidad del software, centralizados para que la firma que
aparece en cada archivo exportado y los créditos de "Acerca de" salgan
siempre idénticos, se use donde se use.
"""

NOMBRE_APP = "Software de Análisis Temporal"

# Versión interna (no forma parte del nombre de la app, pero se muestra
# en "Acerca de" para poder identificar qué build es).
VERSION_APP = "Beta 0.1.2"

# Marca corta que va al pie de cada archivo exportado (PDF, PNG, Excel).
FIRMA_EXPORTACION = "Software de Análisis Temporal. Powered by Juan Jose Chaparro Dev & Claude AI."

_GITHUB_URL = "https://github.com/ChapaStone1"

# Créditos completos, mostrados en el diálogo "Acerca de".
CREDITOS_ACERCA_DE = (
    f"Versión {VERSION_APP}\n"
    "Powered by Juan Jose Chaparro Dev & Claude AI.\n"
    f"Github: {_GITHUB_URL}\n"
    "Sección Ce.P.A.I.D. E.P.S.D. Bahía Blanca.\n"
    "Policía de la Provincia de Buenos Aires, 2026."
)

# Misma información que CREDITOS_ACERCA_DE, pero en HTML: QMessageBox.about()
# detecta automáticamente el texto enriquecido y muestra el link de
# Github como un hipervínculo clickeable en vez de texto plano.
CREDITOS_ACERCA_DE_HTML = (
    f"<p>Versión {VERSION_APP}<br>"
    "Powered by Juan Jose Chaparro Dev &amp; Claude AI.<br>"
    f'Github: <a href="{_GITHUB_URL}">{_GITHUB_URL}</a><br>'
    "Sección Ce.P.A.I.D. E.P.S.D. Bahía Blanca.<br>"
    "Policía de la Provincia de Buenos Aires, 2026.</p>"
)


def nombre_archivo_exportacion(extension: str) -> str:
    """
    Nombre por defecto para los archivos exportados: "DataClock_" +
    fecha y hora actual + extensión (por ejemplo
    "DataClock_20260913_153045.pdf"). Se usa guión bajo en vez de
    separadores como ":" porque esos caracteres no son válidos en
    nombres de archivo en Windows.
    """
    from datetime import datetime

    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    extension = extension.lstrip(".")
    return f"DataClock_{marca}.{extension}"
