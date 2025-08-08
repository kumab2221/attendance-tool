# TASK-301: CSVレポート出力 - テストケース設計

## テストケース一覧

### 1. 正常系テストケース

#### TC-301-001: 社員別CSVレポート出力（正常ケース）
- **テスト目的**: 標準的な勤怠データで社員別CSVが正常に出力される
- **前提条件**: 
  - 3名の社員の1か月分勤怠データ（AttendanceSummary）
  - 出力ディレクトリが存在
- **テストデータ**:
  ```python
  employees = [
      AttendanceSummary(
          employee_id="EMP001",
          employee_name="田中太郎", 
          department="開発部",
          period_start=date(2024, 1, 1),
          period_end=date(2024, 1, 31),
          attendance_days=20,
          total_work_minutes=9600,  # 160時間
          overtime_minutes=1200     # 20時間
      ),
      # ... その他のテストデータ
  ]
  ```
- **実行手順**:
  1. CSVExporter.export_employee_report()を呼び出し
  2. 出力ファイルの存在確認
  3. CSVファイルの内容検証
- **期待結果**:
  - ファイル名: `employee_report_2024_01.csv`
  - UTF-8 BOM付きエンコーディング
  - 3行のデータ行（ヘッダー除く）
  - 必要な全カラムが存在

#### TC-301-002: 部門別CSVレポート出力（正常ケース）
- **テスト目的**: 部門別集計データで部門別CSVが正常に出力される
- **前提条件**: 
  - 3部門のDepartmentSummaryデータ
  - config/csv_format.yamlが存在
- **テストデータ**:
  ```python
  departments = [
      DepartmentSummary(
          department_code="DEV",
          department_name="開発部",
          employee_count=10,
          total_work_minutes=48000,
          attendance_rate=95.5
      ),
      # ... その他のテストデータ
  ]
  ```
- **期待結果**: 部門別CSVファイルの正常生成

#### TC-301-003: 日別詳細CSVレポート出力（正常ケース）
- **テスト目的**: 日別勤怠詳細データでCSVが正常に出力される
- **前提条件**: AttendanceRecordの日別データリスト
- **期待結果**: 日別詳細CSVファイルの正常生成

#### TC-301-004: カスタムフォーマット適用
- **テスト目的**: 設定ファイルのフォーマット設定が正しく適用される
- **前提条件**: csv_format.yamlでカスタム設定を定義
- **実行手順**:
  1. 数値フォーマット（小数点2桁）を設定
  2. カスタムヘッダー名を設定
  3. CSV出力実行
- **期待結果**:
  - 数値が指定フォーマットで出力
  - カスタムヘッダー名が使用される

### 2. 異常系テストケース

#### TC-301-101: 空データセット
- **テスト目的**: データが空の場合の動作確認
- **前提条件**: 空のリスト（[]）をデータとして渡す
- **期待結果**:
  - 例外が発生しない
  - ヘッダーのみのCSVファイルが生成される
  - 適切な警告ログが出力される

#### TC-301-102: 出力ディレクトリが存在しない
- **テスト目的**: 存在しないディレクトリへの出力処理確認
- **前提条件**: 存在しないパス `/nonexistent/path/` を指定
- **期待結果**:
  - ディレクトリが自動作成される
  - CSVファイルが正常に生成される

#### TC-301-103: 書き込み権限なし
- **テスト目的**: 書き込み権限がない場合のエラーハンドリング
- **前提条件**: 読み取り専用ディレクトリを出力先に指定
- **期待結果**:
  - PermissionErrorが適切にハンドリングされる
  - エラーメッセージがExportResultに含まれる
  - 処理が継続される（他のファイルは出力される）

#### TC-301-104: ディスク容量不足シミュレーション
- **テスト目的**: ディスク容量不足時の動作確認
- **前提条件**: モックを使用してディスク容量不足をシミュレート
- **期待結果**:
  - OSErrorが適切にハンドリングされる
  - 部分的に書き込まれたファイルがクリーンアップされる

#### TC-301-105: 不正なデータ形式
- **テスト目的**: データにNoneや不正値が含まれる場合の処理
- **前提条件**:
  ```python
  invalid_data = [
      AttendanceSummary(
          employee_id=None,  # 不正値
          employee_name="",  # 空文字
          total_work_minutes=-100  # 負の値
      )
  ]
  ```
- **期待結果**:
  - データバリデーションが実行される
  - 不正データは適切にスキップまたは修正される
  - 警告ログが出力される

#### TC-301-106: 設定ファイル読み込みエラー
- **テスト目的**: csv_format.yamlが存在しない・破損している場合
- **前提条件**: 設定ファイルを削除または破損させる
- **期待結果**:
  - デフォルト設定が使用される
  - 警告ログが出力される
  - 処理が継続される

### 3. 境界値テストケース

#### TC-301-201: 最小データセット
- **テスト目的**: 1件のデータでの動作確認
- **前提条件**: 1件のAttendanceSummaryデータ
- **期待結果**: 正常にCSVが生成される

#### TC-301-202: 大容量データセット
- **テスト目的**: 1000名×31日分のデータでの性能確認
- **前提条件**: 
  - 1000件のAttendanceSummaryデータ
  - メモリ使用量監視
  - 処理時間計測
- **期待結果**:
  - 処理時間が30秒以内
  - メモリ使用量が500MB以下
  - 全データが正常に出力される

