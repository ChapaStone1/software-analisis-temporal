# Historial de cambios (Changelog)

Registro cronológico (más reciente primero) del desarrollo de este
software. Para la documentación de uso y la arquitectura actual, ver
[README.md](README.md) y los PDF en `reloj_datos/assets/docs/`
(menú **Docs** dentro de la aplicación).

---

## Novedades de esta ronda (documentación, repo y empaquetado)

- **Documentación completa del software**, en español e inglés
  (`reloj_datos/assets/docs/documentacion_es.pdf` /
  `documentation_en.pdf`), generada con `reportlab` a partir de
  `tools/generar_documentacion.py`. Cubre el flujo de trabajo completo,
  los formatos soportados, el mapeo de columnas y el formato de fecha/
  hora manual, los filtros, **cómo se calculan las horas del Reloj de
  Datos** (con tabla de ejemplo), las franjas horarias, los 4 análisis
  de conteo, el Resumen General, la exportación, guardar/cargar
  configuración, y preguntas frecuentes.
- **Menú "Docs"** en la barra superior: abre el PDF correspondiente al
  idioma activo (español o inglés; portugués usa el PDF en inglés) con
  el visor de PDF predeterminado del sistema.
- **Repositorio preparado para GitHub**: `LICENSE` (MIT, uso libre),
  `.gitignore`, un `README.md` nuevo con estilo GitHub (badges,
  secciones, tabla de contenidos), y el README anterior (que en
  realidad era un historial de cambios) movido a este mismo
  `CHANGELOG.md`.
- **Scripts de empaquetado para instaladores**, en `packaging/`:
  - Windows: `packaging/windows/installer.iss` (Inno Setup) +
    `build_installer.bat`, que encadena PyInstaller y Inno Setup y
    genera `SoftwareAnalisisTemporal-Setup.exe`.
  - Linux: `packaging/linux/build_deb.sh`, que encadena PyInstaller y
    `dpkg-deb` y genera un `.deb` instalable con ícono, entrada de
    menú y lanzador en `/usr/bin`. Se probó armando el paquete con un
    binario de prueba: `dpkg-deb` lo construyó sin errores, con la
    estructura y los metadatos correctos.
  - `packaging/README.md` con las instrucciones paso a paso de cada
    instalador, y cómo publicarlos como *Release* de GitHub.

## Novedades de la ronda anterior (correcciones)

- **Bug grave corregido: el filtro por texto no filtraba de verdad.**
  Escribir "moto" solo OCULTABA los demás valores, pero como todos
  arrancan tildados por defecto, los ocultos seguían contando como
  seleccionados — por eso el Reloj de Datos salía con todos los
  registros igual. Ahora escribir un texto de búsqueda tilda
  exactamente los valores que coinciden y destilda el resto (no es
  solo una lupa visual, filtra la selección real).
- **Los filtros ahora muestran mínimo 6 registros** sin scrollear (antes
  el alto máximo de la lista era muy chico). Si hay más valores de los
  que entran, aparece la barra de scroll vertical (ya la traía
  QListWidget, pero el alto era insuficiente para notarla bien).
- **Corregido "Guardar/Cargar configuración" del menú Archivo**, que
  quedaba siempre deshabilitado: `main_window.py` llamaba a un método
  (`config_widget.cargar_columnas`) que ya no existe desde que se sacó
  el selector de columna de los análisis opcionales; esa llamada
  fallaba en silencio y cortaba la función justo antes de habilitar
  esos dos ítems del menú. Los botones de la pestaña "1. Importar" no
  tenían este problema porque se habilitan en otro punto del código,
  por eso solo fallaba el menú.

## Novedades de la ronda anterior

- **Guardar / cargar configuración**: nuevos ítems en el menú Archivo
  ("Guardar configuración…" / "Cargar configuración…") y botones
  equivalentes en la pestaña "1. Importar", habilitados recién cuando
  hay un archivo importado. Guarda en un archivo `.json` todo lo del
  paso 2 (columnas mapeadas, formato de fecha/hora manual), el paso 3
  (filtros, incluida la selección de valores de cada uno) y el paso 4
  (título, subtítulo, color, franjas, y cada análisis con su estado,
  separador y cantidad a graficar). Si al cargar una configuración
  alguna columna guardada no existe en el archivo actualmente
  importado, se avisa con un mensaje en vez de fallar en silencio.
