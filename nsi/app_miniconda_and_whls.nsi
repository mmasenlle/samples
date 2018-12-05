; example1.nsi
;
; This script is perhaps one of the simplest NSIs you can make. All of the
; optional settings are left to their default settings. The installer simply 
; prompts the user asking them where to install, and drops a copy of example1.nsi
; there. 

;--------------------------------

; The name of the installer
Name "beckhoff_utils"

; The file to write
OutFile "beckhoff_utils.exe"

; The default installation directory
InstallDir C:\Lortek

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\beckhoff_utils" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------

; Pages

Page directory
Page instfiles

;--------------------------------

; The stuff to install
Section "" ;No components page, name is not important

  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  File /r beckhoff_utils_source\*
  
  # Start Menu
  createDirectory "$SMPROGRAMS\beckhxplorer"
  createShortCut "$SMPROGRAMS\beckhxplorer\beckhxplorer.lnk" "$INSTDIR\beckhxplorer\beckhxplorer.exe" "" "$INSTDIR\tc_ui\favicon.ico"
  
   ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\beckhoff_utils "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\beckhoff_utils" "DisplayName" "beckhoff_utils"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\beckhoff_utils" "DisplayVersion" "2.0.0.1"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\beckhoff_utils" "Publisher" "Lortek S.Coop"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\beckhoff_utils" "EstimatedSize" 50000
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\beckhoff_utils" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\beckhoff_utils" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\beckhoff_utils" "NoRepair" 1
  WriteUninstaller "uninstall.exe"
  
  # Install service
  nsExec::Exec '"$INSTDIR\tc_ui\tc_ui_srv.exe" install'
  
SectionEnd ; end the section


; Python 2.7
Section -Prerequisites
  SetOutPath $INSTDIR\Prerequisites
  MessageBox MB_YESNO "Install Miniconda2 x86_64?" /SD IDYES IDNO endActiveSync
    File "Prerequisites\Miniconda2-Windows-x86_64.exe"
    ExecWait "$INSTDIR\Prerequisites\Miniconda2-Windows-x86_64.exe"
    Goto endActiveSync
  endActiveSync:
  MessageBox MB_YESNO "Install python libraries?" /SD IDYES IDNO endpylibs
    File "Prerequisites\*.whl"
    # Install python libs (pip wheel <package>)
    nsExec::Exec '"C:\ProgramData\Miniconda2\Scripts\pip.exe" install "$INSTDIR\Prerequisites\pyads-3.0.5-py2-none-any.whl"'
    nsExec::Exec '"C:\ProgramData\Miniconda2\Scripts\pip.exe" install "$INSTDIR\Prerequisites\SimpleWebSocketServer-0.1.0-py2-none-any.whl"'
    nsExec::Exec '"C:\ProgramData\Miniconda2\Scripts\pip.exe" install "$INSTDIR\Prerequisites\xlwt-1.3.0-py2.py3-none-any.whl"'
    nsExec::Exec '"C:\ProgramData\Miniconda2\Scripts\pip.exe" install "$INSTDIR\Prerequisites\paho_mqtt-1.4.0-py2-none-any.whl"'
    nsExec::Exec '"C:\ProgramData\Miniconda2\Scripts\pip.exe" install "$INSTDIR\Prerequisites\mysql_connector-2.1.6-cp27-cp27m-win_amd64.whl"'
    Goto endpylibs
  endpylibs:
  RMDir /r "$INSTDIR\Prerequisites"
SectionEnd

Section "Start service"
  nsExec::Exec '"$INSTDIR\tc_ui\tc_ui_srv.exe" start'
SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"

  # Stop and uninstall service
  nsExec::Exec '"$INSTDIR\tc_ui\tc_ui_srv.exe" stop'
  nsExec::Exec '"$INSTDIR\tc_ui\tc_ui_srv.exe" uninstall'

  # Remove Start Menu launcher
  delete "$SMPROGRAMS\beckhxplorer\beckhxplorer.lnk"
  # Try to remove the Start Menu folder - this will only happen if it is empty
  rmDir "$SMPROGRAMS\beckhxplorer"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\beckhoff_utils"
  DeleteRegKey HKLM SOFTWARE\beckhoff_utils

  ; Remove directories used
  RMDir /r "$INSTDIR"

SectionEnd
