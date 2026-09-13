#!/bin/bash
# =========================================================
#  Build de "Software de Analisis Temporal y de Datos" para
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
pyinstaller --noconfirm --windowed --name "SoftwareAnalisisTemporal" \
    --add-data "reloj_datos/assets:reloj_datos/assets" \
    --collect-all PySide6 \
    main.py

echo ""
echo "Listo. El ejecutable quedo en dist/SoftwareAnalisisTemporal/SoftwareAnalisisTemporal"
echo "Tip: el icono para el menu de aplicaciones esta en reloj_datos/assets/icon.png,"
echo "usalo en un archivo .desktop si queres un acceso directo con icono."
