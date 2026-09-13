"""
data/dbf_reader.py

Lector minimalista del formato DBF (dBase), usado por muchos sistemas
policiales/GIS más viejos para exportar tablas. No depende de ninguna
librería externa: el formato DBF es binario pero simple, así que se lee
directamente con el módulo estándar `struct`.

Soporta los tipos de campo más comunes: C (texto), N/F (numérico),
D (fecha, formato AAAAMMDD) y L (lógico). Los campos tipo M (memo)
requieren un archivo .dbt aparte que no se lee acá: quedan vacíos.
Los registros marcados como borrados (flag '*') se omiten.
"""
import struct
from pathlib import Path
from typing import List, Tuple


def leer_dbf(ruta) -> Tuple[List[str], List[dict]]:
    """Devuelve (nombres_de_columna, filas) a partir de un archivo .dbf."""
    ruta = Path(ruta)
    with open(ruta, "rb") as f:
        encabezado = f.read(32)
        if len(encabezado) < 32:
            raise ValueError("El archivo DBF está vacío o corrupto.")

        num_registros = struct.unpack("<I", encabezado[4:8])[0]
        longitud_encabezado = struct.unpack("<H", encabezado[8:10])[0]
        longitud_registro = struct.unpack("<H", encabezado[10:12])[0]

        # Bytes 29 indica la página de códigos; probamos utf-8 y si
        # falla usamos latin-1 (cubre la enorme mayoría de DBF en español).
        codificacion = "utf-8"

        campos = []
        f.seek(32)
        while True:
            campo_bytes = f.read(32)
            if len(campo_bytes) < 32 or campo_bytes[0:1] == b"\x0d":
                break
            nombre_bruto = campo_bytes[0:11].split(b"\x00")[0]
            tipo = campo_bytes[11:12].decode("ascii", errors="replace")
            longitud = campo_bytes[16]
            try:
                nombre = nombre_bruto.decode(codificacion).strip()
            except UnicodeDecodeError:
                nombre = nombre_bruto.decode("latin-1").strip()
            campos.append((nombre, tipo, longitud))

        columnas = [nombre for nombre, _, _ in campos]

        f.seek(longitud_encabezado)
        filas = []
        for _ in range(num_registros):
            registro = f.read(longitud_registro)
            if len(registro) < longitud_registro:
                break
            if registro[0:1] == b"*":
                continue  # registro marcado como borrado

            fila = {}
            offset = 1
            for nombre, tipo, longitud in campos:
                crudo = registro[offset:offset + longitud]
                offset += longitud
                try:
                    texto = crudo.decode(codificacion, errors="replace").strip()
                except UnicodeDecodeError:
                    texto = crudo.decode("latin-1", errors="replace").strip()

                if tipo == "D" and len(texto) == 8 and texto.isdigit():
                    texto = f"{texto[0:4]}-{texto[4:6]}-{texto[6:8]}"
                elif tipo == "L":
                    if texto.upper() in ("Y", "T"):
                        texto = "True"
                    elif texto.upper() in ("N", "F"):
                        texto = "False"
                    else:
                        texto = ""

                fila[nombre] = texto
            filas.append(fila)

    return columnas, filas
