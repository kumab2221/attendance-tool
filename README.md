# 勤怠管理自動集計ツール (Attendance Tool) 🕒

> **CSV形式の勤怠データを自動集計し、社員別・部門別レポートを生成するPythonツール**

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/Coverage-89%25-brightgreen.svg)](docs/testing/COVERAGE_REPORT.md)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](dist/)

## 🚀 クイックスタート（新メンバー向け）

### ⚡ 30秒でお試し！

```bash
# 1. リポジトリクローン
git clone <repository-url>
cd attendance-tool

# 2. 実行ファイルで即座にテスト（Windows）
dist/attendance-tool-cli.exe --version

# 3. または開発環境セットアップ
python -m venv venv
venv\Scripts\activate  # Windows
pip install -e .

# 4. サンプル実行
attendance-tool --help
```

**🎯 すぐに試したい？** → [📖 5分間チュートリアル](#-5分間チュートリアル) へジャンプ！

---

## 📋 目次

- [🎯 プロジェクト概要](#-プロジェクト概要)
- [⚡ インストール](#-インストール)
- [📖 5分間チュートリアル](#-5分間チュートリアル)
- [🛠️ 開発環境セットアップ](#️-開発環境セットアップ)
- [📚 ドキュメント](#-ドキュメント)
- [🤝 コントリビューション](#-コントリビューション)
- [❓ ヘルプ・サポート](#-ヘルプサポート)

---

## 🎯 プロジェクト概要

### ✨ 主な機能

| 機能 | 説明 | 状態 |
|------|------|------|
| 📥 **CSV読み込み** | 勤怠データの自動読み込み・検証 | ✅ |
| 📊 **自動集計** | 出勤・残業・有給等の自動計算 | ✅ |
| 📈 **レポート生成** | CSV・Excel形式での詳細レポート | ✅ |
| 🏢 **部門別分析** | 部門単位での統計・比較 | ✅ |
| ⚠️ **異常値検出** | データ不整合・エラーの自動検出 | ✅ |
| 🖥️ **GUI・CLI** | 使いやすいインターフェース | ✅ |

### 🏗️ アーキテクチャ

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CSV入力       │───▶│   データ処理     │───▶│  レポート出力   │
│                 │    │                 │    │                 │
│ • 勤怠データ    │    │ • 検証・クレンジ │    │ • CSV・Excel   │
│ • 社員マスター  │    │ • 集計・計算     │    │ • 社員別・部門別│
│ • 就業規則      │    │ • エラー処理     │    │ • 統計・分析    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 📊 品質指標

- **✅ テストカバレッジ**: 89.2%
- **✅ 実装完了**: 25/25 タスク
- **✅ テストケース**: 180個
- **✅ パフォーマンス**: 100名×1ヶ月 < 5分

---

## ⚡ インストール

### 🎯 方法1: 実行ファイル（推奨・初回体験）

```bash
# Windows用実行ファイルダウンロード
# 1. dist/attendance-tool-cli.exe (コマンドライン版)
# 2. dist/attendance-tool-gui.exe (GUI版)

# 即座に実行
dist/attendance-tool-cli.exe --version
dist/attendance-tool-gui.exe
```

### 🔧 方法2: Python開発環境（カスタマイズ・開発用）

#### 前提条件
- **Python**: 3.8以上
- **OS**: Windows 10/11, macOS, Linux
- **メモリ**: 1GB以上
- **ディスク**: 500MB以上

#### セットアップ手順

```bash
# 1. プロジェクトクローン
git clone <repository-url>
cd attendance-tool

# 2. 仮想環境作成・アクティベート
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate

# 3. 依存関係インストール
pip install -e .

# 4. 動作確認
attendance-tool --version
```

### 🧪 開発者向け追加セットアップ

```bash
# 開発用依存関係
pip install -r requirements-dev.txt

# pre-commitフック（推奨）
pre-commit install

# テスト実行確認
pytest tests/ -v

# 品質チェック
pytest tests/ --cov=attendance_tool --cov-report=html
```

---

## 📖 5分間チュートリアル

### ステップ1️⃣: サンプルデータ準備

```bash
# サンプルCSVファイルを作成
cat > sample_attendance.csv << EOF
社員ID,氏名,部署,日付,出勤時刻,退勤時刻
E001,田中太郎,営業部,2024-01-15,09:00,18:00
E002,佐藤花子,開発部,2024-01-15,09:30,19:15
E003,鈴木次郎,人事部,2024-01-15,08:45,17:45
EOF
```

### ステップ2️⃣: 基本的な集計実行

```bash
# CLI版での実行
attendance-tool process \
  --input sample_attendance.csv \
  --output report.csv \
  --month 2024-01
```

### ステップ3️⃣: 結果確認

```bash
# 結果ファイルの確認
cat report.csv

# Expected output:
# 社員ID,氏名,部署,出勤日数,総労働時間,残業時間,...
# E001,田中太郎,営業部,1,8.0,0.0,...
# E002,佐藤花子,開発部,1,8.75,0.75,...
```

### ステップ4️⃣: GUI版でのお試し

```bash
# GUI起動
attendance-tool-gui
# または
dist/attendance-tool-gui.exe

# GUI操作:
# 1. ファイル選択ボタンでsample_attendance.csvを選択
# 2. 出力設定で形式・フォルダを指定
# 3. 実行ボタンをクリック
```

### 🎉 おめでとうございます！

5分間で基本的な勤怠集計を体験できました。
次は [📚 詳細ドキュメント](#-ドキュメント) で機能を深く理解しましょう。

---

## 🛠️ 開発環境セットアップ

### 🏗️ 開発者向け完全セットアップ

```bash
# 1. プロジェクトセットアップ
git clone <repository-url>
cd attendance-tool
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 2. 開発依存関係インストール
pip install -e .
pip install -r requirements-dev.txt

# 3. 開発ツールセットアップ
pre-commit install          # Git hooks
pytest --version           # テストランナー確認
black --version            # フォーマッター確認
mypy --version             # 型チェッカー確認

# 4. IDE設定（VS Code推奨）
code ./.vscode/settings.json  # エディタ設定確認
```

### 🧪 開発ワークフロー

```bash
# 日常的な開発サイクル
# 1. 機能開発
git checkout -b feature/new-feature

# 2. コード品質チェック
black src tests             # コードフォーマット
isort src tests            # import整理
mypy src                   # 型チェック
flake8 src tests          # リンター

# 3. テスト実行
pytest tests/unit/ -v      # 単体テスト
pytest tests/integration/ # 統合テスト
pytest tests/e2e/         # E2Eテスト

# 4. カバレッジ確認
pytest tests/ --cov=attendance_tool --cov-report=html
open htmlcov/index.html    # カバレッジレポート確認

# 5. ビルドテスト
python build_scripts/build_exe.py  # 実行ファイル作成テスト

# 6. コミット・プッシュ
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

### 📁 重要なディレクトリ構造

```
attendance-tool/
├── 📁 src/attendance_tool/     # 📌 メインソースコード
│   ├── cli/                   # CLI インターフェース
│   ├── gui/                   # GUI インターフェース  
│   ├── calculation/           # 勤怠計算エンジン
│   ├── validation/            # データ検証
│   ├── output/               # レポート出力
│   └── utils/                # ユーティリティ
├── 📁 tests/                  # 📌 テストコード（重要！）
│   ├── unit/                 # 単体テスト
│   ├── integration/          # 統合テスト
│   ├── e2e/                  # E2Eテスト
│   └── fixtures/             # テストデータ
├── 📁 docs/                   # 📌 ドキュメント
│   ├── testing/              # テスト関連ドキュメント
│   ├── release/              # リリース関連
│   └── spec/                 # 要件仕様
├── 📁 config/                 # 設定ファイル
├── 📁 build_scripts/          # ビルド・配布スクリプト
└── 📁 dist/                   # 📌 配布用実行ファイル
```

---

## 📚 ドキュメント

### 📖 新メンバー必読ドキュメント

| 順序 | ドキュメント | 対象 | 所要時間 | 説明 |
|------|-------------|------|----------|------|
| 1️⃣ | [📋 このREADME](#) | 全員 | 10分 | プロジェクト全体像 |
| 2️⃣ | [🎯 要件仕様書](docs/spec/attendance-tool-requirements.md) | 全員 | 20分 | 機能要件の理解 |
| 3️⃣ | [🏗️ アーキテクチャ](docs/design/attendance-tool/architecture.md) | 開発者 | 15分 | 設計思想の理解 |
| 4️⃣ | [🧪 テストガイド](docs/testing/README.md) | 開発者 | 15分 | テスト戦略の理解 |
| 5️⃣ | [📋 タスク一覧](docs/tasks/attendance-tool-tasks.md) | PM・リーダー | 30分 | プロジェクト進捗 |

### 🎯 役割別推奨ドキュメント

#### 👨‍💻 **開発者（エンジニア）**
```
📚 推奨学習パス（初日〜1週間）

Day 1: プロジェクト理解
├── README.md（このファイル）         ✅ 10分
├── 要件仕様書                        ✅ 20分
└── アーキテクチャドキュメント         ✅ 15分

Day 2-3: 開発環境・テスト
├── 開発環境セットアップ               ✅ 30分
├── テスト実行ガイド                  ✅ 30分
└── コードレビューガイドライン         ✅ 15分

Day 4-5: 実装理解
├── 主要モジュールのコードリーディング  📖 2時間
├── TDDドキュメント確認              📖 1時間
└── 小さなタスクで実装体験            🔨 半日

Week 1 End: 貢献開始
└── 実際のタスクアサイン・実装開始     🚀
```

#### 👨‍💼 **マネージャー・PM**
- [📊 プロジェクト進捗](docs/tasks/attendance-tool-tasks.md)
- [📈 品質レポート](docs/testing/COVERAGE_REPORT.md)
- [📋 リリースノート](docs/release/RELEASE_NOTES_v0.1.0.md)
- [📋 配布ガイド](docs/release/DISTRIBUTION_GUIDE.md)

#### 🔍 **QA・テスター**
- [🧪 テスト戦略](docs/testing/TEST_STRATEGY.md)
- [📊 テスト実行ガイド](docs/testing/TEST_EXECUTION_GUIDE.md)
- [🗺️ テスト・機能対応表](docs/testing/TEST_MAPPING.md)

#### 📝 **テクニカルライター・ドキュメンテーション**
- [📖 ドキュメント構造](docs/)
- [📋 API仕様](docs/design/attendance-tool/interfaces.ts)
- [📊 ユーザーガイド](docs/gui_usage.md)

### 🔗 クイックリンク

| カテゴリ | リンク | 説明 |
|----------|--------|------|
| **🚀 始める** | [セットアップ](#-インストール) | 環境構築 |
| **📖 学ぶ** | [チュートリアル](#-5分間チュートリアル) | 基本操作 |
| **🔧 開発** | [開発ガイド](#️-開発環境セットアップ) | 開発環境 |
| **🧪 テスト** | [テストガイド](docs/testing/) | 品質保証 |
| **📊 品質** | [カバレッジレポート](docs/testing/COVERAGE_REPORT.md) | 品質状況 |
| **🚢 リリース** | [配布ガイド](docs/release/) | 配布・展開 |

---

## 🤝 コントリビューション

### 🎯 貢献方法

我々は新しいコントリビューターを **大歓迎** しています！

#### 🔰 初回コントリビューター向け

1. **🍴 Fork & Clone**
   ```bash
   # GitHubでFork後
   git clone https://github.com/YOUR_USERNAME/attendance-tool.git
   cd attendance-tool
   ```

2. **🛠️ 環境セットアップ**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -e .
   pip install -r requirements-dev.txt
   pre-commit install
   ```

3. **🌿 ブランチ作成**
   ```bash
   git checkout -b feature/your-feature-name
   # または
   git checkout -b fix/issue-number
   ```

4. **✨ 実装・テスト**
   ```bash
   # 実装
   # ...

   # テスト
   pytest tests/ -v
   
   # 品質チェック
   black src tests
   mypy src
   flake8 src tests
   ```

5. **📝 コミット・PR**
   ```bash
   git add .
   git commit -m "feat: add awesome feature"
   git push origin feature/your-feature-name
   # GitHub上でPull Request作成
   ```

#### 🏷️ コミットメッセージ規則

```bash
# フォーマット
type(scope): description

# 例
feat(calculation): add overtime calculation for holidays
fix(csv-reader): handle empty lines in CSV files
docs(readme): improve installation instructions
test(validation): add unit tests for date validation
```

**タイプ**:
- `feat`: 新機能
- `fix`: バグ修正  
- `docs`: ドキュメント
- `test`: テスト追加/修正
- `refactor`: リファクタリング
- `style`: スタイル修正
- `perf`: パフォーマンス改善

#### 🎯 良いPRの条件

- ✅ **目的が明確** - 何を解決するか明記
- ✅ **テスト追加** - 新機能にはテストを含む
- ✅ **ドキュメント更新** - 必要に応じてドキュメント更新  
- ✅ **品質チェック通過** - CI通過
- ✅ **適切なサイズ** - 1PR = 1機能（巨大なPRは避ける）

### 🐛 Issue報告

#### バグレポート
```markdown
## バグ概要
[簡潔な説明]

## 再現手順
1. ...
2. ...
3. ...

## 期待結果
[期待していた動作]

## 実際の結果  
[実際に起きたこと]

## 環境
- OS: Windows 10
- Python: 3.9
- バージョン: v0.1.0

## 追加情報
[スクリーンショット、ログ等]
```

#### 機能要望
```markdown
## 機能概要
[提案する機能の概要]

## 動機・背景
[なぜこの機能が必要か]

## 提案する解決方法
[具体的な実装案]

## 代替案
[他の解決方法があれば]
```

---

## ❓ ヘルプ・サポート

### 🆘 困った時の対処法

#### 1️⃣ **まず確認すること**

| 問題 | 確認項目 | 解決策 |
|------|----------|--------|
| **インストールエラー** | Python バージョン | Python 3.8+ を使用 |
| **コマンドが見つからない** | 仮想環境アクティベート | `venv\Scripts\activate` |
| **テスト失敗** | 依存関係 | `pip install -r requirements-dev.txt` |
| **権限エラー** | ファイル権限 | 管理者権限で実行 |

#### 2️⃣ **情報収集**

```bash
# 環境情報収集
python --version
pip list | grep attendance
attendance-tool --version

# ログ確認
ls logs/
cat logs/attendance-tool.log

# テスト実行
pytest tests/ -v --tb=short
```

#### 3️⃣ **サポートチャンネル**

| 方法 | 用途 | レスポンス目安 |
|------|------|----------------|
| **🔍 既存Issue検索** | よくある問題 | 即座 |
| **📝 GitHub Issues** | バグ報告・機能要望 | 1-3日 |
| **💬 Discussions** | 質問・議論 | 数時間-1日 |
| **📧 メール** | 機密事項・個別相談 | 1-2日 |

#### 4️⃣ **よくある質問（FAQ）**

<details>
<summary><strong>Q: CSVファイルが読み込めません</strong></summary>

**A: 以下を確認してください:**
- ファイルエンコーディングがUTF-8か
- 必要なカラムが存在するか
- ファイルパスが正しいか

```bash
# エンコーディング確認
file -i your_file.csv

# ファイル内容確認  
head -5 your_file.csv
```
</details>

<details>
<summary><strong>Q: メモリ不足エラーが発生します</strong></summary>

**A: 大容量データの場合:**
- チャンクサイズを小さくする: `--chunk-size 500`
- 不要なデータを事前に削除
- システムメモリを増やす

```bash
# チャンクサイズ指定
attendance-tool process --input large_file.csv --chunk-size 500
```
</details>

<details>
<summary><strong>Q: テストが失敗します</strong></summary>

**A: 以下を試してください:**
```bash
# テスト環境リセット
rm -rf .pytest_cache/ __pycache__/
pip install -r requirements-dev.txt

# 個別テスト実行
pytest tests/unit/test_csv_reader.py -v

# 詳細ログ表示
pytest tests/ -v -s --log-cli-level=DEBUG
```
</details>

### 📞 **緊急サポート**

**重要な問題やセキュリティ関連**:
- 📧 security@company.com
- 🔒 プライベートで報告してください

---

## 📜 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

---

## 👥 貢献者

このプロジェクトは多くの貢献者によって支えられています。

<!-- Contributors will be automatically added here -->

---

## 📈 プロジェクト統計

- **📊 コードライン**: ~15,000行
- **🧪 テストケース**: 180個
- **📦 依存関係**: 12個
- **📚 ドキュメント**: 20+ファイル
- **⚡ パフォーマンス**: 100名×1ヶ月 < 5分

---

## 🎉 最後に

新しいメンバーとしてプロジェクトに参加いただき、ありがとうございます！

**🎯 Next Steps:**
1. ⭐ このリポジトリにStarをつけてください
2. 📖 [5分間チュートリアル](#-5分間チュートリアル) を試してください
3. 🛠️ [開発環境をセットアップ](#️-開発環境セットアップ) してください
4. 💬 質問があればお気軽に [Issues](../../issues) でお聞きください

**Happy Coding! 🚀**

---

<div align="center">

**勤怠管理自動集計ツール** ❤️ **Contributors**

Built with ❤️ by the development team

</div>