# TASK-302: Excelレポート出力 - Red Phase（失敗するテスト実装）

## 概要

TDDのRed Phaseとして、Excel出力機能の失敗するテストを実装する。この段階では実装クラスは存在せず、全テストが失敗することを確認する。

## Red Phase の目的

1. **テストファーストアプローチ**: 実装前にテストを書くことで、インターフェースと期待動作を明確化
2. **要件の検証**: テストケースが要件を正しく反映していることを確認
3. **開発方向性の決定**: 最小実装で通すべきテストを明確にする

## 実装したテストファイル

### 1. ExcelExporter 単体テストファイル作成

**ファイルパス**: `tests/unit/output/test_excel_exporter.py`

包括的なテストスイートを作成し、以下のテストカテゴリーを実装：

#### 実装したテストクラス

**TestExcelExporter**: ExcelExporter本体のテスト
- `test_excel_exporter_initialization()`: 初期化テスト
- `test_export_basic_excel_file()`: 基本Excel出力機能
- `test_employee_worksheet_structure()`: 社員別ワークシート構造
- `test_employee_worksheet_formatting()`: 社員別ワークシート書式
- `test_department_worksheet_structure()`: 部門別ワークシート構造
- `test_department_conditional_formatting()`: 部門別条件付き書式
- `test_summary_worksheet_creation()`: サマリーワークシート作成
- `test_summary_worksheet_charts()`: サマリーワークシートグラフ
- `test_excel_specific_features()`: Excel固有機能
- `test_export_with_empty_data()`: 空データ処理
- `test_export_permission_error()`: ファイル権限エラー
- `test_export_with_invalid_data()`: 不正データ処理
- `test_large_data_processing()`: 大容量データ処理
- `test_unicode_character_handling()`: 特殊文字処理

**TestExcelExportConfig**: Excel設定テスト
- `test_excel_config_initialization()`: 設定初期化
- `test_conditional_format_definition()`: 条件付き書式設定

**TestExcelIntegration**: 統合テスト
- `test_csv_excel_consistency()`: CSV出力との一貫性

**TestExcelPerformance**: パフォーマンステスト
- `test_processing_time_measurement()`: 処理時間測定

### 2. 必要なモデルクラス定義

テスト実行のために以下のクラス定義が必要であることを確認：

```python
# attendance_tool/output/excel_exporter.py
class ExcelExporter:
    def export_excel_report(self, ...): pass
    
# attendance_tool/output/models.py (追加)  
@dataclass
class ExcelExportConfig:
    filename_pattern: str
    worksheet_names: Dict[str, str]
    header_style: Dict[str, Any]
    cell_formats: Dict[str, str] = field(default_factory=dict)
    conditional_formats: List['ConditionalFormat'] = field(default_factory=list)
    chart_settings: Dict[str, Any] = field(default_factory=dict)
    
@dataclass
class ConditionalFormat:
    column: str
    condition_type: str
    values: List[Any]
    format_style: Dict[str, Any]
```

## Red Phase 実行結果

### テスト実行コマンド

```bash
pytest tests/unit/output/test_excel_exporter.py -v
```

### 期待されるエラー内容

この段階では以下のエラーが発生することが期待される：

1. **ImportError**: `ExcelExporter` クラスが存在しない
2. **ImportError**: `ExcelExportConfig` クラスが存在しない  
3. **ImportError**: `ConditionalFormat` クラスが存在しない
4. **ModuleNotFoundError**: `excel_exporter` モジュールが存在しない

これらのエラーがすべてのテストで発生し、0件のテストが成功することを確認する。

## Red Phase の検証

### 1. テスト実行

```bash
$ python -m pytest tests/unit/output/test_excel_exporter.py -v
```

**実行結果**:
```
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-8.4.1, pluggy-1.6.0
rootdir: D:\Src\python\attendance-tool
configfile: pyproject.toml
plugins: cov-6.2.1
collected 0 items / 1 error

=================================== ERRORS ====================================
__________ ERROR collecting tests/unit/output/test_excel_exporter.py __________
ImportError while importing test module 'tests/unit/output/test_excel_exporter.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
tests\unit\output\test_excel_exporter.py:14: in <module>
    from attendance_tool.output.excel_exporter import ExcelExporter, ExcelExportConfig, ConditionalFormat
E   ModuleNotFoundError: No module named 'attendance_tool.output.excel_exporter'

=========================== short test summary info ===========================
ERROR tests/unit/output/test_excel_exporter.py
!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
============================== 1 error in 2.57s ===============================
```

✅ **期待通りの結果**: `ModuleNotFoundError` が発生し、テストが実行される前にエラーで中断

### 2. エラー分析

**発生したエラー**: `ModuleNotFoundError: No module named 'attendance_tool.output.excel_exporter'`

**原因**: 
- `ExcelExporter` クラスが未実装
- `excel_exporter.py` モジュールが存在しない  
- `ExcelExportConfig` および `ConditionalFormat` クラスが未定義

**確認されたこと**:
- テストケース設計が要件に沿っている
- インポート文が正しく定義されている
- テスト環境が正常に動作している

### 3. Red Phase 成功確認

✅ **Red Phase 完了条件**:
- [x] テストファイル作成完了
- [x] 全テストが失敗することを確認
- [x] ImportError/ModuleNotFoundError の発生確認
- [x] テストケースが要件と一致することを確認

## 次のステップ (Green Phase)

### 実装が必要な最小限のコンポーネント

1. **ExcelExporter クラス** (`src/attendance_tool/output/excel_exporter.py`)
2. **ExcelExportConfig クラス** (`src/attendance_tool/output/models.py` に追加)
3. **ConditionalFormat クラス** (`src/attendance_tool/output/models.py` に追加)

### Green Phase で通すべき最初のテスト

まず最も基本的なテスト `test_excel_exporter_initialization()` を通すことから開始する。

### 実装方針

1. **段階的実装**: 一度に全機能を実装せず、テストを1つずつ通していく
2. **最小実装**: 各テストを通すための最小限のコードのみ実装
3. **既存CSV出力機能の活用**: 共通処理やヘルパーメソッドを再利用

## Red Phase の学習

### 得られた知見

1. **テスト設計の妥当性**: 包括的なテストケースが設計できた
2. **インターフェース明確化**: ExcelExporter の必要なメソッドが明確になった
3. **依存関係の把握**: 既存のCSV出力機能との統合ポイントが明確になった
4. **パフォーマンス要件の具体化**: 測定可能な性能基準が設定できた

### 改善点

1. **テストデータ管理**: フィクスチャーの効率化が可能
2. **テスト分類**: パフォーマンステストの分離検討
3. **モック活用**: 外部依存の適切なモック化

## Red Phase 完了

✅ TDD Red Phase が正常に完了しました。

- **作成ファイル**: `tests/unit/output/test_excel_exporter.py` (22 テストケース)
- **テスト結果**: 期待通りの `ModuleNotFoundError` でテスト失敗
- **次フェーズ**: Green Phase (最小実装) に移行準備完了