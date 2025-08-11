; 勤怠管理ツール NSIS インストーラースクリプト
; NSISで実行可能インストーラーを作成

!define APP_NAME "Attendance Tool"
!define APP_VERSION "0.1.0"
!define APP_PUBLISHER "Attendance Tool Development Team"
!define APP_URL "https://github.com/attendance-tool"
!define APP_DESCRIPTION "勤怠データのCSV自動集計・レポート生成ツール"

; 基本設定
Name "${APP_NAME}"
OutFile "dist\AttendanceTool-${APP_VERSION}-Setup.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "InstallPath"
RequestExecutionLevel admin

; 外観設定
!include "MUI2.nsh"
!define MUI_ABORTWARNING

; インストーラーページ
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

; アンインストーラーページ
!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

; 言語設定
!insertmacro MUI_LANGUAGE "Japanese"
!insertmacro MUI_LANGUAGE "English"

; バージョン情報
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey /LANG=${LANG_JAPANESE} "ProductName" "${APP_NAME}"
VIAddVersionKey /LANG=${LANG_JAPANESE} "Comments" "${APP_DESCRIPTION}"
VIAddVersionKey /LANG=${LANG_JAPANESE} "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_JAPANESE} "LegalTrademarks" ""
VIAddVersionKey /LANG=${LANG_JAPANESE} "LegalCopyright" "© 2024 ${APP_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_JAPANESE} "FileDescription" "${APP_DESCRIPTION}"
VIAddVersionKey /LANG=${LANG_JAPANESE} "FileVersion" "${APP_VERSION}"
VIAddVersionKey /LANG=${LANG_JAPANESE} "ProductVersion" "${APP_VERSION}"

; インストール処理
Section "Main Application" SecMain
    SetOutPath "$INSTDIR"
    
    ; 実行ファイルをコピー
    File "dist\attendance-tool-cli.exe"
    File "dist\attendance-tool-gui.exe"
    
    ; ドキュメントファイルをコピー
    File "dist\README.md"
    File "dist\VERSION.txt"
    
    ; 設定サンプルをコピー
    SetOutPath "$INSTDIR\config_samples"
    File /r "dist\config_samples\*"
    
    ; レジストリに登録
    WriteRegStr HKLM "Software\${APP_NAME}" "InstallPath" "$INSTDIR"
    WriteRegStr HKLM "Software\${APP_NAME}" "Version" "${APP_VERSION}"
    
    ; アンインストール情報をレジストリに登録
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" "$INSTDIR\uninstall.exe"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_URL}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" "$INSTDIR\attendance-tool-gui.exe"
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
    
    ; スタートメニューショートカットを作成
    CreateDirectory "$SMPROGRAMS\${APP_NAME}"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME} (GUI).lnk" "$INSTDIR\attendance-tool-gui.exe"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\${APP_NAME} (CLI).lnk" "$INSTDIR\attendance-tool-cli.exe"
    CreateShortCut "$SMPROGRAMS\${APP_NAME}\アンインストール.lnk" "$INSTDIR\uninstall.exe"
    
    ; デスクトップショートカット（オプション）
    CreateShortCut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\attendance-tool-gui.exe"
    
    ; アンインストーラーを作成
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; パス環境変数に追加（オプション）
    ; EnVar::SetHKLM
    ; EnVar::AddValue "PATH" "$INSTDIR"
    ; Pop $0
    
SectionEnd

; アンインストール処理
Section "Uninstall"
    ; ファイル削除
    Delete "$INSTDIR\attendance-tool-cli.exe"
    Delete "$INSTDIR\attendance-tool-gui.exe"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\VERSION.txt"
    Delete "$INSTDIR\uninstall.exe"
    
    ; 設定サンプル削除
    RMDir /r "$INSTDIR\config_samples"
    
    ; ディレクトリ削除（空の場合のみ）
    RMDir "$INSTDIR"
    
    ; ショートカット削除
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME} (GUI).lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\${APP_NAME} (CLI).lnk"
    Delete "$SMPROGRAMS\${APP_NAME}\アンインストール.lnk"
    RMDir "$SMPROGRAMS\${APP_NAME}"
    Delete "$DESKTOP\${APP_NAME}.lnk"
    
    ; レジストリエントリ削除
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
    DeleteRegKey HKLM "Software\${APP_NAME}"
    
    ; パス環境変数から削除（オプション）
    ; EnVar::SetHKLM
    ; EnVar::DeleteValue "PATH" "$INSTDIR"
    ; Pop $0
    
SectionEnd

; セクション説明
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
!insertmacro MUI_DESCRIPTION_TEXT ${SecMain} "勤怠管理ツールのメインアプリケーションファイル"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

; インストール前の確認
Function .onInit
    ; 管理者権限チェック
    UserInfo::GetAccountType
    pop $0
    ${If} $0 != "admin"
        MessageBox MB_ICONSTOP "このインストーラーは管理者権限で実行する必要があります。"
        SetErrorLevel 740
        Quit
    ${EndIf}
    
    ; 既存インストールの確認
    ReadRegStr $0 HKLM "Software\${APP_NAME}" "InstallPath"
    ${If} $0 != ""
        MessageBox MB_YESNO|MB_ICONQUESTION "既存のインストールが見つかりました。$\n$\nアップデートを続行しますか？" IDYES +2
        Abort
    ${EndIf}
FunctionEnd