#### TC-301-203: 極端に長い文字列
- **テスト目的**: 長い社員名・部門名での動作確認
- **前提条件**:
  ```python
  long_name_data = AttendanceSummary(
      employee_name="あ" * 1000,  # 1000文字の名前
      department="部" * 500       # 500文字の部門名
  )
  ```
- **期待結果**: データが適切にエスケープされて出力される

#### TC-301-204: 特殊文字を含むデータ
- **テスト目的**: CSV区切り文字・改行文字を含むデータの処理
- **前提条件**:
  ```python
  special_char_data = AttendanceSummary(
      employee_name='田中,太郎\n"課長"',  # カンマ、改行、クォート
      department="開発\r\n部"             # 改行コード
  )
  ```
- **期待結果**: 適切にクォート・エスケープされて出力される

#### TC-301-205: 日付境界値
- **テスト目的**: 月末日・うるう年での日付処理
- **前提条件**:
  - 2月29日（うるう年）のデータ
  - 1月31日から2月1日をまたがるデータ
- **期待結果**: 日付フォーマットが正確に適用される

#### TC-301-206: ゼロ値データ
- **テスト目的**: すべての数値がゼロの場合の動作
- **前提条件**:
  ```python
  zero_data = AttendanceSummary(
      attendance_days=0,
      total_work_minutes=0,
      overtime_minutes=0
  )
  ```
- **期待結果**: ゼロ値が正しい数値フォーマットで出力される

### 4. 統合テストケース

#### TC-301-301: 3種類レポート同時出力
- **テスト目的**: 社員別・部門別・日別詳細の3つのレポートを同時生成
- **前提条件**: 各レポート用のテストデータセット
- **期待結果**: 3つのCSVファイルが全て正常に生成される

#### TC-301-302: 設定変更後の出力
- **テスト目的**: 設定ファイル変更が即座に反映される
- **前提条件**:
  1. デフォルト設定でCSV出力
  2. csv_format.yamlの設定変更
  3. 再度CSV出力
- **期待結果**: 変更された設定が2回目の出力に反映される

#### TC-301-303: マルチスレッド環境での動作
- **テスト目的**: 複数スレッドから同時にCSV出力した場合の安全性
- **前提条件**: 3つのスレッドから同時にexport_employee_report()を呼び出し
- **期待結果**:
  - 全てのファイルが正常に生成される
  - データの欠損や破損がない
  - ファイル名の衝突が適切に処理される

### 5. パフォーマンステストケース

#### TC-301-401: メモリ使用量テスト
- **テスト目的**: 大容量データ処理時のメモリ使用量測定
- **測定指標**:
  - ピークメモリ使用量
  - メモリリーク有無
  - ガベージコレクション回数

#### TC-301-402: 処理時間計測テスト
- **テスト目的**: データ量別の処理時間測定
- **測定パターン**:
  - 10名×1か月: 1秒以内
  - 100名×1か月: 5秒以内  
  - 1000名×1か月: 30秒以内

#### TC-301-403: 並行処理テスト
- **テスト目的**: 複数レポートの並行生成性能
- **期待結果**: シーケンシャル実行の70%以内の時間で完了

## テストデータ準備

### 標準テストデータセット

```python
# tests/fixtures/csv_export/standard_employee_data.py
STANDARD_EMPLOYEE_DATA = [
    AttendanceSummary(
        employee_id="EMP001",
        employee_name="田中太郎",
        department="開発部",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        total_days=31,
        business_days=22,
        attendance_days=20,
        attendance_rate=90.9,
        total_work_minutes=9600,
        overtime_minutes=1200,
        tardiness_count=2,
        paid_leave_days=1
    ),
    # ... 他のテストデータ
]
```

### テストファイル構造

```
tests/
├── unit/
│   └── output/
│       ├── __init__.py
│       ├── test_csv_exporter.py
│       ├── test_export_result.py
│       └── test_format_validator.py
├── integration/
│   └── test_csv_export_integration.py
└── fixtures/
    └── csv_export/
        ├── standard_employee_data.py
        ├── department_data.py
        ├── daily_detail_data.py
        └── expected_outputs/
            ├── employee_report_2024_01.csv
            ├── department_report_2024_01.csv
            └── daily_detail_2024_01.csv
```

## テスト実行環境

### 必要なモック

```python
# ファイルシステム操作のモック
@patch('pathlib.Path.mkdir')
@patch('pathlib.Path.exists')  
@patch('pandas.DataFrame.to_csv')

# 設定ファイル読み込みのモック
@patch('attendance_tool.utils.config.ConfigManager.get_csv_format')

# 日時のモック
@patch('attendance_tool.output.csv_exporter.datetime')
```

### テスト実行コマンド

```bash
# 単体テスト実行
pytest tests/unit/output/ -v

# 統合テスト実行
pytest tests/integration/test_csv_export_integration.py -v

# パフォーマンステスト実行
pytest tests/performance/test_csv_export_performance.py -v --durations=10

# カバレッジ測定
pytest tests/unit/output/ --cov=src/attendance_tool/output --cov-report=html
```

## 成功基準

- **単体テスト**: すべてのテストケースが成功
- **テストカバレッジ**: 95%以上
- **統合テスト**: エンドツーエンドでの正常動作確認
- **パフォーマンス**: 規定の処理時間・メモリ使用量以内
- **エラーハンドリング**: 全ての異常系で適切な処理が実行される