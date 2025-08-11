# 新メンバー オンボーディングガイド 🚀

> **勤怠管理ツールプロジェクトへようこそ！** このガイドで、初日からプロダクティブに貢献できるようサポートします。

## 🎯 オンボーディング目標

**1週間後の到達目標**:
- ✅ プロジェクト全体像の理解
- ✅ 開発環境の完全セットアップ 
- ✅ 最初のプルリクエスト投稿
- ✅ チーム開発フローへの適応

---

## 📅 Day-by-Day オンボーディングプラン

### 🌅 **Day 1: ウェルカム & 基礎理解**

#### ⏰ 午前（2-3時間）

**1. 🎬 プロジェクト概要（30分）**
```markdown
☑️ メインREADME.mdを読む
☑️ プロジェクトの目的・価値を理解する  
☑️ 主要機能をざっと把握する
☑️ 技術スタック（Python, pytest, CLI/GUI）を確認
```

**2. 🚀 クイックスタート体験（30分）**
```bash
# 実行ファイルで即座に体験
git clone https://github.com/kumab2221/attendance-tool.git
cd attendance-tool
dist/attendance-tool-cli.exe --version
dist/attendance-tool-gui.exe

# 5分間チュートリアルを実行
# （README.mdの手順に従って）
```

**3. 🏗️ アーキテクチャ理解（60分）**
```markdown
☑️ docs/design/attendance-tool/architecture.md を読む
☑️ システム構成図を理解する
☑️ データフローを把握する
☑️ モジュール間の関係を理解する
```

**4. 📋 要件・仕様確認（60分）**
```markdown
☑️ docs/spec/attendance-tool-requirements.md を読む
☑️ 機能要件（REQ-001〜REQ-402）を概要把握
☑️ 非機能要件（NFR-001〜NFR-203）を確認
☑️ 質問リストを作成する
```

#### ⏰ 午後（2-3時間）

**5. 🛠️ 開発環境セットアップ（90分）**
```bash
# 完全な開発環境構築
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -e .
pip install -r requirements-dev.txt
pre-commit install

# 動作確認
pytest tests/ -v
attendance-tool --version
```

**6. 🧪 テスト理解（60分）**
```markdown
☑️ docs/testing/README.md を読む
☑️ テスト戦略を理解する
☑️ カバレッジレポートを確認する
☑️ テスト実行方法を習得する
```

**7. 👥 チーム紹介・質問タイム（30分）**
```markdown
☑️ チームメンバーの紹介
☑️ コミュニケーション方法の確認
☑️ 疑問点・質問の整理
☑️ 次の日の計画確認
```

---

### 🌱 **Day 2: 開発環境習熟**

#### ⏰ 午前（3時間）

**1. 🔍 コードベース探索（90分）**
```bash
# 主要モジュールの理解
ls -la src/attendance_tool/
cat src/attendance_tool/__init__.py

# 重要なファイルを読む（流し読み）
src/attendance_tool/cli/main.py       # CLIエントリーポイント
src/attendance_tool/data/csv_reader.py # データ読み込み
src/attendance_tool/calculation/calculator.py # 計算エンジン
```

**2. 🧪 テストコード理解（90分）**
```bash
# テスト構造の理解
ls -la tests/
pytest tests/unit/test_csv_reader.py -v
pytest tests/integration/test_cli_integration.py -v

# カバレッジ測定
pytest tests/ --cov=attendance_tool --cov-report=html
open htmlcov/index.html
```

#### ⏰ 午後（3時間）

**3. 🔧 開発ツール習熟（60分）**
```bash
# コード品質ツールの使用
black src tests
isort src tests  
mypy src
flake8 src tests

# pre-commitの動作確認
git add .
git commit -m "test: initial setup"
```

**4. 🐛 デバッグ・トラブルシューティング（60分）**
```bash
# 意図的にテストを失敗させてデバッグ
pytest tests/unit/test_csv_reader.py::test_specific_case -v -s --pdb

# ログレベルを上げて詳細出力
pytest tests/ -v -s --log-cli-level=DEBUG
```

**5. 📚 ドキュメント深掘り（60分）**
```markdown
☑️ docs/tasks/attendance-tool-tasks.md - 全体タスク理解
☑️ docs/testing/TEST_MAPPING.md - テスト網羅状況
☑️ 疑問点の整理・質問準備
```

---

### 🌿 **Day 3: 実践・小さなタスク**

#### ⏰ 午前（3時間）

**1. 📝 小さなドキュメント改善（90分）**
```bash
# 例: タイポ修正、コメント追加、README改善等
git checkout -b fix/improve-documentation
# ドキュメント修正
git commit -m "docs: fix typo in installation guide"
git push origin fix/improve-documentation
# プルリクエスト作成
```

**2. 🧪 テストケース追加（90分）**
```bash
# 例: エッジケーステストの追加
git checkout -b test/add-edge-case-tests
# tests/unit/test_csv_reader.py に小さなテスト追加
pytest tests/unit/test_csv_reader.py -v
git commit -m "test: add edge case for empty CSV file"
```