- **Búsqueda por texto en los filtros**: cada uno de los 3 filtros
  ahora tiene un campo de búsqueda que oculta los valores que no
  contienen el texto escrito (por ejemplo, escribir "moto" deja
  visibles solo "MOTOS(ROBO)", "MOTOCHORROS", etc.), sin alterar qué
  valores quedaron tildados.
- **Popup de exportación exitosa**: al exportar a Excel, PDF o PNG,
  aparece un mensaje de confirmación con la opción de abrir el archivo
  exportado directamente (con el programa predeterminado del sistema).
- **Nombre de archivo por defecto**: los archivos exportados ahora se
  llaman `DataClock_AAAAMMDD_HHMMSS` (fecha y hora actuales) en vez de
  `reloj_de_datos`, en los 3 formatos.
- **Versión en el título de la ventana**: ahora dice "Software de
  Análisis Temporal — Beta 0.1.2".

## Novedades de la ronda anterior

- **Corregido el bug de superposición en el Resumen General** (antes
  "Resumen Ejecutivo", ver más abajo): con varios análisis habilitados
  a la vez, las tarjetas y los mini-gráficos "Top 3" se pisaban entre
  sí. Se debía a dos causas: (1) el espacio no se repartía dinámicamente
  según cuántas tarjetas/análisis hubiera, y (2) al acortar nombres muy
  largos y parecidos (por ejemplo, dos dependencias que empiezan
  igual), matplotlib los trataba como la misma categoría y fusionaba
  sus barras. Se corrigieron ambas: el espacio ahora se calcula
  dinámicamente (y las fuentes se achican solas si hace falta), y las
  barras usan posiciones numéricas en vez de las etiquetas como
  categoría. Probado con 1 y con los 4 análisis habilitados a la vez.
- **Renombrado**: "Resumen Ejecutivo" ahora se llama **"Resumen
  General"** en toda la app (checkbox, título de la página, hoja de
  Excel), en los 3 idiomas.

## Novedades de la ronda anterior

- **Resumen ejecutivo (opcional)**: nueva casilla en Configuración,
  "Generar resumen ejecutivo". Si se activa, se agrega como última
  hoja del informe (PDF, PNG y una hoja extra en el Excel) con:
  tarjetas de indicadores clave (eventos analizados, día/hora/franja
  pico, y el principal de cada análisis habilitado — modalidad,
  delito, dependencia, zona), los gráficos por franja horaria y por
  día de la semana, y un **Top 3** de cada análisis de conteo
  habilitado. Usa el mismo encabezado y pie de página que el resto del
  informe (mismo título, mismas estadísticas, mismo "Página X de Y").

## Novedades de la ronda anterior

- **Barra lateral de navegación con scroll**: cada pestaña (Importar,
  Columnas, Filtros, Configuración, Resultados) ahora tiene su propia
  barra de desplazamiento. Antes, si la ventana era chica o una
  pestaña tenía muchos controles (como Configuración con varios
  análisis habilitados), el contenido se cortaba o se superponía sin
  forma de verlo completo; ahora simplemente aparece un scroll.
- **Corregida la proporción del gráfico "por día"**: se veía
  demasiado alto y angosto ("estirado"); ahora tiene una proporción de
  gráfico de barras convencional.
- **Más espacio para etiquetas largas en los rankings**: el margen
  izquierdo del gráfico de cada análisis (modalidades, delitos,
  dependencia) ahora se ajusta automáticamente al largo real de los
  nombres. Zona, que tiene etiquetas cortas, sigue igual que antes.

## Novedades de la ronda anterior

- **Botón "Generar Análisis"** en la pestaña Configuración: ahora más
  grande y ubicado abajo a la derecha.
- **Color del Reloj de Datos elegible**: además del rojo por defecto,
  se puede elegir azul, verde, naranja, morado, gris o turquesa —
  afecta la matriz, el bloque de franjas y el gráfico por franja
  horaria, tanto en pantalla como en PDF/PNG/Excel.
- **Corregido el layout de la página "por día"** cuando no hay ningún
  análisis opcional habilitado: antes dejaba un hueco enorme y vacío;
  ahora el gráfico ocupa la mayor parte de la hoja, centrado.
