# テスト実行ガイド（Test Execution Guide）

## 概要

このガイドは、開発者・QAエンジニア・プロジェクトマネージャーが
勤怠管理ツールのテストを効率的に実行するための実践的な手順書です。

## クイックスタート

### 環境準備
```bash
# 1. プロジェクトクローン
git clone https://github.com/kumab2221/attendance-tool.git
cd attendance-tool

# 2. 仮想環境作成
python -m venv test_env
source test_env/bin/activate  # Linux/Mac
# または
test_env\Scripts\activate     # Windows

# 3. テスト依存関係インストール
pip install -r requirements-dev.txt
pip install -e .
```

### 基本テスト実行
```bash
# 全テスト実行（推奨）
pytest tests/ -v

# カバレッジ付き実行
pytest tests/ --cov=attendance_tool --cov-report=html

# 並列実行（高速化）
pytest tests/ -n auto
```

## テストレベル別実行

### 1. 単体テスト（Unit Tests）

#### 実行コマンド
```bash
# 全単体テスト
pytest tests/unit/ -v

# 特定モジュール
pytest tests/unit/calculation/ -v
pytest tests/unit/validation/ -v
pytest tests/unit/output/ -v

# 特定ファイル
pytest tests/unit/test_csv_reader.py -v

# 特定テストケース
pytest tests/unit/test_calculator.py::test_basic_calculation -v
```

#### 実行時間目安
- **全単体テスト**: 約6秒
- **モジュール別**: 1-2秒
- **単一テスト**: <1秒

#### 期待される結果
```
==================== test session starts ====================
collected 142 items

tests/unit/test_csv_reader.py::test_read_standard_csv PASSED
tests/unit/test_csv_reader.py::test_read_utf8_csv PASSED
tests/unit/test_csv_reader.py::test_handle_invalid_file PASSED
...
tests/unit/calculation/test_calculator.py::test_monthly_summary PASSED

==================== 142 passed in 5.89s ====================
```

### 2. 統合テスト（Integration Tests）

#### 実行コマンド
```bash
# 全統合テスト
pytest tests/integration/ -v

# CLI統合テスト
pytest tests/integration/test_cli_integration.py -v

# 設定統合テスト
pytest tests/integration/test_config_integration.py -v

# エラーハンドリング統合テスト
pytest tests/integration/errors/ -v
```

#### データ準備
```bash
# テストデータ自動生成
python tests/fixtures/generate_test_data.py

# 手動データ確認
ls tests/fixtures/csv/
ls tests/fixtures/expected_outputs/
```

#### 実行時間目安
- **全統合テスト**: 約5秒
- **CLI統合**: 約2秒
- **設定統合**: 約1秒

### 3. E2Eテスト（End-to-End Tests）

#### 実行コマンド
```bash
# 全E2Eテスト
pytest tests/e2e/ -v

# 正常フローのみ
pytest tests/e2e/test_end_to_end.py::TestE2EIntegration::test_complete_normal_workflow -v

# パフォーマンステストのみ
pytest tests/e2e/test_end_to_end.py::TestE2EIntegration::test_performance_regression -v

# セキュリティテストのみ
pytest tests/e2e/test_end_to_end.py::TestE2EIntegration::test_security_compliance -v
```

#### 大容量データテスト
```bash
# 大容量テストデータ生成
export LARGE_TEST_DATA=true
pytest tests/e2e/ -v -k "performance"

# テストデータサイズ設定
export TEST_EMPLOYEE_COUNT=100
export TEST_DAYS_COUNT=30
pytest tests/e2e/test_end_to_end.py::TestE2EIntegration::test_performance_regression -v
```

#### 実行時間目安
- **全E2Eテスト**: 約8秒
- **正常フロー**: 約1秒
- **パフォーマンステスト**: 約3秒
- **大容量データ**: 約15秒

## 特殊テスト実行

### パフォーマンステスト

#### ベンチマークテスト
```bash
# パフォーマンス測定付きテスト
pytest tests/unit/performance/ --benchmark-only

# メモリ使用量監視
pytest tests/e2e/ --profile --profile-svg

# 処理時間詳細測定
pytest tests/unit/calculation/ --durations=10
```

#### カスタムパフォーマンステスト
```bash
# 1. 大容量データ生成
python scripts/generate_performance_data.py --employees 1000 --days 30

# 2. パフォーマンステスト実行
pytest tests/performance/test_large_scale.py -v --tb=short

# 3. 結果分析
python scripts/analyze_performance_results.py
```

### セキュリティテスト

