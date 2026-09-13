#!/bin/bash
# =========================================================
#  Build de "Software de Analisis Temporal" para
#  Linux / Debian (ejecutar en Linux)
# =========================================================
set -e

echo "Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

echo "Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo "Generando ejecutable..."
# No se usa --collect-all PySide6: esta app solo usa QtWidgets/QtGui/
# QtCore (nunca QML/Qt Quick), asi que ese flag empaquetaba modulos
# enteros sin usar (Qt3D, QML, WebEngine, Multimedia, etc.), haciendo
# el ejecutable mucho mas pesado de lo necesario.
pyinstaller --noconfirm --windowed --name "SoftwareAnalisisTemporal" \
    --add-data "reloj_datos/assets:reloj_datos/assets" \
    --exclude-module PySide6.Qt3DAnimation \
    --exclude-module PySide6.Qt3DCore \
    --exclude-module PySide6.Qt3DExtras \
    --exclude-module PySide6.Qt3DInput \
    --exclude-module PySide6.Qt3DLogic \
    --exclude-module PySide6.Qt3DRender \
    --exclude-module PySide6.QtQml \
    --exclude-module PySide6.QtQuick \
    --exclude-module PySide6.QtQuick3D \
    --exclude-module PySide6.QtQuickWidgets \
    --exclude-module PySide6.QtQuickControls2 \
    --exclude-module PySide6.QtWebEngineCore \
    --exclude-module PySide6.QtWebEngineWidgets \
    --exclude-module PySide6.QtWebEngineQuick \
    --exclude-module PySide6.QtMultimedia \
    --exclude-module PySide6.QtMultimediaWidgets \
    --exclude-module PySide6.QtBluetooth \
    --exclude-module PySide6.QtNfc \
    --exclude-module PySide6.QtPositioning \
    --exclude-module PySide6.QtSensors \
    --exclude-module PySide6.QtSerialPort \
    --exclude-module PySide6.QtPdf \
    --exclude-module PySide6.QtPdfWidgets \
    main.py

echo ""
echo "Listo. El ejecutable quedo en dist/SoftwareAnalisisTemporal/SoftwareAnalisisTemporal"
echo "Tip: el icono para el menu de aplicaciones esta en reloj_datos/assets/icon.png,"
echo "usalo en un archivo .desktop si queres un acceso directo con icono."
