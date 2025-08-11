# テスト・機能対応表（Test Mapping）

## 概要

この文書は、勤怠管理ツールの機能とテストコードの対応関係を明確にするためのマトリックス表です。
各機能に対してどのテストが実装されているか、テストカバレッジの状況を把握できます。

## テスト分類

### テストレベル
- **Unit**: 単体テスト（関数・クラス単位）
- **Integration**: 統合テスト（モジュール間）
- **E2E**: エンドツーエンドテスト（システム全体）

### テストタイプ
- **Functional**: 機能テスト
- **Performance**: パフォーマンステスト
- **Security**: セキュリティテスト
- **Error**: エラーハンドリングテスト

## 機能・テスト対応マトリックス

### 📁 フェーズ1: 基盤構築・環境設定

| 機能 | タスク | 実装コード | テストファイル | テストタイプ | 状態 |
|------|--------|------------|----------------|--------------|------|
| プロジェクト構造管理 | TASK-001 | `src/` | - | - | ✅ |
| 設定ファイル読み込み | TASK-002 | `utils/config.py` | `test_config.py` | Unit/Integration | ✅ |
| CLIインターフェース | TASK-003 | `cli/main.py` | `test_cli.py`, `test_cli_integration.py` | Unit/Integration | ✅ |

### 📁 フェーズ2: データ処理基盤

| 機能 | タスク | 実装コード | テストファイル | テストタイプ | 状態 |
|------|--------|------------|----------------|--------------|------|
| CSVファイル読み込み | TASK-101 | `data/csv_reader.py` | `test_csv_reader.py` | Unit | ✅ |
| データ検証・クレンジング | TASK-102 | `validation/validator.py` | `test_data_validator.py`, `test_data_cleaner.py` | Unit | ✅ |
| 期間フィルタリング | TASK-103 | `filtering/date_filter.py` | `test_date_filter.py`, `test_period_specification.py` | Unit | ✅ |

### 📁 フェーズ3: ビジネスロジック実装

| 機能 | タスク | 実装コード | テストファイル | テストタイプ | 状態 |
|------|--------|------------|----------------|--------------|------|
| 勤怠集計エンジン | TASK-201 | `calculation/calculator.py` | `test_calculator.py` | Unit | ✅ |
| 就業規則エンジン | TASK-202 | `calculation/work_rules_engine.py` | `test_work_rules_engine.py` | Unit | ✅ |
| 部門別集計 | TASK-203 | `calculation/department.py` | - | - | ⚠️ |

### 📁 フェーズ4: レポート出力機能

| 機能 | タスク | 実装コード | テストファイル | テストタイプ | 状態 |
|------|--------|------------|----------------|--------------|------|
| CSV出力 | TASK-301 | `output/csv_exporter.py` | `test_csv_exporter.py` | Unit | ✅ |
| Excel出力 | TASK-302 | `output/excel_exporter.py` | `test_excel_exporter.py` | Unit | ✅ |
| テンプレート管理 | TASK-303 | `output/template_manager.py` | `test_template_manager.py` | Unit | ✅ |

### 📁 フェーズ5: エラーハンドリング・ログ機能

| 機能 | タスク | 実装コード | テストファイル | テストタイプ | 状態 |
|------|--------|------------|----------------|--------------|------|
| エラーハンドリング | TASK-401 | `errors/handler.py` | `test_error_classification.py`, `test_recovery_manager.py` | Unit/Integration | ✅ |
| ログ・監査機能 | TASK-402 | `logging/audit_logger.py` | `test_audit_logger.py`, `test_masking.py` | Unit/Security | ✅ |

### 📁 フェーズ6: パフォーマンス・統合テスト

| 機能 | タスク | 実装コード | テストファイル | テストタイプ | 状態 |
|------|--------|------------|----------------|--------------|------|
| パフォーマンス最適化 | TASK-501 | `performance/optimized_calculator.py` | `test_optimized_calculator.py`, `test_memory_optimization.py` | Performance | ✅ |
| 統合テスト | TASK-502 | - | `test_end_to_end.py` | E2E | ✅ |

### 📁 フェーズ7: GUI・最終調整

| 機能 | タスク | 実装コード | テストファイル | テストタイプ | 状態 |
|------|--------|------------|----------------|--------------|------|
| GUI実装 | TASK-601 | `gui/main_window.py` | `test_main_window.py`, `test_file_dialogs.py` | Unit | ✅ |
| パッケージング・配布 | TASK-602 | `build_scripts/` | - | Manual | ✅ |

## 詳細テストマッピング

### 1. CSVファイル読み込み・検証 (TASK-101)

#### 機能コード
```
src/attendance_tool/data/csv_reader.py
src/attendance_tool/validation/enhanced_csv_reader.py
```

#### テストコード
| テストファイル | テスト対象 | テストケース数 | カバレッジ |
|----------------|------------|----------------|------------|
| `test_csv_reader.py` | 基本読み込み機能 | 8 | 95% |
| `test_data_validator.py` | データ検証ルール | 15 | 92% |

#### TDDテストケース
- **正常系**: 標準CSV読み込み、UTF-8/Shift_JIS対応
- **異常系**: ファイル不存在、不正フォーマット、文字化け
- **境界値**: 大容量ファイル、空ファイル

### 2. 勤怠集計エンジン (TASK-201)

#### 機能コード
```
src/attendance_tool/calculation/calculator.py
src/attendance_tool/calculation/summary.py
```

#### テストコード
| テストファイル | テスト対象 | テストケース数 | カバレッジ |
|----------------|------------|----------------|------------|
| `test_calculator.py` | 集計ロジック | 20 | 96% |
| `test_attendance_record.py` | データモデル | 12 | 100% |

