"""
i18n.py

Soporte de idioma español/inglés/portugués para toda la aplicación:
interfaz, informes exportados (PDF/PNG) y Excel. Traducción
centralizada: cada texto visible tiene una clave, y esta clave se
resuelve al idioma activo con tr(clave). Cambiar el idioma no requiere
reiniciar la app: cada widget con textos expone un método retranslate()
que se vuelve a llamar cuando cambia el idioma (ver gui/idioma_bus.py).
El idioma elegido se guarda en disco (ver settings.py) y se restaura
automáticamente la próxima vez que se abre el programa.
"""
from typing import Dict

IDIOMA_POR_DEFECTO = "es"
IDIOMAS_DISPONIBLES = ("es", "en", "pt")


class _EstadoIdioma:
    actual = IDIOMA_POR_DEFECTO


def idioma_actual() -> str:
    return _EstadoIdioma.actual


def establecer_idioma(idioma: str) -> None:
    if idioma in IDIOMAS_DISPONIBLES:
        _EstadoIdioma.actual = idioma


_TEXTOS: Dict[str, Dict[str, str]] = {
    # --- General / marca ---
    "app.nombre": {"es": "Software de Análisis Temporal", "en": "Temporal Analysis Software",
                   "pt": "Software de Análise Temporal"},
    "app.organizacion": {"es": "EPSD Bahía Blanca - CePAID", "en": "EPSD Bahía Blanca - CePAID",
                          "pt": "EPSD Bahía Blanca - CePAID"},

    # --- Menú ---
    "menu.archivo": {"es": "&Archivo", "en": "&File", "pt": "&Arquivo"},
    "menu.archivo.abrir": {"es": "Abrir…", "en": "Open…", "pt": "Abrir…"},
    "menu.archivo.cerrar": {"es": "Cerrar análisis", "en": "Close analysis", "pt": "Fechar análise"},
    "menu.archivo.guardar_config": {"es": "Guardar configuración…", "en": "Save configuration…",
                                     "pt": "Salvar configuração…"},
    "menu.archivo.cargar_config": {"es": "Cargar configuración…", "en": "Load configuration…",
                                    "pt": "Carregar configuração…"},
    "menu.archivo.salir": {"es": "Salir", "en": "Exit", "pt": "Sair"},
    "menu.generar": {"es": "Generar Análisis", "en": "Run Analysis", "pt": "Gerar Análise"},
    "menu.exportar": {"es": "&Exportar", "en": "&Export", "pt": "&Exportar"},
    "menu.exportar.excel": {"es": "Exportar a Excel…", "en": "Export to Excel…", "pt": "Exportar para Excel…"},
    "menu.exportar.pdf": {"es": "Exportar a PDF…", "en": "Export to PDF…", "pt": "Exportar para PDF…"},
    "menu.exportar.png": {"es": "Exportar todo a PNG…", "en": "Export all to PNG…", "pt": "Exportar tudo para PNG…"},
    "menu.idioma": {"es": "&Idioma", "en": "&Language", "pt": "&Idioma"},
    "menu.idioma.es": {"es": "Español", "en": "Spanish", "pt": "Espanhol"},
    "menu.idioma.en": {"es": "English", "en": "English", "pt": "Inglês"},
    "menu.idioma.pt": {"es": "Português", "en": "Portuguese", "pt": "Português"},
    "menu.acerca_de": {"es": "Acerca de", "en": "About", "pt": "Sobre"},
    "menu.docs": {"es": "Docs", "en": "Docs", "pt": "Docs"},
    "dialogo.docs_no_encontrada": {
        "es": "No se encontró el archivo de documentación:\n{ruta}",
        "en": "Documentation file not found:\n{ruta}",
        "pt": "Arquivo de documentação não encontrado:\n{ruta}",
    },
    "dialogo.acerca_de.titulo": {"es": "Acerca de", "en": "About", "pt": "Sobre"},
    "dialogo.cerrar_analisis.titulo": {"es": "Cerrar análisis", "en": "Close analysis", "pt": "Fechar análise"},
    "dialogo.cerrar_analisis.texto": {
        "es": "Esto borra el archivo importado y los resultados generados. ¿Continuar?",
        "en": "This clears the imported file and any generated results. Continue?",
        "pt": "Isso apaga o arquivo importado e os resultados gerados. Continuar?",
    },
    "status.analisis_cerrado": {"es": "Análisis cerrado.", "en": "Analysis closed.", "pt": "Análise fechada."},
    "status.archivo_cargado": {"es": "Archivo cargado: {ruta}", "en": "File loaded: {ruta}",
                                "pt": "Arquivo carregado: {ruta}"},
    "status.generado_ok": {"es": "Reloj de Datos generado correctamente.", "en": "Data Clock generated successfully.",
                            "pt": "Relógio de Dados gerado com sucesso."},
    "status.exportado": {"es": "Exportado a {ruta}", "en": "Exported to {ruta}", "pt": "Exportado para {ruta}"},
    "status.exportado_pdf": {"es": "Exportado a {ruta} ({n} páginas)", "en": "Exported to {ruta} ({n} pages)",
                              "pt": "Exportado para {ruta} ({n} páginas)"},
    "status.exportado_png": {"es": "Exportado a {n} archivos PNG", "en": "Exported to {n} PNG files",
                              "pt": "Exportado para {n} arquivos PNG"},

    "dialogo.falta_importar.titulo": {"es": "Falta importar datos", "en": "No data imported",
                                       "pt": "Faltam dados importados"},
    "dialogo.falta_importar.texto": {"es": "Primero importá un archivo Excel o CSV.",
                                      "en": "First import an Excel or CSV file.",
                                      "pt": "Primeiro importe um arquivo Excel ou CSV."},
    "dialogo.columnas_incompletas.titulo": {"es": "Columnas incompletas", "en": "Incomplete columns",
                                             "pt": "Colunas incompletas"},
    "dialogo.columnas_incompletas.texto": {
        "es": "Definí las 8 columnas obligatorias en la pestaña '2. Columnas': "
              "fecha/hora de inicio y fin, dependencia, modalidad, zona y DelitoCOP.",
        "en": "Set all 8 required columns in the '2. Columns' tab: "
              "start/end date and time, unit, modality, zone and DelitoCOP.",
        "pt": "Defina as 8 colunas obrigatórias na aba '2. Colunas': "
              "data/hora de início e fim, unidade, modalidade, zona e DelitoCOP.",
    },
    "dialogo.sin_resultados.titulo": {"es": "Sin resultados", "en": "No results", "pt": "Sem resultados"},
    "dialogo.sin_resultados.texto": {"es": "No quedaron eventos luego de aplicar los filtros.",
                                      "en": "No events remained after applying the filters.",
                                      "pt": "Não restaram eventos após aplicar os filtros."},
    "dialogo.nada_exportar.titulo": {"es": "Nada para exportar", "en": "Nothing to export",
                                      "pt": "Nada para exportar"},
    "dialogo.nada_exportar.texto": {
        "es": "Primero generá el Reloj de Datos (botón Generar Análisis).",
        "en": "First generate the Data Clock (Run Analysis button).",
        "pt": "Primeiro gere o Relógio de Dados (botão Gerar Análise).",
    },
    "dialogo.error_exportar.titulo": {"es": "Error al exportar", "en": "Export error", "pt": "Erro ao exportar"},
    "dialogo.error_excel": {"es": "No se pudo generar el Excel:\n{exc}", "en": "Could not generate the Excel file:\n{exc}",
                             "pt": "Não foi possível gerar o Excel:\n{exc}"},
    "dialogo.error_pdf": {"es": "No se pudo generar el PDF:\n{exc}", "en": "Could not generate the PDF file:\n{exc}",
                           "pt": "Não foi possível gerar o PDF:\n{exc}"},
    "dialogo.error_imagen": {"es": "No se pudo generar la imagen:\n{exc}", "en": "Could not generate the image:\n{exc}",
                              "pt": "Não foi possível gerar a imagem:\n{exc}"},

    "dialogo.guardar_config.titulo": {"es": "Guardar configuración", "en": "Save configuration",
                                       "pt": "Salvar configuração"},
    "dialogo.guardar_config.ok": {"es": "Configuración guardada en:\n{ruta}", "en": "Configuration saved to:\n{ruta}",
                                   "pt": "Configuração salva em:\n{ruta}"},
    "dialogo.guardar_config.error": {"es": "No se pudo guardar la configuración:\n{exc}",
                                      "en": "Could not save the configuration:\n{exc}",
                                      "pt": "Não foi possível salvar a configuração:\n{exc}"},
    "dialogo.cargar_config.titulo": {"es": "Cargar configuración", "en": "Load configuration",
                                      "pt": "Carregar configuração"},
    "dialogo.cargar_config.error": {"es": "No se pudo cargar la configuración:\n{exc}",
                                     "en": "Could not load the configuration:\n{exc}",
                                     "pt": "Não foi possível carregar a configuração:\n{exc}"},
    "dialogo.cargar_config.ok": {"es": "Configuración cargada correctamente.",
                                  "en": "Configuration loaded successfully.",
                                  "pt": "Configuração carregada com sucesso."},
    "dialogo.cargar_config.columnas_faltantes.titulo": {"es": "Columnas no encontradas",
                                                          "en": "Columns not found",
                                                          "pt": "Colunas não encontradas"},
    "dialogo.cargar_config.columnas_faltantes.texto": {
        "es": "La configuración se cargó, pero estas columnas no existen en el archivo "
              "actualmente importado (quedaron sin asignar):\n{columnas}",
        "en": "The configuration was loaded, but these columns don't exist in the currently "
              "imported file (left unassigned):\n{columnas}",
        "pt": "A configuração foi carregada, mas essas colunas não existem no arquivo "
              "atualmente importado (ficaram sem atribuir):\n{columnas}",
    },
    "dialogo.falta_archivo_config.titulo": {"es": "Falta importar un archivo", "en": "No file imported",
                                             "pt": "Falta importar um arquivo"},
    "dialogo.falta_archivo_config.texto": {
        "es": "Primero importá un archivo Excel, CSV o DBF para poder guardar o cargar una configuración.",
        "en": "First import an Excel, CSV or DBF file to save or load a configuration.",
        "pt": "Primeiro importe um arquivo Excel, CSV ou DBF para salvar ou carregar uma configuração.",
    },

    "dialogo.exportacion_exitosa.titulo": {"es": "Exportación exitosa", "en": "Export successful",
                                            "pt": "Exportação bem-sucedida"},
    "dialogo.exportacion_exitosa.texto": {
        "es": "Se exportó correctamente a:\n{ruta}\n\n¿Querés abrir el archivo ahora?",
        "en": "Successfully exported to:\n{ruta}\n\nDo you want to open the file now?",
        "pt": "Exportado com sucesso para:\n{ruta}\n\nDeseja abrir o arquivo agora?",
    },
    "dialogo.exportacion_exitosa.texto_multiple": {
        "es": "Se generaron {n} imágenes en:\n{ruta}\n\n¿Querés abrir la primera ahora?",
        "en": "{n} images were generated in:\n{ruta}\n\nDo you want to open the first one now?",
        "pt": "Foram geradas {n} imagens em:\n{ruta}\n\nDeseja abrir a primeira agora?",
    },
    "dialogo.no_se_pudo_abrir": {"es": "No se pudo abrir el archivo automáticamente. Lo encontrás en:\n{ruta}",
                                  "en": "Could not open the file automatically. You can find it at:\n{ruta}",
                                  "pt": "Não foi possível abrir o arquivo automaticamente. Você o encontra em:\n{ruta}"},
    "dialogo.exportado_png.titulo": {"es": "Exportado", "en": "Exported", "pt": "Exportado"},
    "dialogo.exportado_png.texto": {
        "es": "Se generaron {n} imágenes (una por página):\n{rutas}",
        "en": "{n} images were generated (one per page):\n{rutas}",
        "pt": "Foram geradas {n} imagens (uma por página):\n{rutas}",
    },
    "dialogo.falta_columna.titulo": {"es": "Falta columna de {nombre}", "en": "Missing {nombre} column",
                                      "pt": "Falta a coluna de {nombre}"},
    "dialogo.falta_columna.texto": {
        "es": "Activaste el análisis de {nombre} pero no elegiste esa columna en la pestaña '2. Columnas'.",
        "en": "You enabled the {nombre} analysis but didn't pick that column in the '2. Columns' tab.",
        "pt": "Você ativou a análise de {nombre}, mas não escolheu essa coluna na aba '2. Colunas'.",
    },
    "nombre.modalidades": {"es": "modalidades", "en": "modalities", "pt": "modalidades"},
    "nombre.delitos": {"es": "delitos", "en": "offenses", "pt": "delitos"},
    "nombre.dependencia": {"es": "dependencia policial", "en": "police unit", "pt": "unidade policial"},
    "nombre.zona": {"es": "zona", "en": "zone", "pt": "zona"},

    # --- Pestañas (navegación lateral) ---
    "tab.importar": {"es": "1. Importar", "en": "1. Import", "pt": "1. Importar"},
    "tab.columnas": {"es": "2. Columnas", "en": "2. Columns", "pt": "2. Colunas"},
    "tab.filtros": {"es": "3. Filtros", "en": "3. Filters", "pt": "3. Filtros"},
    "tab.configuracion": {"es": "4. Configuración", "en": "4. Settings", "pt": "4. Configuração"},
    "tab.resultados": {"es": "5. Resultados", "en": "5. Results", "pt": "5. Resultados"},

    # --- Importar ---
    "importar.examinar": {"es": "Examinar archivo (.xlsx, .xls, .csv, .dbf)…",
                           "en": "Browse file (.xlsx, .xls, .csv, .dbf)…",
                           "pt": "Procurar arquivo (.xlsx, .xls, .csv, .dbf)…"},
    "importar.ninguno": {"es": "Ningún archivo seleccionado.", "en": "No file selected.",
                          "pt": "Nenhum arquivo selecionado."},
    "importar.info": {"es": "{n} registros importados · {c} columnas.", "en": "{n} records imported · {c} columns.",
                       "pt": "{n} registros importados · {c} colunas."},
    "importar.dialogo_titulo": {"es": "Seleccionar archivo de datos", "en": "Select data file",
                                 "pt": "Selecionar arquivo de dados"},
    "importar.formato_no_soportado.titulo": {"es": "Formato no soportado", "en": "Unsupported format",
                                              "pt": "Formato não suportado"},
    "importar.error_titulo": {"es": "Error al importar", "en": "Import error", "pt": "Erro ao importar"},
    "importar.error_texto": {"es": "No se pudo leer el archivo:\n{exc}", "en": "Could not read the file:\n{exc}",
                              "pt": "Não foi possível ler o arquivo:\n{exc}"},
    "importar.guardar_config": {"es": "Guardar configuración…", "en": "Save configuration…",
                                 "pt": "Salvar configuração…"},
    "importar.cargar_config": {"es": "Cargar configuración…", "en": "Load configuration…",
                                "pt": "Carregar configuração…"},

    # --- Columnas (mapeo) ---
    "mapeo.grupo_obligatorias": {"es": "Columnas obligatorias", "en": "Required columns",
                                  "pt": "Colunas obrigatórias"},
    "mapeo.fecha_inicio": {"es": "Fecha de inicio:", "en": "Start date:", "pt": "Data de início:"},
    "mapeo.hora_inicio": {"es": "Hora de inicio:", "en": "Start time:", "pt": "Hora de início:"},
    "mapeo.fecha_fin": {"es": "Fecha de finalización:", "en": "End date:", "pt": "Data de término:"},
    "mapeo.hora_fin": {"es": "Hora de finalización:", "en": "End time:", "pt": "Hora de término:"},
    "mapeo.grupo_opcionales": {"es": "Columnas opcionales", "en": "Optional columns", "pt": "Colunas opcionais"},
    "mapeo.id_evento": {"es": "ID del evento:", "en": "Event ID:", "pt": "ID do evento:"},
    "mapeo.dependencia": {"es": "Dependencia policial:", "en": "Police unit:", "pt": "Unidade policial:"},
    "mapeo.modalidad": {"es": "Modalidad:", "en": "Modality:", "pt": "Modalidade:"},
    "mapeo.tipo_delito": {"es": "Tipo de delito:", "en": "Offense type:", "pt": "Tipo de delito:"},
    "mapeo.zona": {"es": "Zona:", "en": "Zone:", "pt": "Zona:"},
    "mapeo.delito": {"es": "DelitoCOP:", "en": "DelitoCOP:", "pt": "DelitoCOP:"},
    "mapeo.vacio": {"es": "— (ninguna) —", "en": "— (none) —", "pt": "— (nenhuma) —"},
    "mapeo.grupo_formato": {"es": "Formato de fecha y hora", "en": "Date and time format",
                             "pt": "Formato de data e hora"},
    "mapeo.formato_manual": {"es": "Elegir manualmente la configuración de fecha y hora:",
                              "en": "Manually choose the date and time format:",
                              "pt": "Escolher manualmente o formato de data e hora:"},
    "mapeo.formato_fecha": {"es": "Formato de fecha:", "en": "Date format:", "pt": "Formato de data:"},
    "mapeo.formato_hora": {"es": "Formato de hora:", "en": "Time format:", "pt": "Formato de hora:"},

    # --- Filtros ---
    "filtros.grupo_temporal": {"es": "Filtro temporal", "en": "Date/time filter", "pt": "Filtro temporal"},
    "filtros.desde": {"es": "Fecha/hora desde:", "en": "Date/time from:", "pt": "Data/hora de:"},
    "filtros.hasta": {"es": "Fecha/hora hasta:", "en": "Date/time to:", "pt": "Data/hora até:"},
    "filtros.filtro_n": {"es": "Filtro {n}", "en": "Filter {n}", "pt": "Filtro {n}"},
    "filtros.sin_columna": {"es": "— sin filtrar —", "en": "— not filtered —", "pt": "— sem filtro —"},
    "filtros.buscar_placeholder": {"es": "Buscar (ej: moto)…", "en": "Search (e.g: moto)…", "pt": "Buscar (ex: moto)…"},
    "filtros.n_valores": {"es": "{n} de {total} valores", "en": "{n} of {total} values",
                           "pt": "{n} de {total} valores"},
    "filtros.descripcion_fecha": {"es": "Fecha: {desde} a {hasta}", "en": "Date: {desde} to {hasta}",
                                   "pt": "Data: {desde} a {hasta}"},
    "filtros.descripcion_prefijo": {"es": "Filtros aplicados:", "en": "Filters applied:",
                                     "pt": "Filtros aplicados:"},
    "reloj.sin_filtros": {"es": "Sin filtros aplicados", "en": "No filters applied", "pt": "Sem filtros aplicados"},

    # --- Configuración ---
    "config.grupo_titulo": {"es": "Título del Reloj de Datos", "en": "Data Clock title",
                             "pt": "Título do Relógio de Dados"},
    "config.titulo_a_mostrar": {"es": "Título a mostrar:", "en": "Title to display:", "pt": "Título a exibir:"},
    "config.subtitulo": {"es": "Subtítulo (opcional):", "en": "Subtitle (optional):", "pt": "Subtítulo (opcional):"},
    "config.subtitulo_placeholder": {
        "es": "Opcional, por ejemplo: Dependencia / Turno / Zona analizada",
        "en": "Optional, e.g.: Unit / Shift / Zone analyzed",
        "pt": "Opcional, por exemplo: Unidade / Turno / Zona analisada",
    },
    "config.grupo_franjas": {"es": "Totales por franja horaria", "en": "Totals by time band",
                              "pt": "Totais por faixa horária"},
    "config.hora_inicio_franjas": {"es": "Hora de inicio de la primera franja:",
                                    "en": "Start hour of the first band:",
                                    "pt": "Hora de início da primeira faixa:"},
    "config.franjas_n_horas": {"es": "{n} franjas de {h} horas ({rango})", "en": "{n} bands of {h} hours ({rango})",
                                "pt": "{n} faixas de {h} horas ({rango})"},
    "config.a_conector": {"es": "A", "en": "TO", "pt": "ÀS"},
    "config.modalidades_titulo": {"es": "Análisis de modalidades (opcional)", "en": "Modality analysis (optional)",
                                   "pt": "Análise de modalidades (opcional)"},
    "config.delitos_titulo": {"es": "Análisis de delitos (opcional)", "en": "Offense analysis (optional)",
                               "pt": "Análise de delitos (opcional)"},
    "config.dependencia_titulo": {"es": "Análisis por dependencia policial (opcional)",
                                   "en": "Police unit analysis (optional)",
                                   "pt": "Análise por unidade policial (opcional)"},
    "config.zona_titulo": {"es": "Análisis por zona (opcional)", "en": "Zone analysis (optional)",
                            "pt": "Análise por zona (opcional)"},
    "config.realizar": {"es": "Realizar {titulo}", "en": "Run {titulo}", "pt": "Realizar {titulo}"},
    "config.separador": {"es": "Separador (por defecto \",\"):", "en": "Separator (default \",\"):",
                          "pt": "Separador (padrão \",\"):"},
    "config.cantidad_graficar": {"es": "Cantidad a graficar (0 = todas):", "en": "Amount to chart (0 = all):",
                                  "pt": "Quantidade a exibir (0 = todas):"},
    "config.todas": {"es": "Todas", "en": "All", "pt": "Todas"},
    "config.generar_boton": {"es": "⏱  Generar Análisis", "en": "⏱  Run Analysis", "pt": "⏱  Gerar Análise"},
    "config.color_reloj": {"es": "Color del Reloj de Datos:", "en": "Data Clock color:", "pt": "Cor do Relógio de Dados:"},
    "color.rojo": {"es": "Rojo (por defecto)", "en": "Red (default)", "pt": "Vermelho (padrão)"},
    "color.azul": {"es": "Azul", "en": "Blue", "pt": "Azul"},
    "color.verde": {"es": "Verde", "en": "Green", "pt": "Verde"},
    "color.naranja": {"es": "Naranja", "en": "Orange", "pt": "Laranja"},
    "color.morado": {"es": "Morado", "en": "Purple", "pt": "Roxo"},
    "color.gris": {"es": "Gris", "en": "Gray", "pt": "Cinza"},
    "color.turquesa": {"es": "Turquesa", "en": "Teal", "pt": "Turquesa"},

    # --- Resultados ---
    "resultados.pendiente": {"es": "Todavía no se generó el Reloj de Datos.",
                              "en": "The Data Clock hasn't been generated yet.",
                              "pt": "O Relógio de Dados ainda não foi gerado."},
    "resultados.exportar_pdf": {"es": "Exportar a PDF", "en": "Export to PDF", "pt": "Exportar para PDF"},
    "resultados.resumen": {
        "es": "{n} eventos procesados · {ex} excluidos por superar 24 hs · {er} con error de formato de fecha/hora.",
        "en": "{n} events processed · {ex} excluded for exceeding 24 hs · {er} with date/time format errors.",
        "pt": "{n} eventos processados · {ex} excluídos por superar 24 hs · {er} com erro de formato de data/hora.",
    },
    "resultados.pagina1": {"es": "Página 1 — Reloj de Datos", "en": "Page 1 — Data Clock",
                            "pt": "Página 1 — Relógio de Dados"},
    "resultados.pagina2": {"es": "Página 2 — Gráficos", "en": "Page 2 — Charts", "pt": "Página 2 — Gráficos"},
    "resultados.pagina_n": {"es": "Página {n} de {total}", "en": "Page {n} of {total}",
                             "pt": "Página {n} de {total}"},

    # --- Contenido de los informes (reloj + gráficos) ---
    "reloj.titulo_defecto": {"es": "RELOJ DE DATOS", "en": "DATA CLOCK", "pt": "RELÓGIO DE DADOS"},
    "reloj.frec": {"es": "FREC", "en": "FREQ", "pt": "FREQ"},
    "reloj.pct": {"es": "%", "en": "%", "pt": "%"},
    "reloj.dias": {"es": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
                   "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                   "pt": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]},
    "reloj.periodo_analizado": {"es": "Período analizado: {desde} a {hasta}",
                                 "en": "Period analyzed: {desde} to {hasta}",
                                 "pt": "Período analisado: {desde} a {hasta}"},
    "reloj.eventos_stats": {
        "es": "Eventos analizados: {n}  ·  Excluidos por superar 24 hs: {ex}",
        "en": "Events analyzed: {n}  ·  Excluded for exceeding 24 hs: {ex}",
        "pt": "Eventos analisados: {n}  ·  Excluídos por superar 24 hs: {ex}",
    },
    "reloj.pagina_de": {"es": "Página {n} de {total}", "en": "Page {n} of {total}", "pt": "Página {n} de {total}"},
    "graficos.titulo": {"es": "{titulo} — Gráficos", "en": "{titulo} — Charts", "pt": "{titulo} — Gráficos"},
    "graficos.por_franja": {"es": "Frecuencia por franja horaria", "en": "Frequency by time band",
                             "pt": "Frequência por faixa horária"},
    "graficos.por_dia": {"es": "Frecuencia por día de la semana", "en": "Frequency by day of week",
                          "pt": "Frequência por dia da semana"},
    "graficos.ranking_modalidades": {"es": "Ranking de modalidades", "en": "Modality ranking",
                                      "pt": "Ranking de modalidades"},
    "graficos.ranking_delitos": {"es": "Ranking de delitos", "en": "Offense ranking", "pt": "Ranking de delitos"},
    "graficos.ranking_dependencia": {"es": "Ranking por dependencia policial", "en": "Ranking by police unit",
                                      "pt": "Ranking por unidade policial"},
    "graficos.ranking_zona": {"es": "Ranking por zona", "en": "Ranking by zone", "pt": "Ranking por zona"},
    "graficos.ranking_recortado": {
        "es": "Mostrando los primeros {n} de {total} ítems (el Excel exportado tiene el listado completo).",
        "en": "Showing the top {n} of {total} items (the exported Excel has the full list).",
        "pt": "Mostrando os primeiros {n} de {total} itens (o Excel exportado tem a lista completa).",
    },
    "graficos.titulo_resumen": {"es": "{titulo} — Resumen General", "en": "{titulo} — General Summary",
                                 "pt": "{titulo} — Resumo Geral"},
    "config.resumen_ejecutivo": {"es": "Generar resumen general (opcional)",
                                  "en": "Generate general summary (optional)",
                                  "pt": "Gerar resumo geral (opcional)"},
    "resumen.eventos_analizados": {"es": "EVENTOS ANALIZADOS", "en": "EVENTS ANALYZED", "pt": "EVENTOS ANALISADOS"},
    "resumen.dia_pico": {"es": "DÍA PICO", "en": "PEAK DAY", "pt": "DIA DE PICO"},
    "resumen.hora_pico": {"es": "HORA PICO", "en": "PEAK HOUR", "pt": "HORA DE PICO"},
    "resumen.hora_formato": {"es": "{h:02d}:00 hs", "en": "{h:02d}:00 hrs", "pt": "{h:02d}:00 h"},
    "resumen.franja_pico": {"es": "FRANJA PICO", "en": "PEAK TIME BAND", "pt": "FAIXA DE PICO"},
    "resumen.principal": {"es": "{nombre} PRINCIPAL", "en": "TOP {nombre}", "pt": "{nombre} PRINCIPAL"},
    "resumen.top_n": {"es": "Top {n} — {nombre}", "en": "Top {n} — {nombre}", "pt": "Top {n} — {nombre}"},
    "tabla.pos": {"es": "Pos.", "en": "Rank", "pt": "Pos."},
    "tabla.frec": {"es": "Frec.", "en": "Freq.", "pt": "Freq."},
    "tabla.pct": {"es": "%", "en": "%", "pt": "%"},
    "tabla.modalidad": {"es": "Modalidad", "en": "Modality", "pt": "Modalidade"},
    "tabla.delito": {"es": "Delito", "en": "Offense", "pt": "Delito"},
    "tabla.dependencia": {"es": "Dependencia", "en": "Police unit", "pt": "Unidade"},
    "tabla.zona": {"es": "Zona", "en": "Zone", "pt": "Zona"},
    "tabla.posicion": {"es": "Posición", "en": "Rank", "pt": "Posição"},
    "tabla.descripcion": {"es": "Descripción", "en": "Description", "pt": "Descrição"},
    "tabla.frecuencia": {"es": "Frecuencia", "en": "Frequency", "pt": "Frequência"},
    "tabla.porcentaje": {"es": "Porcentaje", "en": "Percentage", "pt": "Porcentagem"},
    "excel.hoja_reloj": {"es": "1. Reloj de Datos", "en": "1. Data Clock", "pt": "1. Relógio de Dados"},
    "excel.hoja_ranking_modalidades": {"es": "Ranking de modalidades", "en": "Modality ranking",
                                        "pt": "Ranking de modalidades"},
    "excel.hoja_ranking_delitos": {"es": "Ranking de delitos", "en": "Offense ranking", "pt": "Ranking de delitos"},
    "excel.hoja_resumen": {"es": "Resumen General", "en": "General Summary", "pt": "Resumo Geral"},
}


def tr(clave: str, **kwargs) -> str:
    """Devuelve el texto para `clave` en el idioma activo, con formato
    opcional vía kwargs (usa str.format)."""
    entrada = _TEXTOS.get(clave)
    if entrada is None:
        return clave
    texto = entrada.get(_EstadoIdioma.actual, entrada.get("es", clave))
    if isinstance(texto, list):
        return texto
    if kwargs:
        try:
            return texto.format(**kwargs)
        except (KeyError, IndexError):
            return texto
    return texto
