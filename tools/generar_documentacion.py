#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tools/generar_documentacion.py

Genera los dos PDF de documentación del software (español e inglés) a
partir del contenido definido en este mismo archivo, usando reportlab.
Se corre una sola vez (o cada vez que se edita el contenido) para
regenerar los PDF que se guardan en reloj_datos/assets/docs/ y que la
propia app abre desde el menú "Docs".

Uso:
    python3 tools/generar_documentacion.py
"""
import os
import sys

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from reloj_datos.branding import VERSION_APP  # noqa: E402

ROJO = colors.HexColor("#C00000")
GRIS_OSCURO = colors.HexColor("#333333")
GRIS = colors.HexColor("#666666")
GRIS_CLARO = colors.HexColor("#F5F5F5")

CARPETA_SALIDA = os.path.join(os.path.dirname(__file__), "..", "reloj_datos", "assets", "docs")


def _estilos():
    base = getSampleStyleSheet()
    estilos = {
        "Titulo": ParagraphStyle(
            "Titulo", parent=base["Title"], fontSize=26, textColor=ROJO, spaceAfter=6, alignment=1,
        ),
        "Subtitulo": ParagraphStyle(
            "Subtitulo", parent=base["Normal"], fontSize=13, textColor=GRIS, alignment=1, spaceAfter=4,
        ),
        "Version": ParagraphStyle(
            "Version", parent=base["Normal"], fontSize=10, textColor=GRIS, alignment=1, spaceAfter=40,
        ),
        "H1": ParagraphStyle(
            "H1", parent=base["Heading1"], fontSize=17, textColor=ROJO, spaceBefore=22, spaceAfter=10,
            borderColor=ROJO, borderWidth=0, borderPadding=0,
        ),
        "H2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontSize=13, textColor=GRIS_OSCURO, spaceBefore=14, spaceAfter=6,
        ),
        "Cuerpo": ParagraphStyle(
            "Cuerpo", parent=base["BodyText"], fontSize=10, leading=15, spaceAfter=8, alignment=4,
        ),
        "Codigo": ParagraphStyle(
            "Codigo", parent=base["Code"], fontSize=9.5, leading=13, backColor=GRIS_CLARO,
            borderPadding=6, spaceAfter=10, textColor=GRIS_OSCURO,
        ),
        "Nota": ParagraphStyle(
            "Nota", parent=base["BodyText"], fontSize=9.5, leading=13, textColor=GRIS,
            leftIndent=10, spaceAfter=10, borderColor=colors.HexColor("#DDDDDD"), borderWidth=0,
        ),
        "Item": ParagraphStyle(
            "Item", parent=base["BodyText"], fontSize=10, leading=14, spaceAfter=4,
        ),
    }
    return estilos


def _pie_de_pagina(canvas_obj, doc, idioma: str):
    canvas_obj.saveState()
    canvas_obj.setFont("Helvetica", 8)
    canvas_obj.setFillColor(GRIS)
    texto_izq = {
        "es": "Software de Análisis Temporal — Documentación",
        "en": "Temporal Analysis Software — Documentation",
    }[idioma]
    canvas_obj.drawString(2 * cm, 1.2 * cm, texto_izq)
    canvas_obj.drawRightString(A4[0] - 2 * cm, 1.2 * cm, f"{doc.page}")
    canvas_obj.restoreState()


def _parrafo(texto, estilo):
    return Paragraph(texto, estilo)


def _lista(items, estilo):
    return ListFlowable(
        [ListItem(Paragraph(t, estilo), bulletColor=ROJO) for t in items],
        bulletType="bullet", start="•", leftIndent=16, spaceBefore=2, spaceAfter=10,
    )


def _tabla_horas(idioma):
    if idioma == "es":
        encabezado = ["Evento", "Duración", "Hora 11", "Hora 12", "Total"]
        filas = [
            ["11:20 a 12:40", "1h 20min", "0,50", "0,50", "1,00"],
            ["11:00 a 11:00 (puntual)", "0 min", "1,00", "0,00", "1,00"],
            ["10:00 a 13:00", "3h", "0,33 (en h.10)*", "0,33", "1,00 (repartido en 3 horas)"],
        ]
    else:
        encabezado = ["Event", "Duration", "Hour 11", "Hour 12", "Total"]
        filas = [
            ["11:20 to 12:40", "1h 20min", "0.50", "0.50", "1.00"],
            ["11:00 to 11:00 (instant)", "0 min", "1.00", "0.00", "1.00"],
            ["10:00 to 13:00", "3h", "0.33 (at h.10)*", "0.33", "1.00 (split across 3 hours)"],
        ]
    datos = [encabezado] + filas
    tabla = Table(datos, colWidths=[4.2 * cm, 2.6 * cm, 2.6 * cm, 2.6 * cm, 3.5 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), GRIS_OSCURO),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CCCCCC")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return tabla


# ======================================================================
# Contenido en español
# ======================================================================

def _contenido_es(estilos):
    e = estilos
    c = []

    c.append(Spacer(1, 4 * cm))
    c.append(_parrafo("Software de Análisis Temporal", e["Titulo"]))
    c.append(_parrafo("Documentación técnica y de uso", e["Subtitulo"]))
    c.append(_parrafo(f"Versión {VERSION_APP}", e["Version"]))
    c.append(_parrafo(
        "E.P.S.D. Bahía Blanca — Sección Ce.P.A.I.D.<br/>"
        "Policía de la Provincia de Buenos Aires",
        ParagraphStyle("centrado", parent=e["Subtitulo"], fontSize=10),
    ))
    c.append(PageBreak())

    # --- 1. Introducción ---
    c.append(_parrafo("1. Introducción", e["H1"]))
    c.append(_parrafo(
        "El Software de Análisis Temporal es una herramienta de escritorio para analizar la "
        "distribución horaria de eventos (hechos delictivos, intervenciones, incidentes, etc.) a "
        "partir de una planilla de datos. Su salida principal es el <b>Reloj de Datos</b>: una "
        "matriz de 7 días × 24 horas que muestra, con un gradiente de color, en qué días y horas se "
        "concentran los eventos analizados.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "Además del Reloj de Datos, el software genera gráficos por franja horaria y por día de la "
        "semana, hasta cuatro análisis de conteo (modalidad, delito, dependencia y zona) y una "
        "página de resumen general, exportables a Excel, PDF y PNG.", e["Cuerpo"],
    ))

    # --- 2. Flujo de trabajo ---
    c.append(_parrafo("2. Flujo de trabajo", e["H1"]))
    c.append(_parrafo("El programa se organiza en 5 pasos, en la barra lateral izquierda:", e["Cuerpo"]))
    c.append(_lista([
        "<b>1. Importar</b>: elegir el archivo de datos (.xlsx, .xls, .csv o .dbf).",
        "<b>2. Columnas</b>: indicar qué columna del archivo corresponde a cada dato que necesita el "
        "programa (fecha/hora de inicio y fin, dependencia, modalidad, zona, DelitoCOP).",
        "<b>3. Filtros</b>: acotar opcionalmente el análisis por fecha/hora y hasta por 3 columnas más, "
        "cada una con sus propios valores a incluir.",
        "<b>4. Configuración</b>: título, color, franjas horarias, y qué análisis opcionales generar.",
        "<b>5. Resultados</b>: se habilita al generar el análisis; muestra todas las páginas del "
        "informe y permite exportarlo.",
    ], e["Item"]))
    c.append(_parrafo(
        "El botón <b>Generar Análisis</b> (abajo a la derecha de \"4. Configuración\", o en el menú "
        "superior) procesa los datos con las columnas, filtros y configuración elegidos, y arma "
        "todas las páginas del informe.", e["Cuerpo"],
    ))

    # --- 3. Formatos de archivo ---
    c.append(_parrafo("3. Formatos de archivo soportados", e["H1"]))
    c.append(_lista([
        "<b>Excel</b> (.xlsx, .xls): se lee la primera hoja del archivo.",
        "<b>CSV</b> (.csv): separador detectado automáticamente (coma o punto y coma).",
        "<b>DBF</b> (.dbf): formato dBase, usado por algunos sistemas policiales/GIS más viejos. Se "
        "lee con un decodificador propio, sin depender de ninguna librería externa. Los campos tipo "
        "\"memo\" (que requieren un archivo .dbt aparte) quedan vacíos.",
    ], e["Item"]))

    # --- 4. Columnas ---
    c.append(_parrafo("4. Columnas obligatorias y formato de fecha/hora", e["H1"]))
    c.append(_parrafo(
        "En el paso \"2. Columnas\" hay que indicar, sin excepción, estas 8 columnas: fecha de "
        "inicio, hora de inicio, fecha de fin, hora de fin, dependencia, modalidad, zona y DelitoCOP.",
        e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Detección automática de fecha/hora:</b> por defecto, el programa prueba varios formatos "
        "comunes (AAAA-MM-DD, DD/MM/AAAA, HH:MM:SS, etc.) hasta encontrar uno que funcione con los "
        "datos del archivo.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Formato manual:</b> si la detección automática falla (por ejemplo, con fechas ambiguas "
        "como \"03/04/2026\", que podría ser 3 de abril o 4 de marzo), se puede tildar \"Elegir "
        "manualmente la configuración de fecha y hora\" y elegir el formato exacto de una lista con "
        "varias opciones (incluye formatos con AM/PM). Ese formato se prueba antes que los "
        "automáticos.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Cruce de medianoche sin columna de fecha de fin real:</b> si la hora de fin es menor que "
        "la de inicio Y las columnas de fecha de inicio y de fin son la misma columna del archivo, el "
        "programa asume que el evento terminó al día siguiente y suma un día a la fecha de fin "
        "automáticamente. Si la hora de fin es igual a la de inicio, se toma como un evento puntual "
        "(no como que duró 24 horas).", e["Nota"],
    ))

    # --- 5. Filtros ---
    c.append(_parrafo("5. Filtros", e["H1"]))
    c.append(_parrafo(
        "<b>Filtro temporal:</b> permite acotar el análisis a un rango de fecha/hora concreto.",
        e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Filtros por columna (hasta 3, independientes entre sí):</b> cada uno elige una columna del "
        "archivo, y muestra la lista de valores únicos que tiene esa columna, todos tildados por "
        "defecto. Destildar algunos valores excluye del análisis a los eventos que los tengan.",
        e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Búsqueda por texto:</b> cada filtro tiene un campo de búsqueda. Escribir un texto ahí "
        "(por ejemplo \"moto\") tilda automáticamente solo los valores que lo contienen (\"MOTOS"
        "(ROBO)\", \"MOTOCHORROS\", etc.) y destilda el resto: no es solo una lupa visual, cambia la "
        "selección real. Al borrar la búsqueda se vuelven a ver todos los valores, con el tilde que "
        "hayan quedado.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "Combinar varios filtros a la vez (por ejemplo, fecha + dependencia + modalidad) funciona "
        "como un \"Y\" lógico: solo quedan los eventos que cumplen todas las condiciones a la vez.",
        e["Nota"],
    ))

    # --- 6. Cómo se calculan las horas ---
    c.append(_parrafo("6. Cómo se calculan las horas — el corazón del Reloj de Datos", e["H1"]))
    c.append(_parrafo(
        "Esta es la parte más importante para interpretar correctamente los números del Reloj de "
        "Datos. <b>Cada evento aporta un total de exactamente 1</b> a la matriz, sin importar cuánto "
        "dure. Ese \"1\" se reparte en partes proporcionales entre todas las horas que el evento "
        "ocupa.", e["Cuerpo"],
    ))
    c.append(_lista([
        "<b>Evento puntual</b> (la hora de inicio es igual a la de fin, por ejemplo un hecho "
        "registrado \"a las 14:00\"): suma 1 completo en esa única hora.",
        "<b>Evento con duración, dentro de una misma franja horaria</b> (por ejemplo, de 11:20 a "
        "12:40): el 1 se reparte proporcionalmente al tiempo pasado en cada hora del reloj que "
        "toca. En este ejemplo, pasa 40 minutos en la hora 11 y 40 minutos en la hora 12 (de una "
        "duración total de 80 minutos), entonces suma 0,5 en la hora 11 y 0,5 en la hora 12.",
        "<b>Evento que abarca varias horas completas</b> (por ejemplo, de 10:00 a 13:00, 3 horas): "
        "el 1 se reparte en partes iguales entre esas 3 horas (0,33 en cada una).",
    ], e["Item"]))
    c.append(_tabla_horas("es"))
    c.append(_parrafo(
        "*Los valores están redondeados a 2 decimales para la tabla; internamente se calculan con "
        "más precisión.", e["Nota"],
    ))
    c.append(_parrafo(
        "Gracias a este reparto proporcional, la <b>suma de todas las celdas de la matriz siempre es "
        "igual a la cantidad de eventos válidos analizados</b> (ni más ni menos), sin importar cuánto "
        "haya durado cada uno. Esto es lo que hace que el total general (celda \"FREC\" abajo a la "
        "derecha) sirva como control de cuadre.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Cruce de medianoche:</b> si un evento cruza la medianoche (por ejemplo, de 23:00 a "
        "01:00), cada hora se contabiliza en el día que realmente le corresponde: la hora 23 en el "
        "día en que empezó, y la hora 0 y 1 en el día siguiente.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Eventos de más de 24 horas:</b> se consideran un error de carga de datos (por ejemplo, "
        "una fecha de fin mal tipeada) y NO entran en la matriz. Se cuentan aparte, como "
        "\"excluidos\", y ese conteo se calcula sobre los eventos que ya pasaron los filtros elegidos "
        "(no sobre el archivo completo): si filtrás por una dependencia y de esos eventos filtrados "
        "5 superan las 24 horas, el programa va a mostrar exactamente esos 5 como excluidos, no los "
        "que haya en todo el archivo.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Errores de formato de fecha/hora:</b> las filas que no se pueden interpretar como fecha/"
        "hora válida (por ejemplo, una celda vacía o con texto no reconocible) tampoco entran al "
        "análisis, y se cuentan aparte como \"con error de formato\".", e["Cuerpo"],
    ))

    # --- 7. Franjas horarias ---
    c.append(_parrafo("7. Franjas horarias configurables", e["H1"]))
    c.append(_parrafo(
        "Además de la matriz hora por hora, el Reloj de Datos agrupa las 24 horas en franjas más "
        "amplias (2, 3 o 4, a elección) para leer el patrón general de un vistazo.", e["Cuerpo"],
    ))
    c.append(_lista([
        "<b>Cantidad de franjas:</b> 4 franjas de 6 horas, 3 de 8, o 2 de 12.",
        "<b>Hora de inicio de la primera franja:</b> configurable (por defecto 00:00). Por ejemplo, "
        "con hora de inicio 07:00 y 4 franjas, quedan: 07-13, 13-19, 19-01 y 01-07.",
        "La <b>matriz de 00 a 23 nunca cambia de disposición</b> por esto: lo único que cambia es "
        "cómo se agrupan esas 24 columnas para el bloque de totales por franja, dibujado debajo. Si "
        "una franja cruza la medianoche, se dibuja partida en 2 tramos (por ejemplo 19-23 y 00-01), "
        "pero sigue siendo una sola franja a efectos del cálculo.",
    ], e["Item"]))

    # --- 8. Análisis de conteo ---
    c.append(_parrafo("8. Análisis de conteo (Modalidad, Delito, Dependencia, Zona)", e["H1"]))
    c.append(_parrafo(
        "Son 4 análisis opcionales e independientes entre sí (se puede activar cualquier combinación "
        "de ellos, incluso los 4 a la vez). Cada uno arma un <i>ranking</i>: cuenta cuántas veces "
        "aparece cada valor distinto de la columna elegida (entre los eventos que pasaron los "
        "filtros), y lo ordena de mayor a menor frecuencia.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Separador (solo en Modalidades):</b> a veces una misma celda de \"modalidad\" tiene más "
        "de un valor junto, separados por una coma (por ejemplo \"MOTOCHORRO, ARMA DE FUEGO\"). Con "
        "el separador configurado (\",\" por defecto), el programa cuenta cada valor por separado: "
        "ese ejemplo suma 1 a \"MOTOCHORRO\" y 1 a \"ARMA DE FUEGO\", no 1 a la combinación completa. "
        "Los demás análisis (Delito, Dependencia, Zona) no usan separador: cada celda se cuenta "
        "como un único valor completo.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Porcentaje:</b> la frecuencia de cada valor dividida por el total de apariciones "
        "contadas en ese análisis (no por la cantidad de eventos, si se usó separador y algunas "
        "celdas tenían más de un valor).", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Cantidad a graficar:</b> cuántos valores del ranking mostrar en el gráfico y la tabla de "
        "esa página (0 = todos). El Excel exportado siempre incluye el ranking completo, aunque en "
        "el PDF/pantalla se haya limitado a menos ítems por espacio.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "Cada análisis habilitado agrega una página propia al informe (tabla arriba, gráfico de "
        "barras abajo), para no competir por espacio con los demás.", e["Nota"],
    ))

    # --- 9. Resumen general ---
    c.append(_parrafo("9. Resumen General", e["H1"]))
    c.append(_parrafo(
        "Página opcional (casilla en \"4. Configuración\") pensada para un vistazo rápido sin "
        "recorrer todo el informe. Muestra, en tarjetas: eventos analizados, día pico, hora pico, "
        "franja pico, y el valor principal (el primero del ranking) de cada análisis de conteo "
        "habilitado. Debajo, los gráficos por franja horaria y por día de la semana, y un \"Top 3\" "
        "de cada análisis habilitado.", e["Cuerpo"],
    ))
    c.append(_lista([
        "<b>Día/hora pico:</b> el día de la semana y la hora del día con mayor frecuencia acumulada "
        "en la matriz del Reloj de Datos.",
        "<b>Franja pico:</b> la franja horaria (de las configuradas en el paso 4) con mayor "
        "frecuencia.",
    ], e["Item"]))

    # --- 10. Personalización ---
    c.append(_parrafo("10. Personalización visual", e["H1"]))
    c.append(_lista([
        "<b>Título y subtítulo</b> del informe, en \"4. Configuración\".",
        "<b>Color del Reloj de Datos:</b> rojo (por defecto), azul, verde, naranja, morado, gris o "
        "turquesa. Afecta la matriz, el bloque de franjas y el gráfico por franja horaria.",
        "<b>Idioma:</b> español, inglés o portugués, elegible desde el menú \"Idioma\", sin reiniciar "
        "el programa. El idioma elegido queda guardado y se restaura la próxima vez que se abre el "
        "programa.",
    ], e["Item"]))

    # --- 11. Exportación ---
    c.append(_parrafo("11. Exportación", e["H1"]))
    c.append(_lista([
        "<b>PDF:</b> un archivo con todas las páginas del informe (Reloj de Datos, por día, una por "
        "cada análisis habilitado, y el Resumen General si está activado). La cantidad de páginas es "
        "variable según cuántos análisis se hayan habilitado.",
        "<b>Excel:</b> una hoja \"1. Reloj de Datos\" con la matriz completa, una hoja por cada "
        "análisis de conteo habilitado (con el ranking completo, sin límite de ítems), y una hoja "
        "\"Resumen General\" si está activado.",
        "<b>PNG:</b> un archivo de imagen por cada página del informe.",
    ], e["Item"]))
    c.append(_parrafo(
        "Los archivos se sugieren con el nombre \"DataClock_AAAAMMDD_HHMMSS\" (fecha y hora del "
        "momento de exportar). Al terminar de exportar, el programa pregunta si se quiere abrir el "
        "archivo generado.", e["Cuerpo"],
    ))

    # --- 12. Guardar y cargar configuración ---
    c.append(_parrafo("12. Guardar y cargar configuración", e["H1"]))
    c.append(_parrafo(
        "Desde el menú Archivo o desde la pestaña \"1. Importar\" (botones habilitados una vez "
        "importado un archivo), se puede guardar en un archivo .json toda la configuración actual: "
        "las columnas mapeadas, los filtros (incluidos los valores tildados de cada uno) y los "
        "ajustes del paso 4. Sirve para no tener que rearmar todo cuando llega un archivo nuevo del "
        "mismo tipo (mismas columnas).", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "Al cargar una configuración guardada, el programa valida cada columna contra el archivo "
        "actualmente importado: si alguna ya no existe (por ejemplo, si el archivo nuevo tiene un "
        "nombre de columna distinto), avisa cuáles con un mensaje, en vez de fallar en silencio o "
        "aplicar algo incorrecto.", e["Cuerpo"],
    ))

    # --- 13. Preguntas frecuentes ---
    c.append(_parrafo("13. Preguntas frecuentes", e["H1"]))
    c.append(_parrafo(
        "<b>¿Por qué el total de la matriz no coincide con la cantidad de filas de mi archivo "
        "original?</b>", e["H2"],
    ))
    c.append(_parrafo(
        "Porque se aplicaron filtros, o porque algunas filas se excluyeron por superar las 24 horas "
        "de duración o por tener un error de formato de fecha/hora. El texto \"Eventos analizados: N "
        "· Excluidos por superar 24 hs: M\" que aparece debajo del título del Reloj de Datos muestra "
        "ambos números; N + M debería coincidir con la cantidad de filas que pasaron los filtros "
        "elegidos.", e["Cuerpo"],
    ))
    c.append(_parrafo("<b>¿Por qué un análisis me pide una columna que ya elegí?</b>", e["H2"]))
    c.append(_parrafo(
        "Los análisis de conteo usan directamente la columna mapeada en el paso 2 (Modalidad, "
        "DelitoCOP, Dependencia o Zona). Si ese mensaje aparece, es porque esa columna específica "
        "quedó vacía en el paso 2.", e["Cuerpo"],
    ))
    c.append(_parrafo("<b>¿El DBF no me importa bien las fechas?</b>", e["H2"]))
    c.append(_parrafo(
        "Probá activar \"Elegir manualmente la configuración de fecha y hora\" en el paso 2, y elegí "
        "el formato AAAAMMDD para la fecha (es el formato nativo del tipo \"Fecha\" de DBF, que el "
        "programa ya convierte a AAAA-MM-DD al leerlo, pero por las dudas está disponible como "
        "opción manual).", e["Cuerpo"],
    ))

    return c


# ======================================================================
# English content
# ======================================================================

def _content_en(styles):
    e = styles
    c = []

    c.append(Spacer(1, 4 * cm))
    c.append(_parrafo("Temporal Analysis Software", e["Titulo"]))
    c.append(_parrafo("Technical and user documentation", e["Subtitulo"]))
    c.append(_parrafo(f"Version {VERSION_APP}", e["Version"]))
    c.append(_parrafo(
        "E.P.S.D. Bahía Blanca — Ce.P.A.I.D. Section<br/>"
        "Buenos Aires Provincial Police",
        ParagraphStyle("centered", parent=e["Subtitulo"], fontSize=10),
    ))
    c.append(PageBreak())

    c.append(_parrafo("1. Introduction", e["H1"]))
    c.append(_parrafo(
        "The Temporal Analysis Software is a desktop tool for analyzing the hourly distribution of "
        "events (crimes, interventions, incidents, etc.) from a spreadsheet of data. Its main output "
        "is the <b>Data Clock</b>: a 7-day × 24-hour matrix that uses a color gradient to show which "
        "days and hours concentrate the analyzed events.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "Besides the Data Clock, the software generates charts by time band and by day of the week, "
        "up to four counting analyses (modality, offense, unit and zone) and a general summary page, "
        "exportable to Excel, PDF and PNG.", e["Cuerpo"],
    ))

    c.append(_parrafo("2. Workflow", e["H1"]))
    c.append(_parrafo("The program is organized into 5 steps, in the left sidebar:", e["Cuerpo"]))
    c.append(_lista([
        "<b>1. Import</b>: choose the data file (.xlsx, .xls, .csv or .dbf).",
        "<b>2. Columns</b>: state which column of the file corresponds to each field the program "
        "needs (start/end date and time, unit, modality, zone, DelitoCOP).",
        "<b>3. Filters</b>: optionally narrow the analysis by date/time and by up to 3 more columns, "
        "each with its own values to include.",
        "<b>4. Settings</b>: title, color, time bands, and which optional analyses to generate.",
        "<b>5. Results</b>: enabled once the analysis is generated; shows every page of the report "
        "and lets you export it.",
    ], e["Item"]))
    c.append(_parrafo(
        "The <b>Run Analysis</b> button (bottom-right of \"4. Settings\", or in the top menu) "
        "processes the data with the chosen columns, filters and settings, and builds every page of "
        "the report.", e["Cuerpo"],
    ))

    c.append(_parrafo("3. Supported file formats", e["H1"]))
    c.append(_lista([
        "<b>Excel</b> (.xlsx, .xls): the first sheet of the file is read.",
        "<b>CSV</b> (.csv): separator auto-detected (comma or semicolon).",
        "<b>DBF</b> (.dbf): dBase format, used by some older police/GIS systems. Read with a "
        "built-in decoder, no external library required. \"Memo\" fields (which require a separate "
        ".dbt file) are left blank.",
    ], e["Item"]))

    c.append(_parrafo("4. Required columns and date/time format", e["H1"]))
    c.append(_parrafo(
        "In step \"2. Columns\", all 8 of these columns must be set: start date, start time, end "
        "date, end time, unit, modality, zone and DelitoCOP.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Automatic date/time detection:</b> by default, the program tries several common formats "
        "(YYYY-MM-DD, DD/MM/YYYY, HH:MM:SS, etc.) until one works with the file's data.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Manual format:</b> if automatic detection fails (for example, with ambiguous dates like "
        "\"03/04/2026\", which could be April 3rd or March 4th), check \"Manually choose the date and "
        "time format\" and pick the exact format from a list of options (including AM/PM formats). "
        "That format is tried before the automatic ones.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Midnight crossing without a real end-date column:</b> if the end time is earlier than the "
        "start time AND the start-date and end-date columns are the same column in the file, the "
        "program assumes the event ended the next day and adds one day to the end date automatically. "
        "If the end time equals the start time, it's treated as an instant event (not as having "
        "lasted 24 hours).", e["Nota"],
    ))

    c.append(_parrafo("5. Filters", e["H1"]))
    c.append(_parrafo(
        "<b>Date/time filter:</b> narrows the analysis to a specific date/time range.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Column filters (up to 3, independent of each other):</b> each one picks a column from "
        "the file and lists its unique values, all checked by default. Unchecking some values "
        "excludes from the analysis any events that have them.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Text search:</b> each filter has a search box. Typing text there (e.g. \"moto\") "
        "automatically checks only the values that contain it (\"MOTOS(ROBO)\", \"MOTOCHORROS\", "
        "etc.) and unchecks the rest — it's not just a visual magnifying glass, it changes the actual "
        "selection. Clearing the search shows every value again, with whatever check state was left.",
        e["Cuerpo"],
    ))
    c.append(_parrafo(
        "Combining several filters at once (e.g. date + unit + modality) works as a logical AND: only "
        "events that meet every condition at the same time remain.", e["Nota"],
    ))

    c.append(_parrafo("6. How hours are computed — the heart of the Data Clock", e["H1"]))
    c.append(_parrafo(
        "This is the most important part for correctly reading the Data Clock's numbers. <b>Each "
        "event contributes a total of exactly 1</b> to the matrix, no matter how long it lasted. That "
        "\"1\" is split proportionally across every hour the event occupies.", e["Cuerpo"],
    ))
    c.append(_lista([
        "<b>Instant event</b> (start time equals end time, e.g. an incident logged \"at 14:00\"): "
        "adds a full 1 to that single hour.",
        "<b>Event with a duration, within a single time span</b> (e.g. from 11:20 to 12:40): the 1 "
        "is split proportionally to the time spent in each clock hour it touches. In this example, it "
        "spends 40 minutes in hour 11 and 40 minutes in hour 12 (out of an 80-minute total duration), "
        "so it adds 0.50 to hour 11 and 0.50 to hour 12.",
        "<b>Event spanning several full hours</b> (e.g. from 10:00 to 13:00, 3 hours): the 1 is split "
        "evenly across those 3 hours (0.33 each).",
    ], e["Item"]))
    c.append(_tabla_horas("en"))
    c.append(_parrafo(
        "*Values are rounded to 2 decimals for the table; internally they're computed with more "
        "precision.", e["Nota"],
    ))
    c.append(_parrafo(
        "Thanks to this proportional split, the <b>sum of every cell in the matrix always equals the "
        "number of valid events analyzed</b> (no more, no less), regardless of how long each one "
        "lasted. This is what makes the grand total (the \"FREQ\" cell at the bottom right) useful as "
        "a cross-check.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Midnight crossing:</b> if an event crosses midnight (e.g. from 23:00 to 01:00), each hour "
        "is counted on the day it actually belongs to: hour 23 on the day it started, and hours 0 and "
        "1 on the next day.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Events longer than 24 hours:</b> treated as a data-entry error (e.g. a mistyped end date) "
        "and are NOT included in the matrix. They're counted separately, as \"excluded\", and that "
        "count is computed over the events that already passed the chosen filters (not over the "
        "whole file): if you filter by a given unit and 5 of those filtered events exceed 24 hours, "
        "the program shows exactly those 5 as excluded, not however many exist in the entire file.",
        e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Date/time format errors:</b> rows that can't be parsed as a valid date/time (e.g. an "
        "empty cell or unrecognizable text) are also left out of the analysis, and counted separately "
        "as \"format errors\".", e["Cuerpo"],
    ))

    c.append(_parrafo("7. Configurable time bands", e["H1"]))
    c.append(_parrafo(
        "Besides the hour-by-hour matrix, the Data Clock groups the 24 hours into wider bands (2, 3 "
        "or 4, your choice) to read the overall pattern at a glance.", e["Cuerpo"],
    ))
    c.append(_lista([
        "<b>Number of bands:</b> 4 bands of 6 hours, 3 of 8, or 2 of 12.",
        "<b>Start hour of the first band:</b> configurable (00:00 by default). For example, with a "
        "07:00 start hour and 4 bands: 07-13, 13-19, 19-01 and 01-07.",
        "The <b>00-to-23 matrix never changes layout</b> because of this: only how those 24 columns "
        "are grouped for the totals-by-band block, drawn below, changes. If a band crosses midnight, "
        "it's drawn split into 2 segments (e.g. 19-23 and 00-01), but it still counts as a single "
        "band for calculation purposes.",
    ], e["Item"]))

    c.append(_parrafo("8. Counting analyses (Modality, Offense, Unit, Zone)", e["H1"]))
    c.append(_parrafo(
        "Four optional analyses, independent of each other (any combination can be enabled, even all "
        "4 at once). Each builds a <i>ranking</i>: it counts how many times each distinct value of "
        "the chosen column appears (among the events that passed the filters), sorted from highest "
        "to lowest frequency.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Separator (Modality only):</b> sometimes a single \"modality\" cell holds more than one "
        "value together, separated by a comma (e.g. \"MOTOCHORRO, FIREARM\"). With the separator set "
        "(\",\" by default), the program counts each value separately: that example adds 1 to "
        "\"MOTOCHORRO\" and 1 to \"FIREARM\", not 1 to the whole combination. The other analyses "
        "(Offense, Unit, Zone) don't use a separator: each cell counts as a single, whole value.",
        e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Percentage:</b> each value's frequency divided by the total number of occurrences counted "
        "in that analysis (not by the number of events, if a separator was used and some cells held "
        "more than one value).", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "<b>Amount to chart:</b> how many ranking values to show in that page's chart and table (0 = "
        "all). The exported Excel always includes the full ranking, even if the PDF/screen version "
        "was limited to fewer items for space.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "Each enabled analysis adds its own page to the report (table on top, bar chart below), so it "
        "never competes for space with the others.", e["Nota"],
    ))

    c.append(_parrafo("9. General Summary", e["H1"]))
    c.append(_parrafo(
        "Optional page (checkbox in \"4. Settings\") meant for a quick look without going through the "
        "whole report. Shows, as cards: events analyzed, peak day, peak hour, peak time band, and the "
        "top value (the first one in the ranking) of each enabled counting analysis. Below that, the "
        "charts by time band and by day of the week, and a \"Top 3\" for each enabled analysis.",
        e["Cuerpo"],
    ))
    c.append(_lista([
        "<b>Peak day/hour:</b> the day of the week and the hour of the day with the highest "
        "cumulative frequency in the Data Clock matrix.",
        "<b>Peak time band:</b> the time band (from the ones set up in step 4) with the highest "
        "frequency.",
    ], e["Item"]))

    c.append(_parrafo("10. Visual customization", e["H1"]))
    c.append(_lista([
        "<b>Title and subtitle</b> of the report, in \"4. Settings\".",
        "<b>Data Clock color:</b> red (default), blue, green, orange, purple, gray or teal. Affects "
        "the matrix, the bands block and the time-band chart.",
        "<b>Language:</b> Spanish, English or Portuguese, chosen from the \"Language\" menu, without "
        "restarting the program. The chosen language is saved and restored the next time the program "
        "is opened.",
    ], e["Item"]))

    c.append(_parrafo("11. Export", e["H1"]))
    c.append(_lista([
        "<b>PDF:</b> one file with every page of the report (Data Clock, by day, one per enabled "
        "analysis, and the General Summary if enabled). The number of pages varies depending on how "
        "many analyses were enabled.",
        "<b>Excel:</b> a \"1. Data Clock\" sheet with the full matrix, one sheet per enabled counting "
        "analysis (with the full ranking, no item limit), and a \"General Summary\" sheet if enabled.",
        "<b>PNG:</b> one image file per page of the report.",
    ], e["Item"]))
    c.append(_parrafo(
        "Files are suggested under the name \"DataClock_YYYYMMDD_HHMMSS\" (the date and time at the "
        "moment of export). After exporting, the program asks whether to open the generated file.",
        e["Cuerpo"],
    ))

    c.append(_parrafo("12. Save and load configuration", e["H1"]))
    c.append(_parrafo(
        "From the File menu or from the \"1. Import\" tab (buttons enabled once a file is imported), "
        "the whole current configuration can be saved to a .json file: the mapped columns, the "
        "filters (including each one's checked values) and the step-4 settings. This saves you from "
        "rebuilding everything when a new file of the same type (same columns) comes in.", e["Cuerpo"],
    ))
    c.append(_parrafo(
        "When loading a saved configuration, the program validates every column against the "
        "currently imported file: if any no longer exists (e.g. the new file uses a different column "
        "name), it warns which ones with a message, instead of failing silently or applying something "
        "incorrect.", e["Cuerpo"],
    ))

    c.append(_parrafo("13. Frequently asked questions", e["H1"]))
    c.append(_parrafo(
        "<b>Why doesn't the matrix total match the row count of my original file?</b>", e["H2"],
    ))
    c.append(_parrafo(
        "Because filters were applied, or because some rows were excluded for exceeding 24 hours in "
        "duration or for having a date/time format error. The text \"Events analyzed: N · Excluded "
        "for exceeding 24 hs: M\" shown below the Data Clock's title shows both numbers; N + M should "
        "match the number of rows that passed the chosen filters.", e["Cuerpo"],
    ))
    c.append(_parrafo("<b>Why does an analysis ask for a column I already picked?</b>", e["H2"]))
    c.append(_parrafo(
        "Counting analyses use directly the column mapped in step 2 (Modality, DelitoCOP, Unit or "
        "Zone). If that message appears, it's because that specific column was left empty in step 2.",
        e["Cuerpo"],
    ))
    c.append(_parrafo("<b>My DBF dates aren't importing correctly?</b>", e["H2"]))
    c.append(_parrafo(
        "Try turning on \"Manually choose the date and time format\" in step 2, and pick the YYYYMMDD "
        "format for the date (that's DBF's native \"Date\" field format, which the program already "
        "converts to YYYY-MM-DD when reading it, but it's available as a manual option just in case).",
        e["Cuerpo"],
    ))

    return c


def generar(idioma: str, filepath: str) -> None:
    estilos = _estilos()
    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        topMargin=2.2 * cm, bottomMargin=2 * cm, leftMargin=2.2 * cm, rightMargin=2.2 * cm,
        title="Software de Análisis Temporal — Documentación" if idioma == "es"
        else "Temporal Analysis Software — Documentation",
    )
    contenido = _contenido_es(estilos) if idioma == "es" else _content_en(estilos)
    doc.build(
        contenido,
        onFirstPage=lambda cv, d: _pie_de_pagina(cv, d, idioma),
        onLaterPages=lambda cv, d: _pie_de_pagina(cv, d, idioma),
    )


def main() -> None:
    os.makedirs(CARPETA_SALIDA, exist_ok=True)
    ruta_es = os.path.join(CARPETA_SALIDA, "documentacion_es.pdf")
    ruta_en = os.path.join(CARPETA_SALIDA, "documentation_en.pdf")
    generar("es", ruta_es)
    generar("en", ruta_en)
    print(f"Generado: {ruta_es}")
    print(f"Generado: {ruta_en}")


if __name__ == "__main__":
    main()