#### ⏰ 午後（3時間）

**3. 🔍 コードレビュー参加（60分）**
```markdown
☑️ 既存のプルリクエストをレビュー
☑️ コメント・質問を投稿
☑️ レビュープロセスを学習
```

**4. 🐛 簡単なバグ修正（120分）**
```bash
# Good First Issue からタスク選択
git checkout -b fix/handle-empty-input
# 小さなバグ修正実装
pytest tests/ -v  # テスト通過確認
git commit -m "fix: handle empty input gracefully"
git push origin fix/handle-empty-input
```

---

### 🌳 **Day 4-5: 機能実装体験**

#### 🎯 中規模タスク挑戦（2日間）

**候補タスク例**:
- 新しいCSVフォーマットサポート
- エラーメッセージの改善
- パフォーマンス最適化
- GUI機能の小さな改善

**実装フロー**:
```bash
# 1. 要件理解・設計検討（半日）
# 2. TDDでのテスト作成（半日）
# 3. 実装（1日）
# 4. レビュー対応・マージ（半日）
```

---

### 🚀 **Week 1 End: 振り返り・次週計画**

#### 📊 成果確認チェックリスト

**技術習得**:
- [ ] 開発環境を問題なくセットアップできる
- [ ] テストを書いて実行できる
- [ ] コード品質ツールを使える
- [ ] プルリクエストを作成できる

**プロジェクト理解**:
- [ ] システム全体のアーキテクチャを説明できる
- [ ] 主要機能（CSV読み込み→計算→出力）を理解している
- [ ] テスト戦略とカバレッジ状況を把握している
- [ ] 開発フローに参加できる

**チーム適応**:
- [ ] コミュニケーション方法を理解している
- [ ] コードレビューに参加できる
- [ ] 質問・相談を適切に行える
- [ ] 次の挑戦目標が明確

---

## 📚 推奨リソース・学習教材

### 📖 **プロジェクト関連ドキュメント**

#### 必読（Priority 1）
1. [📋 メインREADME](../README.md) - プロジェクト全体像
2. [🎯 要件仕様書](spec/attendance-tool-requirements.md) - 機能要件
3. [🏗️ アーキテクチャ](design/attendance-tool/architecture.md) - システム設計
4. [🧪 テストガイド](testing/README.md) - 品質保証

#### 推奨（Priority 2）
5. [📋 タスク一覧](tasks/attendance-tool-tasks.md) - 実装状況
6. [🗺️ テスト対応表](testing/TEST_MAPPING.md) - テスト網羅性
7. [📊 品質レポート](testing/COVERAGE_REPORT.md) - 品質現状

#### 参考（Priority 3）
8. [🚢 リリースガイド](release/DISTRIBUTION_GUIDE.md) - 配布方法
9. [📝 GUI使用法](gui_usage.md) - GUI操作方法

### 🎓 **技術スタック学習**

