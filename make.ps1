# Windows用Makefileラッパー - PowerShell版
param(
    [string]$Target = "help"
)

function Show-Help {
    Write-Host "勤怠管理ツール統合テスト用 Windows Makefile" -ForegroundColor Green
    Write-Host ""
    Write-Host "使用方法: .\make.ps1 <target>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "利用可能なターゲット:" -ForegroundColor Cyan
    Write-Host "  help               このヘルプメッセージを表示"
    Write-Host "  install            依存関係をインストール"
    Write-Host "  test               すべてのテストを実行"
    Write-Host "  unit-test          単体テストを実行"
    Write-Host "  integration-test   統合テストを実行"
    Write-Host "  e2e-test           E2Eテストを実行"
    Write-Host "  lint               コード品質チェック"
    Write-Host "  complexity         コード複雑度チェック（基本）"
    Write-Host "  complexity-report  コード複雑度レポート生成（HTML）"
    Write-Host "  complexity-ci      CI用コード複雑度チェック"
    Write-Host "  format             コードフォーマット"
    Write-Host "  clean              一時ファイルを削除"
    Write-Host "  setup-dev          開発環境をセットアップ"
    Write-Host "  pre-release        リリース前の品質チェック"
    Write-Host "  quality-report     品質レポートを生成"
}

function Install {
    Write-Host "依存関係をインストール中..." -ForegroundColor Yellow
    pip install -e .[dev]
    pip install chardet psutil
}

function Test-All {
    Write-Host "すべてのテストを実行中..." -ForegroundColor Yellow
    Unit-Test
    Integration-Test
    E2E-Test
}

function Unit-Test {
    Write-Host "単体テストを実行中..." -ForegroundColor Yellow
    python -m pytest tests/unit/ -v --cov=attendance_tool --cov-report=term-missing
}

function Integration-Test {
    Write-Host "統合テストを実行中..." -ForegroundColor Yellow
    python -m pytest tests/integration/ -v
}

function E2E-Test {
    Write-Host "E2Eテストを実行中..." -ForegroundColor Yellow
    python -m pytest tests/e2e/ -v --timeout=300
}

function Lint {
    Write-Host "コード品質チェック中..." -ForegroundColor Yellow
    black --check src/ tests/
    mypy src/
    flake8 src/ tests/
}

function Complexity {
    Write-Host "コード複雑度チェック中..." -ForegroundColor Yellow
    python scripts/complexity_check.py --threshold 10 --verbose
}

function Complexity-Report {
    Write-Host "コード複雑度レポート生成中..." -ForegroundColor Yellow
    python scripts/complexity_check.py --threshold 10 --format html --output reports/complexity/complexity_report.html
    Write-Host "HTMLレポートが生成されました: reports/complexity/complexity_report.html" -ForegroundColor Green
}

function Complexity-CI {
    Write-Host "CI用コード複雑度チェック中..." -ForegroundColor Yellow
    python scripts/complexity_check.py --threshold 10 --ci
}

function Format {
    Write-Host "コードフォーマット中..." -ForegroundColor Yellow
    black src/ tests/
    isort src/ tests/
}

function Clean {
    Write-Host "一時ファイルを削除中..." -ForegroundColor Yellow
    Get-ChildItem -Recurse -Filter "*.pyc" | Remove-Item -Force
    Get-ChildItem -Recurse -Directory -Name "__pycache__" | Remove-Item -Recurse -Force
    Remove-Item -Recurse -Force ".pytest_cache" -ErrorAction SilentlyContinue
    Remove-Item -Force ".coverage" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "htmlcov" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue
    Get-ChildItem -Recurse -Directory -Name "*.egg-info" | Remove-Item -Recurse -Force
    Remove-Item -Recurse -Force "reports" -ErrorAction SilentlyContinue
}

function Setup-Dev {
    Write-Host "開発環境をセットアップ中..." -ForegroundColor Yellow
    pip install -e .[dev]
    pip install chardet psutil
    pre-commit install
}

function Pre-Release {
    Write-Host "リリース前の品質チェック中..." -ForegroundColor Yellow
    Lint
    Complexity-CI
    Test-All
    Write-Host "すべてのチェックが完了しました" -ForegroundColor Green
}

function Quality-Report {
    Write-Host "品質レポートを生成中..." -ForegroundColor Yellow
    Unit-Test
    Complexity-Report
    Write-Host "品質レポートが生成されました" -ForegroundColor Green
    Write-Host "  - カバレッジ: htmlcov/index.html" -ForegroundColor Cyan
    Write-Host "  - 複雑度: reports/complexity/complexity_report.html" -ForegroundColor Cyan
}

# メイン処理
switch ($Target.ToLower()) {
    "help" { Show-Help }
    "install" { Install }
    "test" { Test-All }
    "unit-test" { Unit-Test }
    "integration-test" { Integration-Test }
    "e2e-test" { E2E-Test }
    "lint" { Lint }
    "complexity" { Complexity }
    "complexity-report" { Complexity-Report }
    "complexity-ci" { Complexity-CI }
    "format" { Format }
    "clean" { Clean }
    "setup-dev" { Setup-Dev }
    "pre-release" { Pre-Release }
    "quality-report" { Quality-Report }
    default {
        Write-Host "無効なターゲット: $Target" -ForegroundColor Red
        Write-Host "利用可能なターゲットは .\make.ps1 help で確認してください" -ForegroundColor Yellow
        exit 1
    }
}