- **Github como hipervínculo** en el diálogo "Acerca de" (antes era
  texto plano).
- **Formato de fecha/hora manual**: en la pestaña "2. Columnas" se
  puede tildar "Elegir manualmente la configuración de fecha y hora" y
  elegir, de una lista con varios formatos (AAAA-MM-DD, DD/MM/AAAA,
  con AM/PM, etc.), el formato exacto de fecha y de hora del archivo.
  Se prueba antes que la detección automática, para los casos en que
  esta última no da con el formato real de un archivo en particular.

## Novedades de la ronda anterior

- **Corregida la superposición de texto** en las páginas de ranking:
  ahora cada análisis de conteo (modalidades, delitos, dependencia,
  zona) tiene su **propia página**, con la tabla arriba y el gráfico
  abajo (apilados, no lado a lado), cada uno con toda una franja de la
  hoja para sí. La cantidad de páginas del informe ahora es variable
  (2 como mínimo: reloj + día; una más por cada análisis habilitado).
- El gráfico "Frecuencia por franja horaria" pasó a la página 1, junto
  al Reloj de Datos (aprovechando el espacio que la matriz deja libre).
- **Dos análisis nuevos**: "Análisis por dependencia policial" y
  "Análisis por zona" (misma lógica que Modalidades/Delitos, usando la
  columna ya mapeada en el paso 2).
- **Soporte de idioma portugués**, además de español e inglés.
- **El idioma elegido queda guardado**: la próxima vez que abrís el
  programa, arranca en el mismo idioma (usa QSettings de Qt; en
  Windows va al Registro, en Linux a un .ini en `~/.config/`).
- **Nombre de la aplicación**: ahora es simplemente "Software de
  Análisis Temporal" (la versión "Beta 0.1.2" quedó solo en el diálogo
  "Acerca de", no en el nombre).
- Se sacó **"ID del evento"** de las columnas obligatorias (no se
  usaba en ningún análisis).

## Cambios de esta versión (Beta 0.1.2)

- **Corregido el bug de "excluidos por 24hs" mal contado**: antes se
  calculaba sobre el archivo completo, antes de aplicar los filtros.
  Ahora se calcula DESPUÉS de filtrar, así que "eventos analizados" +
  "excluidos por superar 24 hs" siempre suman exactamente el total de
  registros que cumplen los filtros elegidos (verificado contra un
  conteo manual en Excel).
- **El PDF/pantalla ahora también muestra qué filtros se aplicaron**
  (por ejemplo "Filtros aplicados: DELITOCOP: ROBO"), debajo de
  "Eventos analizados / Excluidos". Si no se aplicó ningún filtro, esa
  línea no aparece.
- **Corregida la matriz "rota" de la página 1**: en pantalla, el canvas
  ahora tiene un tamaño FIJO (igual que el PDF exportado) en vez de
  estirarse o achicarse según el ancho de la ventana — eso era lo que
  deformaba y superponía los números.
- **Columnas**: todas son obligatorias ahora (fecha/hora de inicio y
  fin, ID del evento, dependencia, modalidad, zona, DelitoCOP) y se
  sacó "Tipo de delito".
- **Soporte para archivos DBF** (.dbf) además de Excel y CSV, con un
  lector propio sin dependencias externas nuevas.
- Firma al pie de las exportaciones más corta (sin la línea de la
  sección/dependencia).
- "Acerca de" ahora termina con "Policía de la Provincia de Buenos
  Aires, 2026." (se sacó el "2026" que estaba antes, junto a los
  créditos).
- Versión: Beta 0.1.2.

## Cambios de la versión anterior (Beta 1.0)

- **Soporte de idioma español/inglés**: menú "Idioma" en la barra
  superior. Cambiar el idioma traduce al instante toda la interfaz y,
  si ya había un análisis generado, también lo vuelve a mostrar
  traducido (sin perder los datos ni tener que generar de nuevo). Los
  informes exportados (PDF, PNG, Excel) también salen en el idioma
  activo al momento de exportar.
- **Informe de 2 páginas**: página 1 = el Reloj de Datos con las
  franjas horarias integradas (disposición siempre igual, así nunca se
  ven celdas "estiradas" tengas o no habilitados los análisis
  opcionales); página 2 = los gráficos y los rankings, con mucho más
  espacio para que los nombres de modalidades/delitos no queden
  cortados. Ambas páginas llevan número de página ("Página X de Y") y
  la firma del software al pie. La exportación a PNG genera 2 archivos
  (uno por página); la de Excel numera sus hojas.
