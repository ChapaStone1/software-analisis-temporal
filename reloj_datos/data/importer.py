"""
data/importer.py

Sección 2.1 - Importación de datos.
Permite cargar archivos .xlsx, .xls y .csv y obtener una vista previa
antes de procesarlos.
"""
from pathlib import Path
from typing import List

import pandas as pd

from .dbf_reader import leer_dbf


class FormatoNoSoportadoError(Exception):
    pass


class DataImporter:
    """Importa archivos Excel/CSV/DBF a un DataFrame de pandas."""

    EXTENSIONES_SOPORTADAS = {".xlsx", ".xls", ".csv", ".dbf"}

    def __init__(self) -> None:
        self.dataframe: pd.DataFrame | None = None
        self.filepath: str | None = None

    def cargar(self, filepath: str) -> pd.DataFrame:
        """Carga el archivo indicado y lo deja disponible como DataFrame."""
        ruta = Path(filepath)
        extension = ruta.suffix.lower()

        if extension not in self.EXTENSIONES_SOPORTADAS:
            raise FormatoNoSoportadoError(
                f"Formato no soportado: '{extension}'. "
                f"Formatos válidos: {', '.join(sorted(self.EXTENSIONES_SOPORTADAS))}"
            )

        if extension == ".csv":
            df = self._leer_csv(ruta)
        elif extension == ".dbf":
            columnas, filas = leer_dbf(ruta)
            df = pd.DataFrame(filas, columns=columnas)
        else:
            df = pd.read_excel(ruta, dtype=str)

        # Normalizamos: todo como texto, sin NaN "flotantes" molestos
        df = df.fillna("")
        self.dataframe = df
        self.filepath = str(ruta)
        return df

    @staticmethod
    def _leer_csv(ruta: Path) -> pd.DataFrame:
        """Intenta detectar el separador y la codificación más comunes."""
        intentos = [
            {"sep": ",", "encoding": "utf-8"},
            {"sep": ";", "encoding": "utf-8"},
            {"sep": ",", "encoding": "latin-1"},
            {"sep": ";", "encoding": "latin-1"},
        ]
        ultimo_error = None
        for opciones in intentos:
            try:
                df = pd.read_csv(ruta, dtype=str, keep_default_na=False, **opciones)
                if df.shape[1] > 1:  # si separó en más de una columna, es correcto
                    return df
            except Exception as exc:  # noqa: BLE001
                ultimo_error = exc
        # Último recurso: dejar que pandas decida
        try:
            return pd.read_csv(ruta, dtype=str, keep_default_na=False)
        except Exception as exc:  # noqa: BLE001
            raise ultimo_error or exc

    def vista_previa(self, filas: int = 20) -> pd.DataFrame:
        if self.dataframe is None:
            raise RuntimeError("No hay ningún archivo cargado todavía.")
        return self.dataframe.head(filas)

    def columnas(self) -> List[str]:
        if self.dataframe is None:
            return []
        return list(self.dataframe.columns)

    def total_filas(self) -> int:
        if self.dataframe is None:
            return 0
        return len(self.dataframe)