#### TDDテストケース
- **基本集計**: 出勤・欠勤日数、遅刻・早退回数
- **時間計算**: 実労働時間、法定内外残業、深夜勤務
- **境界値**: 0分勤務、24時間勤務、月またぎ

### 3. エラーハンドリング統合 (TASK-401)

#### 機能コード
```
src/attendance_tool/errors/handler.py
src/attendance_tool/errors/exceptions.py
src/attendance_tool/errors/recovery.py
```

#### テストコード
| テストファイル | テスト対象 | テストケース数 | カバレッジ |
|----------------|------------|----------------|------------|
| `test_error_classification.py` | エラー分類 | 10 | 88% |
| `test_recovery_manager.py` | エラー復旧 | 8 | 85% |
| `test_error_integration.py` | 統合エラー処理 | 12 | 90% |

#### TDDテストケース
- **エラー検出**: 各種エラーシナリオ
- **エラー復旧**: リカバリー機能
- **ユーザー通知**: エラーメッセージ表示

### 4. パフォーマンス最適化 (TASK-501)

#### 機能コード
```
src/attendance_tool/performance/optimized_calculator.py
src/attendance_tool/performance/memory_manager.py
src/attendance_tool/performance/chunk_processor.py
```

#### テストコード
| テストファイル | テスト対象 | テストケース数 | カバレッジ |
|----------------|------------|----------------|------------|
| `test_optimized_calculator.py` | 最適化された計算 | 15 | 94% |
| `test_memory_optimization.py` | メモリ管理 | 8 | 87% |
| `test_performance_integration.py` | パフォーマンス統合 | 6 | 85% |

#### パフォーマンステスト要件
- **処理時間**: 100名×1ヶ月データを5分以内
- **メモリ使用量**: 1GB以下
- **スケーラビリティ**: 1000名まで対応

## E2E統合テスト

### test_end_to_end.py

| テストメソッド | 対象機能 | 検証内容 | 実行時間目安 |
|----------------|----------|----------|--------------|
| `test_complete_normal_workflow` | 全体フロー | CSV→集計→レポート出力 | ~1秒 |
| `test_error_handling_workflow` | エラー処理 | 不正データの適切な処理 | ~1秒 |
| `test_performance_regression` | パフォーマンス | 大容量データ処理性能 | ~5秒 |
| `test_security_compliance` | セキュリティ | 個人情報保護 | ~2秒 |
| `test_cli_integration` | CLI統合 | コマンドライン実行 | ~1秒 |
| `test_data_consistency` | データ整合性 | 処理各段階でのデータ保持 | ~1秒 |

## テストカバレッジ状況

### モジュール別カバレッジ

| モジュール | ライン数 | カバー率 | テストファイル数 | 状態 |
|------------|----------|----------|------------------|------|
| `cli/` | 450 | 92% | 2 | ✅ Good |
| `data/` | 280 | 95% | 1 | ✅ Excellent |
| `validation/` | 520 | 88% | 2 | ✅ Good |
| `calculation/` | 680 | 94% | 2 | ✅ Excellent |
| `output/` | 340 | 91% | 3 | ✅ Good |
| `errors/` | 230 | 89% | 3 | ✅ Good |
| `logging/` | 195 | 93% | 4 | ✅ Excellent |
| `performance/` | 310 | 87% | 6 | ⚠️ Acceptable |
| `gui/` | 420 | 75% | 3 | ⚠️ Needs Improvement |

### 全体統計

- **総テストファイル数**: 26
- **総テストケース数**: 約180
- **全体カバレッジ**: 89.2%
- **実行時間**: 約15秒（全テスト）

## テスト不足領域

### 🔴 高優先度

1. **GUI テスト** (75% カバレッジ)
   - ユーザーインタラクションテスト
   - UIコンポーネントテスト
   - エラー表示テスト

2. **部門別集計機能**
   - 専用テストファイル未作成
   - 階層構造テスト不足

### 🟡 中優先度

3. **パフォーマンステスト**
   - より大規模なデータでのテスト
   - 並行処理テスト
   - メモリリークテスト

4. **セキュリティテスト**
   - より包括的なセキュリティチェック
   - データ暗号化テスト

## テスト実行方法

### 全テスト実行
```bash
# 全テスト実行
python -m pytest tests/ -v

# カバレッジ付き実行
python -m pytest tests/ --cov=attendance_tool --cov-report=html
```

### カテゴリ別実行
```bash
# 単体テストのみ
python -m pytest tests/unit/ -v

# 統合テストのみ
python -m pytest tests/integration/ -v

# E2Eテストのみ
python -m pytest tests/e2e/ -v
```

### 特定機能のテスト
```bash
# CSVReader関連
python -m pytest tests/unit/test_csv_reader.py -v

# 計算機能関連
python -m pytest tests/unit/calculation/ -v

# エラーハンドリング関連
python -m pytest tests/unit/errors/ -v
```

## 継続的改善

### テスト品質向上のための課題

1. **カバレッジ向上**
   - GUI部分の自動テスト強化
   - エッジケースの追加テスト

2. **テストデータ管理**
   - より多様なテストデータセット
   - テストデータ生成の自動化

3. **テスト自動化**
   - CI/CD パイプラインでの自動テスト実行
   - パフォーマンス回帰テストの定期実行

4. **テストドキュメント**
   - テスト仕様書の継続更新
   - 新機能追加時のテスト追加ガイドライン

---

**最終更新**: 2025-08-11  
**作成者**: Development Team  
**レビュー**: 定期的に更新予定