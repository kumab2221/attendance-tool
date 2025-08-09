# TASK-302: Excelレポート出力 - 詳細要件定義

## 概要

勤怠集計結果をExcel形式（.xlsx）でエクスポートする機能を実装する。社員別・部門別・サマリーのワークシートを分割し、セル書式設定・自動幅調整・グラフ機能を含む高品質なExcelレポートを提供する。

## 要件リンク

- **REQ-012**: Excel出力機能
- **REQ-009**: 社員別集計出力（Excel形式）
- **REQ-010**: 部門別集計出力（Excel形式）

## アクセプタンスクライテリア

### 1. 社員別Excelワークシート

**Given**: 勤怠集計結果データ（AttendanceSummaryリスト）が存在する
**When**: Excel出力を実行する
**Then**: 以下の条件を満たすExcelファイルが生成される

- ファイル名: `attendance_report_{year}_{month}.xlsx`
- ワークシート名: `社員別レポート`
- 必須カラム: CSV出力と同等の13カラム
- セル書式:
  - ヘッダー行: 太字、背景色（薄いブルー）
  - 数値列: 適切な数値フォーマット（小数点桁数指定）
  - 日付列: YYYY-MM-DD形式
- 自動幅調整: 全カラムがコンテンツに適した幅に調整
- 罫線: 全セルに薄いグレーの罫線

### 2. 部門別Excelワークシート

**Given**: 部門別集計結果データ（DepartmentSummaryリスト）が存在する
**When**: Excel出力を実行する
**Then**: 以下の条件を満たすワークシートが同一ファイル内に作成される

- ワークシート名: `部門別レポート`
- 必須カラム: CSV出力と同等の8カラム
- 条件付き書式: 平均出勤率に基づく色分け
  - 95%以上: 緑色背景
  - 90-95%: 黄色背景
  - 90%未満: 赤色背景

### 3. サマリーワークシート

**Given**: 社員別・部門別データが存在する
**When**: Excel出力を実行する
**Then**: 以下の条件を満たすサマリーワークシートが作成される

- ワークシート名: `サマリー`
- 集計情報:
  - 総従業員数
  - 総出勤日数
  - 平均出勤率
  - 総残業時間
  - 部門数
- グラフ:
  - 部門別出勤率の棒グラフ
  - 残業時間の円グラフ（オプション）

### 4. Excel固有機能

**Given**: Excelファイルが生成される
**When**: ファイルをExcelアプリケーションで開く
**Then**: 以下の機能が正常に動作する

- フィルター機能: ヘッダー行に自動フィルターを設定
- 固定表示: ヘッダー行を固定表示
- 印刷設定: A4サイズに最適化された印刷レイアウト
- ワークシート保護: 数式セルの保護（オプション）

### 5. 大容量データ対応

**Given**: 1000名×1か月分の勤怠データが存在する
**When**: Excel出力を実行する
**Then**: 以下の性能基準を満たす

- メモリ使用量: 1GB以下
- 処理時間: 60秒以内
- ファイル生成成功
- ファイルサイズ: 20MB以下

### 6. Excel互換性

**Given**: 生成されたExcelファイル
**When**: 様々なExcelバージョンで開く
**Then**: 以下の互換性を確保する

- Microsoft Excel 2016以降: 完全対応
- LibreOffice Calc: 基本機能対応
- Google Sheets: インポート可能

### 7. エラーハンドリング

**Given**: 様々な異常ケースが発生する
**When**: Excel出力を実行する
**Then**: 適切なエラーハンドリングが行われる

- メモリ不足: 適切なエラーメッセージと部分保存
- ファイル破損: 一時ファイルからの復旧
- 書式エラー: デフォルト書式での継続
- 権限エラー: CSV出力との統一的な処理

## 技術仕様

### 使用技術

- **openpyxl**: Excel (.xlsx) ファイルの作成・編集
- **pandas**: データフレーム操作とExcelWriter連携
- **datetime**: 日付フォーマット処理
- **logging**: 処理ログ出力
- **pathlib**: ファイルパス操作

### データフロー

1. 入力データの検証（CSVExporter と共通ヘルパー使用）
2. Excelブック作成
3. ワークシート別データ変換・書き込み
4. セル書式設定・自動調整
5. グラフ・チャート追加（オプション）
6. ファイル保存・検証

### パフォーマンス要件

