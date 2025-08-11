@echo off
:: Windows用Makefileラッパー
setlocal enabledelayedexpansion

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="install" goto install
if "%1"=="test" goto test
if "%1"=="unit-test" goto unit-test
if "%1"=="integration-test" goto integration-test
if "%1"=="e2e-test" goto e2e-test
if "%1"=="performance-test" goto performance-test
if "%1"=="security-test" goto security-test
if "%1"=="lint" goto lint
if "%1"=="complexity" goto complexity
if "%1"=="complexity-report" goto complexity-report
if "%1"=="complexity-ci" goto complexity-ci
if "%1"=="format" goto format
if "%1"=="clean" goto clean
if "%1"=="test-data" goto test-data
if "%1"=="setup-dev" goto setup-dev
if "%1"=="pre-release" goto pre-release
if "%1"=="quality-report" goto quality-report
goto invalid

:help
echo 勤怠管理ツール統合テスト用 Windows Makefile
echo.
echo 利用可能なターゲット:
echo   help               このヘルプメッセージを表示
echo   install            依存関係をインストール
echo   test               すべてのテストを実行
echo   unit-test          単体テストを実行
echo   integration-test   統合テストを実行
echo   e2e-test           E2Eテストを実行
echo   performance-test   パフォーマンステストを実行
echo   security-test      セキュリティテストを実行
echo   lint               コード品質チェック
echo   complexity         コード複雑度チェック（基本）
echo   complexity-report  コード複雑度レポート生成（HTML）
echo   complexity-ci      CI用コード複雑度チェック（閾値超過で失敗）
echo   format             コードフォーマット
echo   clean              一時ファイルを削除
echo   test-data          テストデータを生成
echo   setup-dev          開発環境をセットアップ
echo   pre-release        リリース前の品質チェック
echo   quality-report     品質レポートを生成（カバレッジ + 複雑度）
goto end

:install
echo 依存関係をインストール中...
pip install -e .[dev]
pip install chardet psutil
goto end

:test
echo すべてのテストを実行中...
call %0 unit-test
call %0 integration-test
call %0 e2e-test
goto end

:unit-test
echo 単体テストを実行中...
python -m pytest tests/unit/ -v --cov=attendance_tool --cov-report=term-missing
goto end

:integration-test
echo 統合テストを実行中...
python -m pytest tests/integration/ -v
goto end

:e2e-test
echo E2Eテストを実行中...
python -m pytest tests/e2e/ -v --timeout=300
goto end

:performance-test
echo パフォーマンステストを実行中...
python -m pytest tests/e2e/test_end_to_end.py::TestE2EIntegration::test_performance_regression -v
goto end

:security-test
echo セキュリティテストを実行中...
python -m pytest tests/e2e/test_end_to_end.py::TestE2EIntegration::test_security_compliance -v
goto end

:lint
echo コード品質チェック中...
black --check src/ tests/
mypy src/
flake8 src/ tests/
goto end

:complexity
echo コード複雑度チェック中...
python scripts/complexity_check.py --threshold 10 --verbose
goto end

:complexity-report
echo コード複雑度レポート生成中...
python scripts/complexity_check.py --threshold 10 --format html --output reports/complexity/complexity_report.html
echo HTMLレポートが生成されました: reports/complexity/complexity_report.html
goto end

:complexity-ci
echo CI用コード複雑度チェック中...
python scripts/complexity_check.py --threshold 10 --ci
goto end

:format
echo コードフォーマット中...
black src/ tests/
isort src/ tests/
goto end

:clean
echo 一時ファイルを削除中...
for /r . %%i in (*.pyc) do del "%%i" 2>nul
for /r . %%i in (__pycache__) do rmdir /s /q "%%i" 2>nul
rmdir /s /q .pytest_cache 2>nul
del .coverage 2>nul
rmdir /s /q htmlcov 2>nul
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul
for /r . %%i in (*.egg-info) do rmdir /s /q "%%i" 2>nul
rmdir /s /q reports 2>nul
goto end

:test-data
echo テストデータを生成中...
python -c "from pathlib import Path; from src.attendance_tool.e2e.test_data_manager import TestDataManager; dm = TestDataManager(); dm.generate_standard_csv_data(Path('test_data.csv'), 10, 21); print('テストデータ test_data.csv を生成しました')"
goto end

:setup-dev
echo 開発環境をセットアップ中...
pip install -e .[dev]
pip install chardet psutil
pre-commit install
goto end

:pre-release
echo リリース前の品質チェック中...
call %0 lint
call %0 complexity-ci
call %0 test
echo すべてのチェックが完了しました
goto end

:quality-report
echo 品質レポートを生成中...
call %0 unit-test
call %0 complexity-report
echo 品質レポートが生成されました
echo   - カバレッジ: htmlcov/index.html
echo   - 複雑度: reports/complexity/complexity_report.html
goto end

:invalid
echo 無効なターゲット: %1
echo 利用可能なターゲットは "make.bat help" で確認してください
exit /b 1

:end