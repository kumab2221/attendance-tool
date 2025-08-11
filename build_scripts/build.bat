@echo off
REM 勤怠管理ツール Windows ビルドスクリプト

echo ============================================
echo Attendance Tool Windows Build Script
echo ============================================

REM Python環境の確認
python --version >nul 2>&1
if errorlevel 1 (
    echo エラー: Pythonがインストールされていません。
    echo Python 3.8以降をインストールしてください。
    pause
    exit /b 1
)

echo Pythonバージョン確認:
python --version

REM 仮想環境の作成
echo.
echo 仮想環境を作成中...
if exist "build_env" (
    echo 既存の仮想環境をクリーンアップ中...
    rmdir /s /q build_env
)

python -m venv build_env
if errorlevel 1 (
    echo エラー: 仮想環境の作成に失敗しました。
    pause
    exit /b 1
)

REM 仮想環境のアクティベート
echo 仮想環境をアクティベート中...
call build_env\Scripts\activate.bat

REM pip のアップグレード
echo.
echo pipをアップグレード中...
python -m pip install --upgrade pip

REM ビルド用依存関係のインストール
echo.
echo ビルド用依存関係をインストール中...
pip install -r requirements-build.txt
if errorlevel 1 (
    echo エラー: 依存関係のインストールに失敗しました。
    pause
    exit /b 1
)

REM プロジェクトのインストール（開発モード）
echo.
echo プロジェクトをインストール中...
pip install -e .
if errorlevel 1 (
    echo エラー: プロジェクトのインストールに失敗しました。
    pause
    exit /b 1
)

REM ビルドスクリプトの実行
echo.
echo ビルドプロセスを開始中...
python build_scripts\build_exe.py
if errorlevel 1 (
    echo エラー: ビルドプロセスに失敗しました。
    deactivate
    pause
    exit /b 1
)

REM 仮想環境の非アクティベート
deactivate

echo.
echo ============================================
echo ビルド完了！
echo 実行ファイルは dist/ ディレクトリに作成されました。
echo ============================================

REM distディレクトリの内容を表示
if exist "dist" (
    echo.
    echo 作成されたファイル:
    dir dist /B
)

echo.
echo ビルドプロセスが完了しました。
pause