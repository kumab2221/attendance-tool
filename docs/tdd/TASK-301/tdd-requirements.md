# TASK-301: CSVレポート出力 - 詳細要件定義

## 概要

勤怠集計結果を各種CSV形式でエクスポートする機能を実装する。社員別レポート、部門別レポート、日別詳細レポートの3種類のCSV出力に対応し、UTF-8エンコーディングでの出力とカスタムヘッダー・フォーマット機能を提供する。

## 要件リンク

- **REQ-011**: CSV出力機能
- **REQ-009**: 社員別集計出力
- **REQ-010**: 部門別集計出力

## アクセプタンスクライテリア

### 1. 社員別CSVレポート出力

**Given**: 勤怠集計結果データ（AttendanceSummaryリスト）が存在する
**When**: 社員別CSVレポート出力を実行する
**Then**: 以下の条件を満たすCSVファイルが生成される

- ファイル名: `employee_report_{year}_{month}.csv`
- エンコーディング: UTF-8（BOM付き）
- 区切り文字: カンマ
- 必須カラム:
  - 社員ID, 氏名, 部署, 対象年月
  - 出勤日数, 欠勤日数, 遅刻回数, 早退回数
  - 総労働時間, 所定労働時間, 残業時間, 深夜労働時間
  - 有給取得日数

### 2. 部門別CSVレポート出力

**Given**: 部門別集計結果データ（DepartmentSummaryリスト）が存在する
**When**: 部門別CSVレポート出力を実行する
**Then**: 以下の条件を満たすCSVファイルが生成される

- ファイル名: `department_report_{year}_{month}.csv`
- エンコーディング: UTF-8（BOM付き）
- 必須カラム:
  - 部署, 対象年月, 所属人数
  - 総出勤日数, 総欠勤日数, 総労働時間, 総残業時間
  - 平均出勤率

### 3. 日別詳細CSVレポート出力

**Given**: 日別勤怠詳細データが存在する
**When**: 日別詳細CSVレポート出力を実行する
**Then**: 以下の条件を満たすCSVファイルが生成される

- ファイル名: `daily_detail_{year}_{month}.csv`
- エンコーディング: UTF-8（BOM付き）
- 必須カラム:
  - 社員ID, 氏名, 部署, 勤務日
  - 出勤時刻, 退勤時刻, 休憩時間, 労働時間, 残業時間
  - 遅刻時間, 早退時間, 勤務状態

### 4. カスタムフォーマット対応

**Given**: CSV出力設定（config/csv_format.yaml）が存在する
**When**: CSV出力を実行する
**Then**: 設定ファイルに従ったフォーマットでファイルが生成される

- ヘッダー名のカスタマイズ
- 数値フォーマット（小数点桁数）の適用
- エンコーディング設定の反映

### 5. 大容量データ対応

**Given**: 1000名×1か月分の勤怠データが存在する
**When**: CSV出力を実行する
**Then**: 以下の性能基準を満たす

- メモリ使用量: 500MB以下
- 処理時間: 30秒以内
- ファイル生成成功

### 6. エラーハンドリング

**Given**: 様々な異常ケースが発生する
**When**: CSV出力を実行する
**Then**: 適切なエラーハンドリングが行われる

- 出力ディレクトリが存在しない場合の自動作成
- ディスク容量不足エラーの検出と通知
- ファイル書き込み権限エラーの処理
- 不正なデータ形式の検出とスキップ

## 技術仕様

### 使用技術

- **pandas**: CSV出力とデータフレーム操作
- **pathlib**: ファイルパス操作
- **datetime**: 日付フォーマット処理
- **logging**: 処理ログ出力
- **yaml**: 設定ファイル読み込み

### データフロー

1. 入力データの検証
2. 設定ファイルの読み込み
3. データの変換・フォーマット
4. CSV出力実行
5. 出力結果の検証

### パフォーマンス要件

- **処理時間**: 100名分データを5秒以内
- **メモリ使用量**: データ量の3倍以下
- **同時出力**: 3種類のレポートを並行生成可能

### セキュリティ要件

- **個人情報保護**: ログに個人情報を出力しない
- **ファイル権限**: 適切な読み取り専用権限を設定
- **データ暗号化**: 必要に応じてファイル暗号化対応

## インターフェース設計

### CSVExporter クラス

```python
class CSVExporter:
    def export_employee_report(
        self, 
        summaries: List[AttendanceSummary], 
        output_path: Path,
        year: int,
        month: int
    ) -> ExportResult
    
    def export_department_report(
        self, 
        summaries: List[DepartmentSummary], 
        output_path: Path,
        year: int,
        month: int
    ) -> ExportResult
    
    def export_daily_detail_report(
        self, 
        records: List[AttendanceRecord], 
        output_path: Path,
        year: int,
        month: int
    ) -> ExportResult
```

### ExportResult クラス

```python
@dataclass
class ExportResult:
    success: bool
    file_path: Path
    record_count: int
    file_size: int
    processing_time: float
    errors: List[str]
```

## テストケース

### 単体テスト
- CSV形式の正確性検証
- エンコーディング確認
- 数値フォーマット検証
- エラーケース処理

### 統合テスト
- 大容量データ処理
- 複数レポート同時出力
- 設定ファイル連携

### 境界値テスト
- 空データセット
- 最大データ量
- ファイルサイズ上限

## 完了条件

- [ ] 3種類のCSV出力機能が正常動作
- [ ] UTF-8エンコーディング対応完了
- [ ] カスタムフォーマット機能実装
- [ ] エラーハンドリング実装
- [ ] パフォーマンス基準達成
- [ ] テストカバレッジ95%以上
- [ ] ドキュメント更新完了

## 依存関係

- **前提条件**: TASK-203（部門別集計機能）が完了済み
- **入力データ**: AttendanceSummary, DepartmentSummary, AttendanceRecord
- **設定ファイル**: config/csv_format.yaml
- **出力先**: output/ ディレクトリ

## 備考

- Excel互換性を考慮してBOM付きUTF-8を使用
- 将来のExcel出力機能（TASK-302）との連携を考慮した設計
- 国際化対応を見据えた多言語ヘッダー対応の検討