#### 基本セキュリティテスト
```bash
# 個人情報保護テスト
pytest tests/unit/logging/test_masking.py -v

# 一時ファイル管理テスト
pytest tests/integration/test_temp_file_cleanup.py -v

# ログセキュリティテスト
pytest tests/e2e/test_end_to_end.py::TestE2EIntegration::test_security_compliance -v
```

#### 追加セキュリティ検証
```bash
# ログファイル内容確認
python scripts/check_log_security.py

# 一時ファイル残存確認
python scripts/verify_cleanup.py
```

### GUIテスト

#### GUI自動テスト実行
```bash
# GUI単体テスト
pytest tests/unit/gui/ -v

# GUI統合テスト（要：ディスプレイ環境）
export DISPLAY=:0  # Linux
pytest tests/integration/test_gui_integration.py -v

# ヘッドレスモード（CI用）
pytest tests/unit/gui/ -v --headless
```

#### GUI手動テスト
```bash
# GUI起動確認
python gui_main.py

# CLI起動確認
python cli_main.py --help

# 実行ファイル確認
dist/attendance-tool-gui.exe
dist/attendance-tool-cli.exe --version
```

## カバレッジ測定

### 基本カバレッジ測定

#### HTML レポート生成
```bash
# カバレッジ測定 + HTMLレポート
pytest tests/ --cov=attendance_tool --cov-report=html

# レポート確認
open htmlcov/index.html  # Mac
start htmlcov/index.html # Windows
```

#### ターミナルレポート
```bash
# 詳細レポート
pytest tests/ --cov=attendance_tool --cov-report=term-missing

# サマリーのみ
pytest tests/ --cov=attendance_tool --cov-report=term
```

### 高度なカバレッジ分析

#### ブランチカバレッジ
```bash
# ブランチカバレッジ測定
pytest tests/ --cov=attendance_tool --cov-branch --cov-report=html

# 未カバーブランチ特定
pytest tests/ --cov=attendance_tool --cov-branch --cov-report=term-missing
```

#### モジュール別カバレッジ
```bash
# 特定モジュールのカバレッジ
pytest tests/unit/calculation/ --cov=attendance_tool.calculation

# 複数モジュール指定
pytest tests/ --cov=attendance_tool.validation --cov=attendance_tool.output
```

### カバレッジ閾値設定
```bash
# カバレッジが90%未満の場合失敗
pytest tests/ --cov=attendance_tool --cov-fail-under=90

# 特定モジュールの閾値設定
pytest tests/unit/gui/ --cov=attendance_tool.gui --cov-fail-under=80
```

## テストデータ管理

### テストデータ生成

#### 標準テストデータ
```python
# Python スクリプトでの生成
from tests.fixtures.test_data_manager import TestDataManager

manager = TestDataManager()

# 小規模データ（開発・単体テスト用）
data = manager.generate_csv_data(employees=3, days=5)
manager.save_csv(data, "tests/fixtures/csv/small_test_data.csv")

# 中規模データ（統合テスト用）
data = manager.generate_csv_data(employees=20, days=20)
manager.save_csv(data, "tests/fixtures/csv/medium_test_data.csv")

# 大規模データ（パフォーマンステスト用）
data = manager.generate_csv_data(employees=100, days=30)
manager.save_csv(data, "tests/fixtures/csv/large_test_data.csv")
```

#### エラーデータ生成
```python
# 不正データ生成
error_data = manager.generate_error_data(
    error_types=['invalid_date', 'missing_time', 'negative_hours'],
    error_rate=0.1  # 10%のエラー率
)
manager.save_csv(error_data, "tests/fixtures/csv/error_test_data.csv")
```

#### バッチ生成
```bash
# 全テストデータ一括生成
python scripts/generate_all_test_data.py

# カスタムデータセット生成
python scripts/generate_test_data.py \
    --employees 50 \
    --days 15 \
    --error-rate 0.05 \
    --output tests/fixtures/csv/custom_data.csv
```

### テストデータクリーンアップ

#### 一時データ削除
```bash
# 一時テストファイル削除
python scripts/cleanup_test_data.py

# 手動削除
rm -rf tests/temp_*
rm -rf output/test_*
```

## 並列テスト実行

### pytest-xdist使用

#### 基本並列実行
```bash
# CPU数に応じた自動並列化
pytest tests/ -n auto

# 固定プロセス数指定
pytest tests/ -n 4

# 並列実行 + カバレッジ
pytest tests/ -n auto --cov=attendance_tool
```

#### 並列実行の制限
```bash
# 特定テストを順次実行
pytest tests/integration/ -n auto -m "not sequential"
pytest tests/integration/ -m "sequential"
```

### テスト分散

