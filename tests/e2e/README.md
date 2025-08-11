# E2E（統合）テストスイート 🧪

> **システム全体の動作を検証するEnd-to-Endテスト**  
> 新メンバー向け：E2Eテストの実行方法と理解すべきポイント

## 🎯 E2Eテストとは？

**E2E（End-to-End）テスト**は、ユーザーの実際の使用フローを模倣し、システム全体が期待通りに動作することを検証するテストです。

### 📊 勤怠管理ツールでのE2Eフロー
```
📥 CSVファイル読み込み
    ↓
🔍 データ検証・クレンジング
    ↓
⚙️ 勤怠計算・集計処理
    ↓
📈 レポート生成・出力
    ↓
✅ 結果検証
```

## テストの種類

### 1. 正常フローテスト (`test_complete_normal_workflow`)

- CSVファイルの読み込み
- データ検証
- 集計処理
- レポート出力

のすべてのステップが正常に動作することを確認します。

### 2. 異常ケーステスト (`test_error_handling_workflow`)

以下のエラー状況での動作を確認します：

- 不正なCSVファイル
- データ形式エラー
- 欠損データの処理

### 3. パフォーマンステスト (`test_performance_regression`)

- 大容量データ処理の性能確認
- メモリ使用量の監視
- 処理時間の測定

### 4. セキュリティテスト (`test_security_compliance`)

- 個人情報のログ出力防止
- 一時ファイルの適切な削除
- データ保護の確認

### 5. CLI統合テスト (`test_cli_integration`)

コマンドライン経由での実行が正常に動作することを確認します。

### 6. データ整合性テスト (`test_data_consistency_through_pipeline`)

処理の各段階でデータが正しく保持されることを確認します。

### 7. 並行性・安定性テスト

- 複数処理の並行実行
- メモリリーク検出

## テスト実行

### 個別実行

```bash
# 特定のテストを実行
python -m pytest tests/e2e/test_end_to_end.py::TestE2EIntegration::test_complete_normal_workflow -v

# パフォーマンステストのみ
python -m pytest tests/e2e/test_end_to_end.py::TestE2EIntegration::test_performance_regression -v
```

### 全E2Eテスト実行

```bash
python -m pytest tests/e2e/ -v
```

### Makefileを使用

```bash
# すべてのE2Eテスト
make e2e-test

# パフォーマンステストのみ
make performance-test

# セキュリティテストのみ
make security-test
```

## テストデータ

### 標準テストデータ

`TestDataManager.generate_standard_csv_data()` により生成される標準的な勤怠データ：

- 従業員数：3名（デフォルト）
- 勤務日数：3日（デフォルト）
- 基本的な勤務パターン（9:00-18:00、休憩1時間）
- 遅刻・残業のランダムなバリエーション

### 大容量テストデータ

パフォーマンステスト用の大容量データ：

- 従業員数：100名（本格テスト時）
- 勤務日数：30日（1ヶ月分）
- 総レコード数：3,000レコード

### 破損テストデータ

エラーハンドリングテスト用の不正データ：

- 不正な日付（2024-02-30）
- 不正な時刻（25:00）
- 欠損データ
- データ不整合（退勤 < 出勤）

## ファイル構成

```
tests/e2e/
├── __init__.py                 # E2Eテストパッケージ
├── README.md                   # このファイル
├── conftest.py                 # テスト設定・フィクスチャ
├── test_end_to_end.py         # メインE2Eテスト
└── ../fixtures/e2e/           # テスト用固定データ
    └── standard_workflow_data.csv
```

## CI/CD統合

### GitHub Actions

`.github/workflows/e2e-tests.yml` でE2Eテストの自動実行が設定されています：

- Python 3.8-3.11での実行
- 単体テスト → 統合テスト → E2Eテストの順序実行
- パフォーマンス・セキュリティテストの個別実行
- カバレッジレポート生成

### 実行時間の目安

- 正常フロー：約1秒
- 異常ケース：約1秒
- パフォーマンステスト：約5秒（小規模データ）
- セキュリティテスト：約2秒
- 全E2Eテスト：約10秒

## トラブルシューティング

### よくある問題

1. **文字エンコーディングエラー**
   - 解決策：UTF-8 BOM付きCSVを使用
   - chardetパッケージのインストールを確認

2. **メモリ不足エラー**
   - 解決策：テストデータサイズを削減
   - パフォーマンステストの実行環境を確認

3. **一時ファイルの削除エラー**
   - 解決策：Windowsの場合、ファイルロックを確認
   - テスト後のクリーンアップ処理を確認

### ログ出力

詳細なテスト実行ログを表示する場合：

```bash
python -m pytest tests/e2e/ -v -s --log-cli-level=DEBUG
```

## 貢献

新しいE2Eテストを追加する場合：

1. `test_end_to_end.py`に新しいテストメソッドを追加
2. 必要に応じて`conftest.py`にフィクスチャを追加
3. テストデータが必要な場合は`TestDataManager`を拡張
4. このREADMEを更新