- **Franjas horarias con hora de inicio configurable**: además de
  elegir 2/3/4 franjas, ahora se elige desde qué hora arranca la
  primera (por defecto 00:00). Por ejemplo, con hora de inicio 07:00 y
  2 franjas, quedan "07:00 a 18:59" y "19:00 a 06:59". El Reloj de
  Datos en sí (la matriz de 00 a 23) nunca cambia de disposición por
  esto: solo lo hacen las sumatorias por franja (que se dibujan
  partidas en 2 tramos si cruzan la medianoche) y los gráficos.
- **Análisis de Modalidades y de Delitos ya no piden la columna de
  nuevo**: usan directamente lo que se mapeó en la pestaña
  "2. Columnas" (Modalidad / DelitoCOP). Se sacó "Observaciones" del
  mapeo (ya no se usa) y se renombró "Delito" a "DelitoCOP".
- **Filtros por columna**: siguen siendo 3 filtros fijos e
  independientes (Filtro 1, 2, 3), cada uno con su propia columna y
  lista de valores, combinables entre sí sin pisarse.
- Botón "Generar Análisis" también en la pestaña "4. Configuración", y
  botón "Exportar a PDF" en "5. Resultados", además del menú superior
  (con "Generar Análisis" antes que "Exportar", y "Generar Análisis" /
  "Acerca de" como acciones directas de un clic, sin desplegable).


- **Nombre de la aplicación**: "Software de Análisis Temporal y de Datos Beta 1.0".
- **Ícono propio**: un reloj con una cuña roja (el mismo lenguaje visual
  del gradiente de color del Reloj de Datos), en `reloj_datos/assets/`.
- **Menú convencional** en la parte superior: Archivo (Abrir, Cerrar
  análisis, Salir), **Generar Análisis** (acción directa, un clic la
  ejecuta), Exportar (Excel, PDF, PNG) y **Acerca de** (acción directa
  que muestra los créditos del software).
- Las pestañas del flujo de trabajo (Importar / Columnas / Filtros /
  Configuración / Resultados) se muestran **verticales**, a la
  izquierda de la pantalla, con el texto siempre horizontal (barra de
  navegación propia, no la QTabBar nativa de Qt: rotar texto sobre esa
  barra depende de trucos de bajo nivel que se comportan distinto según
  el tema visual del sistema y podían romperse por completo).
- La pestaña **Resultados queda deshabilitada** hasta que se genera el
  análisis por primera vez.
- Botón **"⏱ Generar Análisis"** también disponible al pie de la pestaña
  "4. Configuración", y botón **"Exportar a PDF"** directo en la pestaña
  "5. Resultados" (además del menú Exportar).
- **Subtítulo manual** (además del título), configurable en la pestaña
  "4. Configuración".
- Se sacó la sección "Otras columnas a conservar" del mapeo de columnas
  (Sección 2.2): ya no es necesaria.
- **Filtros por columna**: ahora son 3 filtros fijos e independientes
  (Filtro 1, Filtro 2, Filtro 3), cada uno con su propia columna y su
  propia lista de valores — se pueden combinar los 3 al mismo tiempo
  (por ejemplo, modalidad + dependencia + delito) sin que uno pise al
  otro. Al elegir una columna, todos sus valores aparecen tildados por
  defecto.
- **Análisis de Delitos** (opcional, igual que el de Modalidades pero
  sin separador, ya que esa columna no combina valores en una misma
  celda): elegís la columna (por ejemplo `DELITOCOP`) y la cantidad a
  graficar. Se puede tener modalidades y delitos habilitados al mismo
  tiempo; cada uno agrega su propia tabla y gráfico de ranking, y su
  propia hoja en el Excel exportado.
- Las exportaciones (pantalla, PDF, PNG, Excel) muestran también la
  **cantidad de eventos analizados** y **cuántos se excluyeron por
  superar las 24 hs de duración**.
- **Firma del software** al pie de cada archivo exportado (PDF, PNG y
  Excel): *"Software de Análisis Temporal. Powered by Juan Jose Chaparro
  Dev & Claude AI. Sección Ce.P.A.I.D. E.P.S.D. Bahía Blanca."*
