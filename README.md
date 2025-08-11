# 勤怠管理自動集計ツール (Attendance Tool) 🕒

> **CSV形式の勤怠データを自動集計し、社員別・部門別レポートを生成するPythonツール**

[![Python Version](https://img.shields.io/badge/Python-3.13%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Test Coverage](https://img.shields.io/badge/Coverage-89%25-brightgreen.svg)](docs/testing/COVERAGE_REPORT.md)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](dist/)

## 🚀 クイックスタート（新メンバー向け）

### ⚡ 30秒でお試し！

```bash
# 1. リポジトリクローン
git clone https://github.com/kumab2221/attendance-tool.git
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
- **✅ 循環的複雑度**: 閾値10以下維持
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
- **Python**: 3.13以上
- **OS**: Windows 10/11, macOS, Linux
- **メモリ**: 1GB以上
- **ディスク**: 500MB以上

#### セットアップ手順

```bash
# 1. プロジェクトクローン
git clone https://github.com/kumab2221/attendance-tool.git
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
git clone https://github.com/kumab2221/attendance-tool.git
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

# 3. コード複雑度チェック
make complexity              # 基本的な複雑度チェック
make complexity-report       # HTMLレポート生成
make complexity-ci          # CI用（閾値超過で失敗）

# 4. テスト実行
pytest tests/unit/ -v      # 単体テスト
pytest tests/integration/ # 統合テスト
pytest tests/e2e/         # E2Eテスト

# 5. カバレッジ確認
pytest tests/ --cov=attendance_tool --cov-report=html
open htmlcov/index.html    # カバレッジレポート確認

# 6. 品質レポート生成
make quality-report        # カバレッジ + 複雑度の統合レポート

# 7. ビルドテスト
python build_scripts/build_exe.py  # 実行ファイル作成テスト

# 8. コミット・プッシュ
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature
```

### 📏 コード品質管理

#### 🧮 循環的複雑度チェック（lizard）

コード品質の維持のため、循環的複雑度を継続的に監視しています。

```bash
# Unix/Linux/macOS
make complexity              # 基本的な複雑度チェック（閾値: 10）
make complexity-report       # 詳細なHTMLレポート生成
make complexity-ci          # CI用チェック（閾値超過で失敗）

# Windows（make.cmdまたはmake.batを使用）
.\make.cmd complexity        # 基本的な複雑度チェック
.\make.cmd complexity-report # HTMLレポート生成  
.\make.cmd complexity-ci     # CI用チェック

# 手動実行（全OS共通・カスタム閾値）
python scripts/complexity_check.py --threshold 15 --verbose
```

**生成場所**: `reports/complexity/complexity_report.html`

#### 📊 複雑度分布の目安

| 複雑度レベル | CCN範囲 | 状態 | 対応方針 |
|------------|---------|------|----------|
| **低** | 1-5 | ✅ 良好 | 維持 |
| **中** | 6-10 | ⚠️ 注意 | レビュー強化 |
| **高** | 11-20 | ❌ 要改善 | リファクタリング必須 |
| **超高** | 21+ | 🚫 禁止 | 即座に分割 |

#### 🔄 品質ゲート

```bash
# リリース前の必須チェック
make pre-release           # Unix/Linux/macOS
.\make.cmd pre-release     # Windows

# 実行内容:
# 1. コードフォーマット・リント (black, mypy, flake8)
# 2. 複雑度チェック (lizard, 閾値10)  
# 3. 全テスト実行 (unit + integration + e2e)
```

#### 📈 CI/CD品質チェック

GitHub Actionsで自動実行される品質チェック：

- **🔍 コードフォーマット**: black, isort
- **📝 静的解析**: mypy, flake8
- **🧮 複雑度チェック**: lizard（閾値15）
- **🔒 セキュリティスキャン**: bandit, safety
- **📏 保守性指数**: radon

レポートは各PR実行時にArtifactとしてダウンロード可能です。

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
├── 📁 scripts/                # 開発用スクリプト
│   └── complexity_check.py   # lizard複雑度チェックツール
├── 📁 reports/                # 📌 品質レポート出力先
│   └── complexity/           # 複雑度分析結果
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
| **🧮 複雑度** | [複雑度チェック](scripts/complexity_check.py) | コード複雑度 |
| **🚢 リリース** | [配布ガイド](docs/release/) | 配布・展開 |

---
