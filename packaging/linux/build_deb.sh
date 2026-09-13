#!/bin/bash
# ============================================================
#  Genera el paquete .deb completo:
#   1) Compila la app con PyInstaller (carpeta dist/...)
#   2) Arma el árbol de directorios estilo Debian y lo empaqueta
#      con dpkg-deb
#  Ejecutar en Linux (Debian/Ubuntu y derivados), desde esta
#  misma carpeta (packaging/linux).
# ============================================================
set -e

cd "$(dirname "$0")/../.."
RAIZ_PROYECTO="$(pwd)"
NOMBRE_PKG="software-analisis-temporal"
VERSION="$(python3 -c "from reloj_datos.branding import VERSION_APP; print(VERSION_APP.replace('Beta ', ''))")"
ARQUITECTURA="amd64"

echo "=== Paso 1/2: compilando con PyInstaller ==="
bash build_linux.sh

DIST_DIR="$RAIZ_PROYECTO/dist/SoftwareAnalisisTemporal"
if [ ! -d "$DIST_DIR" ]; then
    echo "No se encontró $DIST_DIR (¿falló el build de PyInstaller?)."
    exit 1
fi

echo ""
echo "=== Paso 2/2: armando el paquete .deb ==="

CARPETA_BUILD="$RAIZ_PROYECTO/packaging/linux/build/${NOMBRE_PKG}_${VERSION}"
rm -rf "$CARPETA_BUILD"

# --- Estructura del paquete ---
mkdir -p "$CARPETA_BUILD/DEBIAN"
mkdir -p "$CARPETA_BUILD/opt/${NOMBRE_PKG}"
mkdir -p "$CARPETA_BUILD/usr/share/applications"
mkdir -p "$CARPETA_BUILD/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$CARPETA_BUILD/usr/bin"

# El binario compilado y todas sus dependencias van a /opt/<pkg>/
cp -r "$DIST_DIR"/* "$CARPETA_BUILD/opt/${NOMBRE_PKG}/"

# Ícono y entrada de menú
cp "$RAIZ_PROYECTO/reloj_datos/assets/icon.png" \
   "$CARPETA_BUILD/usr/share/icons/hicolor/256x256/apps/${NOMBRE_PKG}.png"
cp "$RAIZ_PROYECTO/packaging/linux/${NOMBRE_PKG}.desktop" \
   "$CARPETA_BUILD/usr/share/applications/${NOMBRE_PKG}.desktop"

# Lanzador en /usr/bin para poder ejecutarlo también desde una terminal
ln -sf "/opt/${NOMBRE_PKG}/SoftwareAnalisisTemporal" \
   "$CARPETA_BUILD/usr/bin/${NOMBRE_PKG}"

# --- Archivo de control ---
TAMANIO_KB=$(du -sk "$CARPETA_BUILD/opt/${NOMBRE_PKG}" | cut -f1)
cat > "$CARPETA_BUILD/DEBIAN/control" << EOF
Package: ${NOMBRE_PKG}
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARQUITECTURA}
Installed-Size: ${TAMANIO_KB}
Maintainer: Juan Jose Chaparro <https://github.com/<tu-usuario>>
Description: Software de Análisis Temporal (Reloj de Datos)
 Analiza la distribución horaria de eventos a partir de una planilla
 de datos (Excel, CSV o DBF) y genera el "Reloj de Datos": una matriz
 de 7 dias x 24 horas coloreada segun la frecuencia de eventos, mas
 analisis de conteo por modalidad, delito, dependencia y zona.
EOF

chmod 0755 "$CARPETA_BUILD/DEBIAN"
find "$CARPETA_BUILD/opt/${NOMBRE_PKG}" -type f -exec chmod 0644 {} \;
chmod 0755 "$CARPETA_BUILD/opt/${NOMBRE_PKG}/SoftwareAnalisisTemporal"
find "$CARPETA_BUILD/opt/${NOMBRE_PKG}" -type d -exec chmod 0755 {} \;

# --- Empaquetado final ---
CARPETA_SALIDA="$RAIZ_PROYECTO/packaging/linux/output"
mkdir -p "$CARPETA_SALIDA"
ARCHIVO_DEB="$CARPETA_SALIDA/${NOMBRE_PKG}_${VERSION}_${ARQUITECTURA}.deb"

dpkg-deb --build --root-owner-group "$CARPETA_BUILD" "$ARCHIVO_DEB"

echo ""
echo "Listo. El paquete quedó en $ARCHIVO_DEB"
echo "Instalar con: sudo apt install \"$ARCHIVO_DEB\""
