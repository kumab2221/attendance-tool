# アセット管理 (Assets Directory) 🎨

> **新メンバー向け**: アプリケーションで使用するアイコン・画像ファイルの管理ガイド

## 📁 概要

このディレクトリには、勤怠管理ツールの実行ファイル生成時に使用するアセットファイル（主にアイコン）を配置します。

### 🎯 新メンバーが知っておくべきポイント

1. **📝 現状**: 現在このディレクトリは空です（意図的）
2. **⚙️ 動作**: アイコンなしでも正常にビルドできます
3. **🔧 カスタマイズ**: 独自アイコンが必要な場合のみ追加

---

## 📋 必要なファイル（オプション）

### 🖼️ アイコンファイル

| ファイル名 | 用途 | 形式 | サイズ推奨 |
|------------|------|------|------------|
| **`icon.ico`** | Windows実行ファイル用 | ICO | 32×32, 48×48, 256×256 |
| **`icon.png`** | ドキュメント・Web用 | PNG | 256×256 |

### 🖼️ その他のアセット（将来の拡張用）
- スプラッシュ画面用画像
- GUI内で使用するアイコン類
- ブランディング用画像

---

## 🛠️ アイコン作成方法

### ステップ1️⃣: PNG作成
```markdown
✅ 推奨仕様:
- サイズ: 256×256ピクセル（正方形）
- フォーマット: PNG（透明背景推奨）
- デザイン: シンプルで視認性の高いデザイン
```

### ステップ2️⃣: ICO変換

**方法A: ImageMagick（推奨）**
```bash
# ImageMagickインストール後
magick convert icon.png -define icon:auto-resize icon.ico
```

**方法B: オンラインツール**
- [ConvertICO](https://convertio.co/png-ico/) - ブラウザで簡単変換
- [ICO Convert](https://icoconvert.com/) - 多サイズ一括生成

### ステップ3️⃣: ファイル配置
```bash
# assetsディレクトリに配置
cp your-icon.ico assets/icon.ico
cp your-icon.png assets/icon.png
```

---

## 📦 ビルド時の動作

### ✅ **アイコンファイルがある場合**
```bash
# build_scripts/build_exe.py が自動的にアイコンを適用
pyinstaller --icon=assets/icon.ico ...
```

### ⚙️ **アイコンファイルがない場合（現状）**
```bash
# デフォルトのWindowsアイコンを使用
# エラーにならず正常にビルドされます
pyinstaller ... # --iconオプションなし
```

### 🔍 動作確認方法
```bash
# ビルド実行
python build_scripts/build_exe.py

# 生成された実行ファイルのアイコン確認
ls -la dist/
# → attendance-tool-cli.exe
# → attendance-tool-gui.exe
```

---

## 🎨 アイコンデザインガイドライン

### 💡 **推奨デザイン要素**
- 📅 カレンダー・時計モチーフ
- ⏰ 時間管理を象徴するデザイン
- 📊 データ・レポートを表現
- 🏢 ビジネス・企業向けの印象

### 🎨 **カラーパレット推奨**
```css
/* ビジネス系カラー */
主色: #2E86C1 (ブルー)
副色: #28B463 (グリーン)
強調: #F39C12 (オレンジ)
ベース: #34495E (ダークグレー)
```

### ❌ **避けるべきデザイン**
- 複雑すぎるデザイン（小さいサイズで不明瞭）
- 著作権のある画像の使用
- ブランドカラーと相反する色使い

---

## 🚀 新メンバー向けクイックスタート

### 📖 **アイコンが必要ない場合（推奨）**
```bash
# 何もしない - デフォルトで動作します
# ビルド時にアイコンは自動的にスキップされます
```

### 🎨 **カスタムアイコンを追加する場合**

**1分間セットアップ**:
```bash
# 1. PNGアイコンを準備（256×256推奨）
# 2. オンラインでICOに変換
# 3. ファイル配置
cp your-icon.ico assets/icon.ico
cp your-icon.png assets/icon.png

# 4. ビルドしてテスト
python build_scripts/build_exe.py
```

---

## 📞 サポート・ヘルプ

### 🆘 **よくある質問**

<details>
<summary><strong>Q: アイコンファイルがなくてもビルドできますか？</strong></summary>

**A: はい、問題ありません。**
- デフォルトのWindowsアイコンが使用されます
- ビルドプロセスにエラーは発生しません
- 機能面での影響はありません
</details>

<details>
<summary><strong>Q: アイコンが反映されません</strong></summary>

**A: 以下を確認してください:**
```bash
# ファイル名・場所確認
ls -la assets/
# → icon.ico があるか確認

# ファイルフォーマット確認
file assets/icon.ico
# → "MS Windows icon resource" と表示されるか

# ビルドスクリプトの再実行
python build_scripts/build_exe.py
```
</details>

<details>
<summary><strong>Q: どんなデザインがおすすめですか？</strong></summary>

**A: ビジネス向けシンプルデザインがおすすめ:**
- 📅 カレンダーアイコン
- ⏰ 時計アイコン  
- 📊 チャート・グラフアイコン
- 💼 ビジネスバッグアイコン

**参考サイト**:
- [Feather Icons](https://feathericons.com/) - シンプルアイコン
- [Heroicons](https://heroicons.com/) - モダンアイコン
</details>

### 📧 **サポート連絡先**
- 🐛 **バグ・問題**: GitHub Issues
- 💬 **質問・相談**: GitHub Discussions  
- 📝 **改善提案**: Pull Request

---

<div align="center">

**アセット管理ガイド** 🎨 **Built for Developers**

*Last Updated: 2025-08-11*

</div>