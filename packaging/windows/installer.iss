; ============================================================
;  Instalador de "Software de Analisis Temporal" para Windows
;  Se compila con Inno Setup (https://jrsoftware.org/isinfo.php),
;  a partir de la carpeta ya generada por PyInstaller en
;  dist\SoftwareAnalisisTemporal (ver build_installer.bat).
; ============================================================

#define MyAppName "Software de Analisis Temporal"
#ifndef MyAppVersion
  #define MyAppVersion "0.1.2"
#endif
#define MyAppPublisher "Juan Jose Chaparro"
#define MyAppURL "https://github.com/<tu-usuario>/<tu-repositorio>"
#define MyAppExeName "SoftwareAnalisisTemporal.exe"
#define MyDistDir "..\..\dist\SoftwareAnalisisTemporal"

[Setup]
AppId={{B6E5B6B4-6B8B-4C2E-9B7E-RELOJDEDATOS01}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
; El instalador se genera en packaging\windows\output\
OutputDir=output
OutputBaseFilename=SoftwareAnalisisTemporal-Setup
SetupIconFile=..\..\reloj_datos\assets\icon.ico
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
LicenseFile=..\..\LICENSE

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Copia TODO el contenido generado por PyInstaller (el .exe y sus
; dependencias) a la carpeta de instalación.
Source: "{#MyDistDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
