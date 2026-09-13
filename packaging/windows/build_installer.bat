@echo off
REM ============================================================
REM  Genera el instalador .exe completo:
REM   1) Compila la app con PyInstaller (carpeta dist\...)
REM   2) Empaqueta esa carpeta en un instalador con Inno Setup
REM  Ejecutar en Windows, desde esta misma carpeta
REM  (packaging\windows), con Inno Setup ya instalado
REM  (https://jrsoftware.org/isdl.php).
REM ============================================================
setlocal

cd /d "%~dp0..\.."

echo === Paso 1/2: compilando con PyInstaller ===
call build_windows.bat
if errorlevel 1 (
    echo Fallo la compilacion con PyInstaller.
    exit /b 1
)

echo.
echo === Paso 2/2: generando el instalador con Inno Setup ===

REM Busca ISCC.exe (el compilador de Inno Setup) en las ubicaciones
REM tipicas; si lo tenes en otro lado, ajusta esta linea.
set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
    echo No se encontro Inno Setup ^(ISCC.exe^). Instalalo desde:
    echo   https://jrsoftware.org/isdl.php
    exit /b 1
)

REM Lee la version actual desde branding.py para que el instalador
REM siempre quede con el mismo numero que la app.
for /f "delims=" %%v in ('python -c "from reloj_datos.branding import VERSION_APP; print(VERSION_APP.replace('Beta ', ''))"') do set APP_VERSION=%%v

"%ISCC%" /DMyAppVersion="%APP_VERSION%" "packaging\windows\installer.iss"
if errorlevel 1 (
    echo Fallo la generacion del instalador.
    exit /b 1
)

echo.
echo Listo. El instalador quedo en packaging\windows\output\SoftwareAnalisisTemporal-Setup.exe
pause