#### Python開発
- [Python公式ドキュメント](https://docs.python.org/3/) - 言語仕様
- [pytest公式ガイド](https://docs.pytest.org/) - テストフレームワーク  
- [Black](https://black.readthedocs.io/) - コードフォーマッター
- [mypy](https://mypy.readthedocs.io/) - 型チェック

#### 業務ドメイン
- 勤怠管理システムの基礎知識
- 労働基準法・就業規則の基本
- CSVデータ処理のベストプラクティス

### 🛠️ **開発ツール**

#### 必須ツール
- **IDE**: Visual Studio Code（推奨設定あり）
- **Git**: バージョン管理
- **pytest**: テスト実行
- **pre-commit**: コード品質自動チェック

#### 推奨ツール
- **GitHub CLI**: プルリクエスト管理
- **Windows Terminal**: 高機能ターミナル
- **Docker**: 環境統一（オプション）

---

## 🤝 チーム・コミュニケーション

### 📞 **コミュニケーションチャンネル**

| チャンネル | 用途 | レスポンス目安 |
|------------|------|----------------|
| **Slack #dev-team** | 日常的な質問・議論 | 数時間 |
| **GitHub Issues** | バグ報告・機能提案 | 1-3日 |
| **GitHub Discussions** | 設計議論・アイデア | 1-7日 |
| **Daily Standup** | 進捗共有・ブロッカー | 毎日 |
| **PR Review** | コードレビュー | 1-2日 |

### 🎯 **効果的な質問方法**

#### 良い質問の例
```markdown
## 質問: CSV読み込みでエンコーディングエラー

### 状況
- ファイル: `sample_data.csv`  
- エラー: `UnicodeDecodeError: 'utf-8' codec can't decode`
- 環境: Windows 10, Python 3.9

### 試したこと
1. ファイルエンコーディングをUTF-8に変換 → 同じエラー
2. `encoding='shift_jis'` を指定 → 別のエラー

### 質問
Shift_JISエンコードのCSVファイルを適切に処理する方法は？
設定で自動検出できる仕組みはありますか？

### コード（問題箇所）
```python
df = pd.read_csv(file_path, encoding='utf-8')  # ここでエラー
```
```

#### 避けるべき質問例
- ❌ "動きません"
- ❌ "エラーが出ます"
- ❌ "どうすればいいですか"

### 👥 **メンター・バディ制度**

**🤝 バディシステム**:
- 新メンバーには経験豊富なチームメンバーがバディとして付きます
- 日常的な質問・相談の第一窓口
- 技術的なサポート・コードレビュー
- キャリア相談・チーム文化の共有

**🧑‍🏫 技術メンター**:
- 複雑な技術問題への専門的サポート
- アーキテクチャ・設計レビュー
- スキル向上のための学習プラン

---

## 🎯 役割別オンボーディング

### 👨‍💻 **ソフトウェアエンジニア**

**Week 1 Focus**:
- [ ] Python開発環境マスター
- [ ] テスト駆動開発（TDD）実践
- [ ] 小〜中規模機能実装
- [ ] コードレビュープロセス参加

**Extended Learning Path (Month 1)**:
- Week 2: パフォーマンス最適化に挑戦
- Week 3: 新機能の要件定義から実装まで
- Week 4: 技術負債解消・リファクタリング

### 🔍 **QAエンジニア**

**Week 1 Focus**:
- [ ] テスト戦略の理解
- [ ] 自動テスト環境習熟
- [ ] バグ発見・報告プロセス
- [ ] 品質メトリクス分析

**Extended Learning Path**:
- Week 2: E2Eテスト強化
- Week 3: パフォーマンステスト設計
- Week 4: 品質向上提案・実装

### 👨‍💼 **プロダクト/プロジェクトマネージャー**

**Week 1 Focus**:
- [ ] プロジェクト全体像・進捗把握
- [ ] ステークホルダー関係理解
- [ ] 品質・リスク状況の把握
- [ ] チーム開発プロセス理解

**Extended Learning Path**:
- Week 2: 要件管理・優先順位付け
- Week 3: リリース計画・品質管理
- Week 4: チーム効率化・プロセス改善

### 📝 **テクニカルライター**

**Week 1 Focus**:
- [ ] 既存ドキュメント構造の理解
- [ ] ユーザー視点でのドキュメント評価
- [ ] 改善点の特定・提案
- [ ] 小さな修正・追加の実践

---

## 📈 成長・評価指標

### 🎯 **Week 1 成功指標**

**技術的成長**:
- [ ] 独立して開発環境をセットアップできる
- [ ] 基本的なテストを書いて実行できる
- [ ] 簡単なバグ修正を完了できる
- [ ] プルリクエストを作成・マージできる

**プロジェクト理解**:
- [ ] システム概要を他人に説明できる
- [ ] 主要な技術的判断の背景を理解している
- [ ] 品質・テスト方針を把握している
- [ ] チーム開発フローを理解している

**チーム統合**:
- [ ] 適切なコミュニケーション方法を身につけている
- [ ] コードレビューに建設的に参加できる
- [ ] 質問・相談を効果的に行える
- [ ] チーム文化・価値観を理解している

### 🚀 **Month 1 発展目標**

**技術リーダーシップ**:
- [ ] 中〜大規模機能を設計・実装できる
- [ ] 他のメンバーのコードレビューができる
- [ ] 技術的な提案・改善を行える
- [ ] 新メンバーのサポートができる

**プロダクト貢献**:
- [ ] ユーザー価値を意識した開発ができる
- [ ] 品質向上・効率化に貢献している
- [ ] プロジェクト全体の改善提案を行える
- [ ] ドメイン知識を深めて専門性を発揮している

---

## 🎉 オンボーディング完了

### ✅ 卒業要件

以下すべてを達成したらオンボーディング完了です！

**Technical Mastery**:
- [x] 完全な開発環境セットアップ
- [x] TDDによるテスト作成・実行
- [x] コード品質ツールの活用
- [x] CI/CDパイプラインの理解

**Project Understanding**:
- [x] システム全体アーキテクチャの理解
- [x] 要件・仕様の把握
- [x] 品質・テスト戦略の理解
- [x] 開発プロセスへの適応

**Team Integration**:
- [x] 効果的なコミュニケーション
- [x] コードレビュー参加
- [x] 問題解決・サポート活用
- [x] プロジェクト貢献の実績

### 🎯 Next Steps

オンボーディング完了後は：

1. **🎖️ 専門領域の選択**: フロントエンド/バックエンド/QA/PM等
2. **📈 スキル向上計画**: 個人の成長目標設定
3. **🤝 メンタリング参加**: 新メンバーのサポート
4. **🚀 リーダーシップ発揮**: プロジェクトの改善・発展への貢献

**おめでとうございます！🎉**
これで立派なチームメンバーです。
引き続き学習・成長・貢献を楽しんでください！

---

<div align="center">

**Welcome to the team! 🚀**

*Built with ❤️ by the development team*

</div>