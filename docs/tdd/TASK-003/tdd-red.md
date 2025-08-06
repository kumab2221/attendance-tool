# TASK-003: CLIインターフェース基盤 - Red Phase実装

## Red Phase実行結果

### テスト実装完了

1. **単体テスト**: `tests/unit/test_cli.py`
   - TestMainCommand: メインコマンドのテスト（3テストケース）
   - TestProcessCommand: processコマンドのテスト（3テストケース）
   - TestArgumentParsing: 引数パーステスト（6テストケース）
   - TestFileValidation: ファイルバリデーションテスト（3テストケース）
   - TestDateValidation: 日付バリデーションテスト（2テストケース）
   - TestOptionCombinations: オプション組み合わせテスト（3テストケース）
   - TestErrorHandling: エラーハンドリングテスト（3テストケース）

2. **統合テスト**: `tests/integration/test_cli_integration.py`
   - TestCliIntegration: CLI統合テスト（5テストケース）
   - TestFileOperations: ファイル操作統合テスト（3テストケース）
   - TestConfigIntegration: 設定統合テスト（3テストケース）
   - TestPerformanceIntegration: パフォーマンス統合テスト（2テストケース）
   - TestErrorScenarios: エラーシナリオ統合テスト（2テストケース）

### 失敗確認

```python
# インポートテストで期待通り失敗を確認
try:
    from attendance_tool.cli import main
    # ❌ 成功してはいけない
except ImportError as e:
    # ✅ 期待通りの失敗: No module named 'attendance_tool.cli.main'
```

### テスト設計ポイント

1. **失敗するテスト作成**
   - まだ実装されていないCLIモジュールをインポートして失敗
   - 存在しないコマンドやオプションを実行して失敗
   - 適切なエラーメッセージが返されることを期待

2. **包括的なテストケース**
   - 正常系: 基本的なコマンド実行
   - 異常系: 不正な引数、ファイルエラー、権限エラー
   - 境界値: 日付の境界、ファイルサイズの境界
   - 組み合わせ: 複数オプションの組み合わせ

3. **テストフィクスチャ活用**
   - tempfile/tempdir: 一時ファイル・ディレクトリ作成
   - click.testing.CliRunner: CLI実行テスト
   - CSV データ生成: 様々なパターンのテストデータ

4. **エラーハンドリング重視**
   - 適切なエラーメッセージ
   - 正しい終了コード
   - ユーザーフレンドリーなメッセージ

## 次のステップ（Green Phase）

Red Phaseが完了し、テストが期待通り失敗することを確認できました。
次はGreen Phaseとして、テストが通る最小限のCLI実装を行います。

### 実装予定の最小機能

1. **メインコマンド構造**
   - `attendance_tool.cli.main:main` 関数
   - Click decoratorによるコマンド定義
   - ヘルプメッセージとバージョン表示

2. **processコマンド骨格**
   - 基本的な引数定義（--input, --output）
   - 引数の存在チェック
   - 基本的なバリデーション

3. **エラーハンドリング基盤**
   - 適切なエラーメッセージ表示
   - 終了コード制御

実装は最小限にとどめ、まずテストを通すことに集中します。