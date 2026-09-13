@echo off
REM =========================================================
REM  Build de "Software de Analisis Temporal y de Datos" para
REM  Windows (ejecutar en Windows)
REM =========================================================

echo Instalando dependencias...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

echo Generando ejecutable...
pyinstaller --noconfirm --windowed --name "SoftwareAnalisisTemporal" ^
    --icon "reloj_datos\assets\icon.ico" ^
    --add-data "reloj_datos\assets;reloj_datos\assets" ^
    --collect-all PySide6 ^
    main.py

echo.
echo Listo. El ejecutable quedo en dist\SoftwareAnalisisTemporal\SoftwareAnalisisTemporal.exe
pause
