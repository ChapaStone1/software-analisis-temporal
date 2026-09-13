"""
config_profile.py

Guarda y carga en un archivo .json toda la configuración de un
análisis: las columnas mapeadas (paso 2), los filtros (paso 3) y la
configuración del Reloj de Datos (paso 4). Pensado para no tener que
rearmar todo de nuevo cuando llega otro archivo del mismo tipo.

Se usa JSON porque es lo que ya trae Python (sin sumar ninguna
dependencia nueva), representa bien esta mezcla de texto/listas/
booleanos/números, y queda legible si alguna vez hay que abrirlo a
mano para corregir algo.
"""
import json
from typing import List

VERSION_PERFIL = 1


def construir_perfil(mapping_widget, filter_widget, config_widget) -> dict:
    return {
        "version": VERSION_PERFIL,
        "columnas": mapping_widget.a_dict(),
        "filtros": filter_widget.a_dict(),
        "configuracion": config_widget.a_dict(),
    }


def guardar_perfil(perfil: dict, filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(perfil, f, ensure_ascii=False, indent=2)


def cargar_perfil(filepath: str) -> dict:
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def aplicar_perfil(
    perfil: dict, mapping_widget, filter_widget, config_widget, columnas_disponibles: List[str]
) -> List[str]:
    """
    Aplica un perfil cargado a los 3 widgets correspondientes.
    Devuelve la lista (sin duplicados) de nombres de columna que el
    perfil esperaba encontrar y no existen en el archivo actualmente
    importado, para poder avisarle al usuario en vez de fallar en
    silencio.
    """
    columnas_faltantes: List[str] = []

    datos_columnas = perfil.get("columnas", {})
    columnas_faltantes += mapping_widget.aplicar_dict(datos_columnas, columnas_disponibles)

    datos_filtros = perfil.get("filtros", {})
    columnas_faltantes += filter_widget.aplicar_dict(datos_filtros, columnas_disponibles)

    datos_config = perfil.get("configuracion", {})
    config_widget.aplicar_dict(datos_config)

    vistas = set()
    unicas = []
    for columna in columnas_faltantes:
        if columna not in vistas:
            vistas.add(columna)
            unicas.append(columna)
    return unicas