- **Hoja A4 vertical** (antes apaisada) para PDF, PNG y pantalla, con
  las tipografías de la matriz ajustadas al ancho más angosto.
- Corregido el error de exportación a PDF: cada exportación regenera
  una figura nueva (en vez de reutilizar la que ya está embebida en la
  pantalla de resultados) y adjunta explícitamente el canvas de
  matplotlib correspondiente (Agg para PNG, PDF para PDF) antes de
  guardar, evitando conflictos con el backend interactivo de Qt.
- Corregidos los gráficos de barras (por franja horaria, por día y de
  modalidades/delitos), que se veían demasiado anchos o se superponían
  con muchas filas de ranking: ahora tienen ancho fijo, quedan
  centrados y la tabla de ranking queda confinada a su propio espacio.

## ¿Por qué Python?

- **Multiplataforma real**: el mismo código corre en Windows y en cualquier
  distro basada en Debian sin cambios, y se empaqueta como ejecutable nativo
  para cada sistema con PyInstaller (no requiere que el usuario final instale
  Python).
- **Librerías maduras para exactamente este problema**: `pandas` para leer
  Excel/CSV, `openpyxl` para exportar Excel con colores, `reportlab` para
  PDF, `matplotlib` para los gráficos, y `PySide6` (Qt) para una interfaz
  gráfica profesional e idéntica en ambos sistemas operativos.
- Es la combinación estándar en la industria para este tipo de herramientas
  de escritorio para análisis de datos.

## Estructura del proyecto (clases)

```
reloj_datos/
├── main.py                          # Punto de entrada
├── requirements.txt
├── build_windows.bat                # Generar .exe
├── build_linux.sh                   # Generar binario Linux
└── reloj_datos/
    ├── branding.py                  # Nombre de la app, firma y créditos
    ├── resources.py                 # Rutas al ícono (dev y empaquetado)
    ├── settings.py                  # Persistencia del idioma elegido (QSettings)
    ├── config_profile.py            # Guardar/cargar configuración completa (.json)
    ├── assets/
    │   ├── icon.png                 # Ícono para Linux / dentro de la app
    │   └── icon.ico                 # Ícono para Windows
    ├── models/
    │   └── event.py                 # Event: un registro/evento
    ├── data/
    │   ├── importer.py              # DataImporter (Sección 2.1)
    │   ├── column_mapping.py        # ColumnMapping, EventBuilder (Sección 2.2)
    │   └── filters.py               # EventFilter (Sección 3)
    ├── processing/
    │   ├── time_distributor.py      # TimeDistributor (Sección 4)
    │   ├── reloj_matrix.py          # RelojMatrix (Secciones 5 y 7)
    │   ├── franjas_horarias.py      # FranjaHoraria (Sección 7.3)
    │   ├── color_scale.py           # ColorScale (Sección 6)
    │   ├── modalidad_analyzer.py    # ModalidadAnalyzer (Sección 8.4)
    │   └── chart_generator.py       # ChartGenerator (Sección 8)
    ├── export/
    │   ├── excel_exporter.py        # ExcelExporter (Sección 9)
    │   ├── pdf_exporter.py          # PDFExporter (Sección 9)
    │   └── image_exporter.py        # ImageExporter (Sección 9)
    └── gui/
        ├── main_window.py           # Ventana principal (orquesta todo)
        ├── import_widget.py         # Pestaña 1: Importar
        ├── mapping_widget.py        # Pestaña 2: Columnas
        ├── filter_widget.py         # Pestaña 3: Filtros
        ├── config_widget.py         # Pestaña 4: Configuración
        ├── results_widget.py        # Pestaña 5: Resultados
        ├── matrix_table_widget.py   # Tabla coloreada del Reloj de Datos
        └── chart_canvas.py          # Embebido de gráficos matplotlib en Qt
```

Cada clase corresponde 1 a 1 con una sección del documento de requerimiento,
lo que permite mantener y extender el sistema sin tocar las demás partes.

### Cobertura del requerimiento

