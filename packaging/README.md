# Compilar los instaladores

Los dos instaladores se generan **cada uno en su propio sistema operativo** (no se puede armar el
`.exe` desde Linux ni el `.deb` desde Windows sin máquinas virtuales, que no vale la pena para una
app de escritorio con interfaz gráfica).

## Windows — `SoftwareAnalisisTemporal-Setup.exe`

**Requisitos previos** (una sola vez):
1. Python 3.11+ instalado, con `pip install -r requirements.txt` ya corrido.
2. [Inno Setup 6](https://jrsoftware.org/isdl.php) instalado (es gratis).

**Generar el instalador:**
```bat
cd packaging\windows
build_installer.bat
```

Este script:
1. Corre `build_windows.bat` (PyInstaller), que compila la app a `dist\SoftwareAnalisisTemporal\`.
2. Compila `installer.iss` con Inno Setup, tomando la versión actual desde `branding.py`.

El instalador final queda en `packaging\windows\output\SoftwareAnalisisTemporal-Setup.exe`. Es un
instalador normal con asistente: acceso directo opcional en el escritorio, entrada en el menú
Inicio, desinstalador registrado en "Agregar o quitar programas".

> Si Inno Setup quedó instalado en una ruta distinta a las habituales, editá la línea `set "ISCC=..."`
> de `build_installer.bat` con la ruta correcta a `ISCC.exe`.

### Problema conocido: "El sistema no puede encontrar la ruta especificada"

Si `ISCC.exe` falla a mitad de la compresión con ese mensaje (suele pasar comprimiendo algún
archivo dentro de `_internal\PySide6\qml\...`), es el límite de **260 caracteres por ruta** de
Windows (`MAX_PATH`): la carpeta del proyecto está en una ruta muy larga (por ejemplo dentro de
`Escritorio\...`) y, sumada a las carpetas internas de PySide6, se pasa del límite.

Solución más simple: **mové la carpeta del proyecto a una ruta corta**, por ejemplo `C:\rdt\`, y
volvé a compilar desde ahí. El script de build ya excluye los módulos de PySide6 que esta app no
usa (QML, Qt3D, WebEngine, etc.), así que con una ruta corta no debería volver a pasar.

## Linux (Debian/Ubuntu y derivados) — `.deb`

**Requisitos previos** (una sola vez):
```bash
sudo apt install python3 python3-venv python3-pip dpkg-dev
```

**Generar el paquete:**
```bash
cd packaging/linux
chmod +x build_deb.sh
./build_deb.sh
```

Este script:
1. Corre `build_linux.sh` (PyInstaller), que compila la app a `dist/SoftwareAnalisisTemporal/`.
2. Arma el árbol de directorios estilo Debian (`/opt/software-analisis-temporal/`, entrada de menú
   en `/usr/share/applications/`, ícono, y un lanzador en `/usr/bin/`).
3. Empaqueta todo con `dpkg-deb --build --root-owner-group` (no hace falta `sudo` ni `fakeroot`).

El paquete final queda en `packaging/linux/output/software-analisis-temporal_<version>_amd64.deb`.
Se instala con:
```bash
sudo apt install ./software-analisis-temporal_<version>_amd64.deb
```
y queda disponible en el menú de aplicaciones, además de poder ejecutarse desde cualquier terminal
con el comando `software-analisis-temporal`.

## Publicar los instaladores en GitHub

Una vez generados ambos archivos, subilos a una **Release** del repositorio (no directamente al
código fuente): en GitHub, `Releases` → `Draft a new release` → arrastrar el `.exe` y el `.deb`
como *assets* de esa versión. Así quedan disponibles para descargar sin inflar el tamaño del
repositorio con binarios.