#### モジュール別分散実行
```bash
# 端末1: データ処理テスト
pytest tests/unit/data/ tests/unit/validation/ -v

# 端末2: 計算・出力テスト
pytest tests/unit/calculation/ tests/unit/output/ -v

# 端末3: 統合・E2Eテスト
pytest tests/integration/ tests/e2e/ -v
```

## CI/CD統合

### GitHub Actions

#### ワークフロー実行
```bash
# ローカルでのCI環境再現
act -j test

# 特定ジョブのみ実行
act -j unit-tests
act -j integration-tests
act -j e2e-tests
```

#### 環境変数設定
```yaml
# .github/workflows/test.yml
env:
  PYTEST_ARGS: "-v --tb=short"
  COVERAGE_THRESHOLD: "85"
  PARALLEL_JOBS: "4"
```

### 事前コミットフック

#### pre-commit設定
```bash
# pre-commit インストール
pip install pre-commit
pre-commit install

# 手動実行
pre-commit run --all-files

# 特定フック実行
pre-commit run pytest
pre-commit run black
pre-commit run mypy
```

## トラブルシューティング

### よくある問題と解決策

#### 1. テスト実行エラー

**問題**: `ModuleNotFoundError: No module named 'attendance_tool'`
```bash
# 解決策1: エディタブルインストール
pip install -e .

# 解決策2: PYTHONPATH設定
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

**問題**: `FileNotFoundError: config/logging.yaml`
```bash
# 解決策: 設定ファイルコピー
cp config/*.yaml tests/fixtures/config/
```

#### 2. カバレッジ測定エラー

**問題**: カバレッジが正しく測定されない
```bash
# 解決策1: .coveragerc確認
cat .coveragerc

# 解決策2: カバレッジファイル削除
rm .coverage
rm -rf htmlcov/
```

#### 3. パフォーマンステスト失敗

**問題**: 大容量データでメモリ不足
```bash
# 解決策1: テストデータサイズ縮小
export TEST_EMPLOYEE_COUNT=10
export TEST_DAYS_COUNT=5

# 解決策2: メモリ使用量監視
pytest tests/e2e/ --memprof
```

#### 4. GUI テスト失敗

**問題**: ヘッドレス環境でGUIテスト失敗
```bash
# 解決策1: 仮想ディスプレイ使用
Xvfb :99 -screen 0 1024x768x24 &
export DISPLAY=:99

# 解決策2: GUIテストスキップ
pytest tests/ -m "not gui"
```

### デバッグテクニック

#### 詳細ログ出力
```bash
# pytest詳細ログ
pytest tests/ -v -s --log-cli-level=DEBUG

# 特定テストのデバッグ
pytest tests/unit/test_calculator.py::test_specific_case -v -s --pdb

# 失敗時のデバッガ起動
pytest tests/ --pdb-on-failure
```

#### テスト結果分析
```bash
# テスト結果をJUnit XML出力
pytest tests/ --junitxml=results.xml

# 実行時間分析
pytest tests/ --durations=10

# メモリ使用量プロファイル
pytest tests/ --profile
```

## 品質チェックリスト

### テスト実行前チェック

- [ ] 仮想環境が有効化されている
- [ ] 最新の依存関係がインストール済み
- [ ] テストデータが準備されている
- [ ] 必要な設定ファイルが存在する

### テスト実行後確認

- [ ] すべてのテストが成功している
- [ ] カバレッジが目標値を達成している
- [ ] パフォーマンス要件を満たしている
- [ ] エラーログに異常がない

### リリース前最終チェック

- [ ] 全テストスイート実行 (`pytest tests/ -v`)
- [ ] カバレッジ90%以上 (`--cov-fail-under=90`)
- [ ] E2Eテスト全て成功
- [ ] パフォーマンス回帰なし
- [ ] セキュリティテスト全て成功

## 付録

### 有用なコマンド集

```bash
# テスト環境リセット
rm -rf .pytest_cache/ __pycache__/ *.pyc .coverage htmlcov/

# テストのみ実行（ビルドスキップ）
pytest tests/ --no-build

# 失敗したテストのみ再実行
pytest --lf

# キーワードベースフィルタリング
pytest -k "test_csv and not test_large"

# マーカーベースフィルタリング  
pytest -m "slow"
pytest -m "not slow"

# テスト収集確認（実行はしない）
pytest --collect-only tests/
```

### 設定ファイル例

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --cov=attendance_tool
    --cov-report=term-missing
    --cov-fail-under=85
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    gui: marks tests as GUI tests
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
```

#### .coveragerc  
```ini
[run]
source = src/attendance_tool
omit = 
    tests/*
    */migrations/*
    */venv/*
    setup.py
    build_scripts/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

---

**作成日**: 2025-08-11  
**最終更新**: 2025-08-11  
**バージョン**: 1.0  
**作成者**: QA Team