| Sección del PDF | Clase(s) responsable(s) |
|---|---|
| 2.1 Importación | `DataImporter` |
| 2.2 Selección de columnas | `ColumnMapping`, `EventBuilder`, `MappingWidget` |
| 3 Filtros | `EventFilter`, `FilterWidget` |
| 4 Procesamiento (incl. cruce de medianoche y fracciones de hora) | `TimeDistributor` |
| 5 Generación del Reloj de Datos | `RelojMatrix` |
| 6 Colores automáticos | `ColorScale` |
| 7 Totales (día / hora / franja configurable) | `RelojMatrix`, `FranjaHoraria` |
| 8 Gráficos automáticos + Análisis de modalidades | `ChartGenerator`, `ModalidadAnalyzer` |
| 9 Exportación (Excel/PDF/PNG) | `ExcelExporter`, `PDFExporter`, `ImageExporter` |
| 10 Reglas de cálculo | Verificado con los ejemplos exactos del PDF (ver más abajo) |

Las funcionalidades opcionales de la Sección 14 (comparación entre períodos,
dashboard interactivo, estadísticas descriptivas, etc.) **no están incluidas
en esta primera versión** porque el propio documento las marca como
sugerencias opcionales; si las necesitás, decime cuáles priorizar y las
agrego sobre esta misma base.

### Formatos de fecha/hora aceptados en la importación

El parseo separa explícitamente la parte de **fecha** y la de **hora** de
cada columna antes de combinarlas, así que funciona tanto si tenés columnas
de fecha "limpias" (`2026-09-01`) como si tu fecha ya viene con la hora en
cero (`2026-09-01 00:00:00`) y la hora real está en otra columna aparte
(`10:00:00`), que es un formato muy habitual en exportaciones policiales.

Además:
- Si usás **la misma columna** de fecha para inicio y para fin, y la hora
  de fin es *menor* a la de inicio, el sistema asume que el evento cruzó
  la medianoche y le suma un día a la fecha de fin automáticamente.
- Si la hora de inicio y la de fin son **iguales**, se interpreta como un
  **evento puntual** (solo se conoce el momento del hecho) y cuenta como
  **1 ocurrencia** en esa hora — no como una duración de 24 hs ni de 0.

### Regla de cálculo horario (definida por el usuario)

Cada evento aporta un total de **1 ocurrencia** al Reloj de Datos:

- **Evento puntual** (fecha/hora de inicio y fin iguales): el 1 se asigna
  completo a esa hora. Ejemplo: un hecho a las 12:00 → suma 1 a la celda
  de las 12:00.
- **Evento con duración**: el 1 se reparte proporcionalmente entre las
  horas de reloj que involucra, según el tiempo real ocupado en cada una.
  Ejemplo: un evento de 11:20 a 12:40 (40 min en la hora 11 + 40 min en
  la hora 12, sobre 80 min totales) reparte 0,5 a las 11hs y 0,5 a las
  12hs.

> Nota: esto reemplaza el criterio de "valor = horas de duración" que
> traía el documento de requerimiento original (donde 10:00-13:00 daba
> 1,1,1). Con la regla nueva, ese mismo evento reparte 0,33 en cada una
> de las 3 horas, porque el total del evento siempre suma 1.

### Colores automáticos (gradiente continuo)

En vez de 3 niveles fijos (sin color / amarillo / rojo), el reloj usa una
escala continua: blanco para las horas de menor frecuencia y un rojo cada
vez más intenso para las de mayor frecuencia. La matriz principal, los
totales por día, los totales por hora y los totales por franja horaria
tienen cada uno su propia escala (relativa a sus propios valores mínimo y
máximo), igual que en una planilla de Excel con formato condicional.

### Título y rango de fechas

El título que se muestra arriba del Reloj de Datos es configurable desde
la pestaña "4. Configuración". Debajo del título aparece automáticamente
una descripción del período efectivamente analizado (calculada a partir
del rango real de fecha/hora de los eventos que entraron al cálculo,
luego de aplicar los filtros).

### Pantalla única y PDF de una sola hoja

El Reloj de Datos (con las franjas horarias integradas debajo, igual que
en una planilla de Excel con esa distribución), el gráfico por franja
horaria, el gráfico por día de la semana y -si está habilitado- el
ranking de modalidades con su gráfico, se muestran todos juntos en una
única pantalla de resultados. La exportación a PDF reutiliza exactamente
esa misma composición y la ajusta a una sola hoja A4 apaisada.

