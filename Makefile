# 勤怠管理ツール統合テスト用Makefile

.PHONY: help install test unit-test integration-test e2e-test lint format clean complexity complexity-report complexity-ci

help:  ## このヘルプメッセージを表示
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## 依存関係をインストール
	pip install -e .[dev]
	pip install chardet psutil

test: unit-test integration-test e2e-test  ## すべてのテストを実行

unit-test:  ## 単体テストを実行
	python -m pytest tests/unit/ -v --cov=attendance_tool --cov-report=term-missing

integration-test:  ## 統合テストを実行
	python -m pytest tests/integration/ -v

e2e-test:  ## E2Eテストを実行
	python -m pytest tests/e2e/ -v --timeout=300

performance-test:  ## パフォーマンステストを実行
	python -m pytest tests/e2e/test_end_to_end.py::TestE2EIntegration::test_performance_regression -v

security-test:  ## セキュリティテストを実行
	python -m pytest tests/e2e/test_end_to_end.py::TestE2EIntegration::test_security_compliance -v

lint:  ## コード品質チェック
	black --check src/ tests/
	mypy src/
	flake8 src/ tests/

complexity:  ## コード複雑度チェック（基本）
	python scripts/complexity_check.py --threshold 10 --verbose

complexity-report:  ## コード複雑度レポート生成（HTML）
	python scripts/complexity_check.py --threshold 10 --format html --output reports/complexity/complexity_report.html
	@echo "📄 HTMLレポートが生成されました: reports/complexity/complexity_report.html"

complexity-ci:  ## CI用コード複雑度チェック（閾値超過で失敗）
	python scripts/complexity_check.py --threshold 10 --ci

format:  ## コードフォーマット
	black src/ tests/
	isort src/ tests/

clean:  ## 一時ファイルを削除
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/
	rm -rf reports/

# テストデータ生成
test-data:  ## テストデータを生成
	python -c "
from pathlib import Path
from src.attendance_tool.e2e.test_data_manager import TestDataManager
dm = TestDataManager()
dm.generate_standard_csv_data(Path('test_data.csv'), 10, 21)
print('テストデータ test_data.csv を生成しました')
"

# 開発環境セットアップ
setup-dev:  ## 開発環境をセットアップ
	pip install -e .[dev]
	pip install chardet psutil
	pre-commit install

# リリース前チェック
pre-release:  ## リリース前の品質チェック
	make lint
	make complexity-ci
	make test
	@echo "すべてのチェックが完了しました"

# 品質レポート生成
quality-report:  ## 品質レポートを生成（カバレッジ + 複雑度）
	make unit-test
	make complexity-report
	@echo "🎉 品質レポートが生成されました"
	@echo "  - カバレッジ: htmlcov/index.html"
	@echo "  - 複雑度: reports/complexity/complexity_report.html"