- **処理時間**: 100名分データを10秒以内
- **メモリ使用量**: データ量の5倍以下
- **同時出力**: CSV出力と並行実行可能

### セキュリティ要件

- **個人情報保護**: CSV出力と同等の保護レベル
- **ファイル権限**: 適切な読み取り専用権限を設定
- **一時ファイル**: 安全な一時ファイル処理

## インターフェース設計

### ExcelExporter クラス

```python
class ExcelExporter:
    def export_excel_report(
        self, 
        employee_summaries: List[AttendanceSummary],
        department_summaries: List[DepartmentSummary],
        output_path: Path,
        year: int,
        month: int,
        include_charts: bool = False
    ) -> ExportResult
    
    def export_employee_worksheet(
        self, 
        workbook: Workbook,
        summaries: List[AttendanceSummary]
    ) -> None
    
    def export_department_worksheet(
        self, 
        workbook: Workbook,
        summaries: List[DepartmentSummary]
    ) -> None
    
    def export_summary_worksheet(
        self, 
        workbook: Workbook,
        employee_summaries: List[AttendanceSummary],
        department_summaries: List[DepartmentSummary]
    ) -> None
```

### ExcelExportConfig クラス

```python
@dataclass
class ExcelExportConfig:
    filename_pattern: str
    worksheet_names: Dict[str, str]
    header_style: Dict[str, Any]
    cell_formats: Dict[str, str]
    conditional_formats: List[ConditionalFormat]
    chart_settings: Dict[str, Any]
```

### ConditionalFormat クラス

```python
@dataclass
class ConditionalFormat:
    column: str
    condition_type: str  # "between", "greater_than", etc.
    values: List[Any]
    format_style: Dict[str, Any]
```

## テストケース

### 単体テスト
- Excel形式の正確性検証
- ワークシート構造確認
- セル書式設定検証
- グラフ生成テスト

### 統合テスト
- 大容量データ処理
- 複数ワークシート生成
- ファイル互換性確認

### 境界値テスト
- 最大ワークシート数
- 最大行数（Excel制限）
- メモリ使用量上限

## CSV出力機能との統合

### 共通インターフェース

```python
class ReportExporter:
    """統合レポート出力機能"""
    
    def __init__(self):
        self.csv_exporter = CSVExporter()
        self.excel_exporter = ExcelExporter()
    
    def export_reports(
        self,
        employee_summaries: List[AttendanceSummary],
        department_summaries: List[DepartmentSummary],
        output_path: Path,
        year: int,
        month: int,
        formats: List[str] = ["csv", "excel"]
    ) -> Dict[str, ExportResult]:
        results = {}
        if "csv" in formats:
            results["csv"] = self._export_csv(...)
        if "excel" in formats:
            results["excel"] = self._export_excel(...)
        return results
```

### 共通ヘルパーメソッドの再利用

- `_safe_get_value()`: データバリデーション
- `_minutes_to_hours()`: 時間換算
- `_format_period_string()`: 期間フォーマット
- `_handle_export_error()`: エラーハンドリング

## 完了条件

- [ ] 3種類のワークシート出力機能が正常動作
- [ ] セル書式設定・自動幅調整機能実装
- [ ] グラフ・チャート機能実装（基本）
- [ ] Excel互換性確認（2016以降）
- [ ] エラーハンドリング実装
- [ ] パフォーマンス基準達成
- [ ] テストカバレッジ95%以上
- [ ] CSV出力機能との統合
- [ ] ドキュメント更新完了

## 依存関係

- **前提条件**: TASK-301（CSV出力機能）が完了済み
- **入力データ**: AttendanceSummary, DepartmentSummary
- **共通ライブラリ**: CSVExporter のヘルパーメソッド再利用
- **出力先**: output/ ディレクトリ

## 非機能要件

### 拡張性
- 新しいワークシート形式の追加が容易
- カスタムチャート機能の拡張可能性
- テンプレート機能（TASK-303）への対応準備

### 保守性
- CSV出力機能と統一されたアーキテクチャ
- 設定ファイルによる柔軟なカスタマイズ
- ログ出力による運用支援

### 運用性
- 大容量データでの安定動作
- エラー発生時の適切な復旧手順
- ファイル破損時の検出・通知機能

## 備考

- Excel出力はCSV出力の上位互換として位置づけ
- 将来のBI連携を考慮したデータ構造設計
- 国際化対応（多言語ヘッダー）への拡張可能性を確保