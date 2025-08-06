# 勤怠管理自動集計ツール (Attendance Tool)

勤怠データのCSVファイルを自動集計し、社員別・部門別レポートを生成するPythonツールです。

## 機能概要

- CSVファイルからの勤怠データ読み込み・検証
- 月単位・期間指定での勤怠集計
- 出勤・欠勤・遅刻・早退・残業時間の自動計算
- 就業規則に基づく労働時間の集計
- CSV・Excel形式でのレポート出力
- エラーハンドリング・異常値検出機能

## 必要環境

- Python 3.8以上
- Windows 10/11
- メモリ: 1GB以上
- ディスク容量: 100MB以上

## インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd attendance-tool
```

### 2. 仮想環境の作成

```bash
python -m venv venv
```

### 3. 仮想環境の有効化

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 開発環境の場合

```bash
pip install -r requirements-dev.txt
```

## 使用方法

### 基本的な使用方法

```bash
# 月単位集計
attendance-tool --input data/attendance.csv --output output/report.csv --month 2024-03

# 期間指定集計
attendance-tool --input data/attendance.csv --output output/report.csv --start 2024-03-01 --end 2024-03-31

# Excel形式での出力
attendance-tool --input data/attendance.csv --output output/report.xlsx --month 2024-03
```

### 入力CSVファイル形式

必要なカラム:
- `社員ID`: 社員の識別子
- `氏名`: 社員名
- `部署`: 所属部門
- `日付`: 出勤日 (YYYY-MM-DD形式)
- `出勤時刻`: 出勤時間 (HH:MM形式)
- `退勤時刻`: 退勤時間 (HH:MM形式)

例:
```csv
社員ID,氏名,部署,日付,出勤時刻,退勤時刻
E001,田中太郎,営業部,2024-03-01,09:00,18:00
E002,佐藤花子,開発部,2024-03-01,09:30,19:15
```

## 設定

設定ファイルは `config/` ディレクトリに配置します:

- `work_rules.yaml`: 就業規則の設定
- `csv_format.yaml`: CSVフォーマットの設定
- `logging.yaml`: ログ出力の設定

## プロジェクト構造

```
attendance-tool/
├── src/
│   └── attendance_tool/
│       ├── cli/          # CLIインターフェース
│       ├── models/       # データモデル
│       ├── services/     # ビジネスロジック
│       ├── utils/        # ユーティリティ
│       └── reports/      # レポート生成
├── tests/               # テストコード
│   ├── unit/           # 単体テスト
│   ├── integration/    # 統合テスト
│   └── fixtures/       # テストデータ
├── config/             # 設定ファイル
├── data/               # サンプルデータ
├── output/             # 出力ファイル
└── docs/               # ドキュメント
```

## 開発

### テストの実行

```bash
pytest
```

### コードフォーマット

```bash
black src tests
isort src tests
```

### 型チェック

```bash
mypy src
```

### リンター

```bash
flake8 src tests
```

## トラブルシューティング

### よくある問題

1. **ファイルが見つからないエラー**
   - 入力ファイルパスが正しいか確認してください
   - ファイルの読み込み権限を確認してください

2. **CSVフォーマットエラー**
   - 必要なカラムが存在するか確認してください
   - 文字エンコーディング（UTF-8）を確認してください

3. **メモリ不足エラー**
   - 大容量ファイルの場合、チャンク処理が自動的に行われます
   - システムメモリが1GB以上あることを確認してください

## ライセンス

MIT License

## 貢献

バグ報告や機能要望は Issue でお知らせください。
プルリクエストも歓迎します。

## 更新履歴

### v0.1.0 (開発中)
- 初期リリース準備
- 基本的な勤怠集計機能
- CSV/Excel出力機能