@echo off
REM =========================================================
REM  Build de "Software de Analisis Temporal" para
REM  Windows (ejecutar en Windows)
REM =========================================================

echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo Generando ejecutable...
REM No se usa --collect-all PySide6: esta app solo usa QtWidgets/QtGui/
REM QtCore (nunca QML/Qt Quick), asi que ese flag empaquetaba modulos
REM enteros sin usar (Qt3D, QML, WebEngine, Multimedia, etc.) con
REM carpetas internas muy profundas que en Windows pueden superar el
REM limite de 260 caracteres por ruta (MAX_PATH) y hacer fallar tanto
REM a PyInstaller como al instalador de Inno Setup. Se excluyen ademas
REM explicitamente por si el hook automatico de PySide6 los llegara a
REM sumar igual.
pyinstaller --noconfirm --windowed --name "SoftwareAnalisisTemporal" ^
    --icon "reloj_datos\assets\icon.ico" ^
    --add-data "reloj_datos\assets;reloj_datos\assets" ^
    --exclude-module PySide6.Qt3DAnimation ^
    --exclude-module PySide6.Qt3DCore ^
    --exclude-module PySide6.Qt3DExtras ^
    --exclude-module PySide6.Qt3DInput ^
    --exclude-module PySide6.Qt3DLogic ^
    --exclude-module PySide6.Qt3DRender ^
    --exclude-module PySide6.QtQml ^
    --exclude-module PySide6.QtQuick ^
    --exclude-module PySide6.QtQuick3D ^
    --exclude-module PySide6.QtQuickWidgets ^
    --exclude-module PySide6.QtQuickControls2 ^
    --exclude-module PySide6.QtWebEngineCore ^
    --exclude-module PySide6.QtWebEngineWidgets ^
    --exclude-module PySide6.QtWebEngineQuick ^
    --exclude-module PySide6.QtMultimedia ^
    --exclude-module PySide6.QtMultimediaWidgets ^
    --exclude-module PySide6.QtBluetooth ^
    --exclude-module PySide6.QtNfc ^
    --exclude-module PySide6.QtPositioning ^
    --exclude-module PySide6.QtSensors ^
    --exclude-module PySide6.QtSerialPort ^
    --exclude-module PySide6.QtPdf ^
    --exclude-module PySide6.QtPdfWidgets ^
    main.py

echo.
echo Listo. El ejecutable quedo en dist\SoftwareAnalisisTemporal\SoftwareAnalisisTemporal.exe
pause