La lógica de distribución horaria fue verificada contra los ejemplos
exactos del documento (10:00-13:00 → 1,1,1 · 08:30-11:30 → 0.5,1,1,0.5 ·
cruce de medianoche lunes 22:00 a martes 03:00) y contra un caso completo
de principio a fin (importar → mapear → filtrar → generar → exportar a
Excel y PDF), todo dando el resultado esperado.

---

## 1. Instalación (modo desarrollo, para probar o modificar el código)

### En Windows

1. Instalar **Python 3.11 o superior** desde https://python.org (marcar la
   casilla "Add Python to PATH" durante la instalación).
2. Abrir la carpeta del proyecto y ejecutar en una terminal (CMD o
   PowerShell):
   ```bat
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   python main.py
   ```

### En Linux (Debian / Ubuntu y derivados)

1. Instalar Python y las dependencias del sistema para Qt:
   ```bash
   sudo apt update
   sudo apt install python3 python3-venv python3-pip libgl1
   ```
2. Crear el entorno virtual e instalar las dependencias:
   ```bash
   cd reloj_datos
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

---

## 2. Generar el ejecutable instalable (sin necesidad de Python en la PC destino)

El proyecto usa **PyInstaller** para empaquetar la app como un ejecutable
autónomo. Hay que compilar **en cada sistema operativo destino** (no se
puede generar el `.exe` de Windows desde Linux ni viceversa sin
máquinas virtuales o *cross-compilation*, que no es recomendable para
apps con interfaz gráfica).

### Generar el `.exe` en Windows

Doble clic en `build_windows.bat`, o desde la terminal:
```bat
build_windows.bat
```
El resultado queda en `dist\RelojDeDatos\RelojDeDatos.exe`. Se puede
copiar toda la carpeta `dist\RelojDeDatos` a cualquier PC con Windows
10/11 (64 bits) sin necesidad de instalar Python ahí.

### Generar el binario en Linux / Debian

```bash
chmod +x build_linux.sh
./build_linux.sh
```
El resultado queda en `dist/RelojDeDatos/RelojDeDatos`. Se puede copiar
la carpeta `dist/RelojDeDatos` a cualquier equipo Debian/Ubuntu de la
misma arquitectura (por ejemplo, 64 bits) sin instalar Python.

> Tip: si querés un instalador "de verdad" (con ícono en el menú, acceso
> directo, desinstalador), en Windows se puede envolver la carpeta
> `dist\RelojDeDatos` con **Inno Setup**, y en Debian se puede armar un
> paquete `.deb` con `dpkg-deb` a partir de esa misma carpeta. Si querés,
> te preparo esos empaquetados también.

---

## 3. Uso de la aplicación

1. **Pestaña "1. Importar"**: elegí el archivo Excel (.xlsx/.xls) o CSV.
   Verás una vista previa de los primeros registros.
2. **Pestaña "2. Columnas"**: indicá qué columna del archivo corresponde a
   fecha/hora de inicio y fin (obligatorias), y opcionalmente
   dependencia, modalidad, zona, delito, observaciones, etc.
3. **Pestaña "3. Filtros"**: opcionalmente, activá un rango de fecha/hora
   y/o filtrá por los valores de cualquier columna.
4. **Pestaña "4. Configuración"**: elegí en cuántas franjas horarias
   agrupar el día (4/3/2) y, si querés, activá el análisis de
   modalidades indicando la columna y el separador (por defecto `,`).
5. Hacé clic en **"⏱ Generar Reloj de Datos"**: se abre la pestaña
   "5. Resultados" con la matriz coloreada, los gráficos por franja y
   por día, y (si corresponde) el ranking de modalidades.
6. Usá los botones **"Exportar a Excel"**, **"Exportar a PDF"** o
   **"Exportar gráficos a PNG"** de la barra superior para guardar los
   resultados.

---

## 4. Próximos pasos sugeridos

- Empaquetar como `.deb` / instalador `.exe` con ícono propio.
- Sumar las funcionalidades opcionales de la Sección 14 que más te
  sirvan (comparación entre períodos, tendencias mensuales, guardado
  de configuraciones favoritas, etc.).
- Tests automatizados (`pytest`) sobre las clases de `processing/` para
  blindar la lógica de cálculo ante futuros cambios.
