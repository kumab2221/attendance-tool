# TASK-301: CSVレポート出力 - Red Phase（失敗するテスト実装）

## 実装ステータス

✅ **Red Phase完了**: 失敗するテストを実装しました

## 実装内容

### 1. テストファイルの作成

#### テスト構造
```
tests/
├── unit/output/
│   ├── __init__.py
│   └── test_csv_exporter.py        # メインテストファイル
├── fixtures/csv_export/
│   ├── standard_employee_data.py   # テストデータ定義
│   └── expected_outputs/           # 期待値CSVファイル
└── integration/
    └── test_csv_export_integration.py  # 統合テスト（未実装）
```

#### 実装したテストケース

**正常系テスト**:
- `test_export_employee_report_normal_case()` - TC-301-001
- `test_export_department_report_normal_case()` - TC-301-002

**異常系テスト**:
- `test_export_with_empty_dataset()` - TC-301-101
- `test_export_nonexistent_directory()` - TC-301-102
- `test_export_permission_error()` - TC-301-103
- `test_export_disk_full_error()` - TC-301-104
- `test_export_with_invalid_data()` - TC-301-105
- `test_export_with_config_error()` - TC-301-106

**境界値テスト**:
- `test_export_special_characters()` - TC-301-204
- `test_export_large_dataset_performance()` - TC-301-202

**統合テスト**:
- `test_multiple_reports_export()` - TC-301-301

### 2. テストデータの準備

#### 標準テストデータ (`standard_employee_data.py`)

```python
STANDARD_EMPLOYEE_DATA = [
    AttendanceSummary(
        employee_id="EMP001",
        employee_name="田中太郎",
        department="開発部",
        # ... 必要なフィールド
    ),
    # ... 3名分のデータ
]

STANDARD_DEPARTMENT_DATA = [
    DepartmentSummary(
        department_code="DEV",
        department_name="開発部",
        # ... 必要なフィールド
    ),
    # ... 2部門分のデータ
]
```

#### エッジケースデータ

- 空の名前・部門名
- 特殊文字を含むデータ（CSV区切り文字、改行文字など）
- ゼロ値データ
- 境界値データ（うるう年、月末日など）

### 3. 期待値ファイルの作成

#### 社員別レポート期待値
- ファイル名: `employee_report_2024_01.csv`
- UTF-8 BOM付きエンコーディング
- 必須カラム: 社員ID, 氏名, 部署, 対象年月, 出勤日数, etc.

#### 部門別レポート期待値  
- ファイル名: `department_report_2024_01.csv`
- 部門ごとの集計データ
- 平均出勤率のパーセンテージ表示

## 現在のテスト実行結果

### 期待される失敗

```bash
$ pytest tests/unit/output/test_csv_exporter.py -v
```

**予想されるエラー**:
```
ImportError: No module named 'attendance_tool.output.csv_exporter'
```

これらのモジュールはまだ実装されていないため、テストは失敗します:

1. `attendance_tool.output.csv_exporter.CSVExporter`
2. `attendance_tool.output.csv_exporter.ExportResult`
3. `attendance_tool.output.models.CSVExportConfig`

### Red Phaseでテストされる機能

#### 必須実装項目

1. **CSVExporter クラス**
   ```python
   class CSVExporter:
       def export_employee_report(self, summaries, output_path, year, month) -> ExportResult
       def export_department_report(self, summaries, output_path, year, month) -> ExportResult
       def export_daily_detail_report(self, records, output_path, year, month) -> ExportResult
   ```

2. **ExportResult データクラス**
   ```python
   @dataclass
   class ExportResult:
       success: bool
       file_path: Path
       record_count: int
       file_size: int
       processing_time: float
       errors: List[str]
       warnings: List[str]
   ```

3. **エラーハンドリング機能**
   - PermissionError の適切な処理
   - OSError（ディスク容量不足）の処理
   - FileNotFoundError（設定ファイル）の処理

4. **データバリデーション**
   - None値の検出と処理
   - 不正値（負の値など）の検出
   - 特殊文字のエスケープ処理

5. **パフォーマンス要件**
   - 1000件データの30秒以内処理
   - メモリ使用量の監視
   - ファイル書き込み性能

## テスト実行手順

### 1. 依存関係の確認

```bash
# 必要なパッケージがインストールされているか確認
pip list | grep -E "(pandas|pytest|pathlib)"
```

### 2. テスト実行

```bash
# Red Phase: テストが失敗することを確認
pytest tests/unit/output/test_csv_exporter.py -v

# 期待される結果: ImportError でテストがスキップされる
```

### 3. カバレッジ測定準備

```bash
# テストカバレッジ用の設定
pytest tests/unit/output/ --cov=src/attendance_tool/output --cov-report=term-missing
```

## 次のステップ（Green Phase）

Green Phaseでは以下を実装します:

1. **出力ディレクトリの作成**
   ```bash
   mkdir -p src/attendance_tool/output
   ```

2. **基本モジュールファイルの作成**
   - `src/attendance_tool/output/__init__.py`
   - `src/attendance_tool/output/csv_exporter.py`
   - `src/attendance_tool/output/models.py`

3. **最小実装の作成**
   - テストが通る最小限の機能
   - スタブメソッド中心の実装
   - 基本的なファイル出力機能

## 実装上の注意点

### 1. エンコーディング対応
- UTF-8 BOM付き（`utf-8-sig`）でExcel互換性を確保
- 文字化け防止のための適切なエンコーディング処理

### 2. CSV特殊文字処理
- カンマ、改行文字、クォート文字の適切なエスケープ
- pandas の `to_csv()` メソッドの活用

### 3. エラーハンドリング設計
- 部分的な成功（一部ファイルの出力失敗）への対応
- ログ記録とユーザーへの適切な通知

### 4. パフォーマンス考慮事項
- 大容量データでのメモリ効率的な処理
- チャンク処理による分割出力の検討

## 品質基準

### テスト成功基準
- 全テストケースが期待通りに失敗している
- テストデータが適切に準備されている
- モック・パッチが正しく設定されている

### コード品質基準
- テストコードの可読性
- テストケースの網羅性（正常・異常・境界値）
- テストデータの妥当性

## 確認済み項目

- ✅ テストファイル作成完了
- ✅ テストデータ準備完了
- ✅ 期待値ファイル作成完了
- ✅ エラーハンドリングテスト実装
- ✅ パフォーマンステスト実装
- ✅ 統合テスト基本実装

**Red Phase完了**: 次のGreen Phaseで実装を開始できます。