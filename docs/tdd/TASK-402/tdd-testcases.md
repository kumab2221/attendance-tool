# TASK-402: ログ機能・監査対応 - テストケース設計

## 概要

構造化ログ出力、個人情報マスキング、パフォーマンス計測、監査ログ生成機能のテストケースを設計する。既存のエラーログ機能との統合も考慮して包括的なテスト戦略を構築する。

## テスト戦略

### テストレベル
- **単体テスト**: 個別機能の動作確認
- **統合テスト**: 既存システムとの連携確認  
- **パフォーマンステスト**: ログ出力のオーバーヘッド測定
- **セキュリティテスト**: 個人情報マスキングの確実性確認

### テストカテゴリ
- **構造化ログテスト**: JSON形式ログの正確性
- **マスキングテスト**: 個人情報の完全マスキング
- **パフォーマンステスト**: 計測精度とオーバーヘッド
- **監査ログテスト**: コンプライアンス要件充足
- **ローテーションテスト**: ログ管理機能

## テストケース詳細

### 1. 構造化ログ出力テスト

#### TC-402-001: JSON形式ログ出力
**目的**: ログエントリがJSON形式で正しく出力されることを確認

**テストデータ**:
```python
test_cases = [
    {
        "level": "INFO",
        "module": "csv_reader",
        "operation": "file_read",
        "message": "CSVファイル読み込み開始",
        "details": {
            "file_path": "/data/input.csv",
            "record_count": 1000
        },
        "expected_fields": [
            "timestamp", "level", "module", "operation", 
            "message", "details", "correlation_id", "session_id"
        ]
    },
    {
        "level": "ERROR",
        "module": "validator",
        "operation": "data_validation",
        "message": "データ検証エラー",
        "details": {
            "error_count": 5,
            "validation_rules": ["date_format", "time_logic"]
        },
        "expected_fields": [
            "timestamp", "level", "module", "operation",
            "message", "details", "correlation_id", "session_id"
        ]
    }
]
```

**期待結果**:
- JSON形式で出力される
- 必須フィールドがすべて含まれる
- タイムスタンプがISO8601形式
- correlation_idとsession_idが正しく生成される

#### TC-402-002: ログレベル別出力制御
**目的**: ログレベルに応じて適切な出力先に記録されることを確認

**テストシナリオ**:
```python
test_cases = [
    {
        "level": "DEBUG",
        "expected_outputs": ["file"],  # デバッグモードのみ
        "config": {"debug_mode": True}
    },
    {
        "level": "INFO", 
        "expected_outputs": ["file"],
        "config": {"debug_mode": False}
    },
    {
        "level": "WARNING",
        "expected_outputs": ["file", "console"],
        "config": {"debug_mode": False}
    },
    {
        "level": "ERROR",
        "expected_outputs": ["file", "console"],
        "config": {"debug_mode": False}
    },
    {
        "level": "CRITICAL",
        "expected_outputs": ["file", "console", "email"],
        "config": {"debug_mode": False}
    }
]
```

#### TC-402-003: 相関ID・セッションID管理
**目的**: 処理チェーン全体で一意なIDが適切に管理されることを確認

**テストシナリオ**:
1. 新しい処理セッション開始
2. 複数のログエントリを出力
3. セッションIDが全エントリで同一であることを確認
4. 相関IDが処理ごとに一意であることを確認

### 2. 個人情報マスキングテスト

#### TC-402-010: 基本マスキング機能
**目的**: 各種個人情報が適切にマスキングされることを確認

**テストデータ**:
```python
test_cases = [
    {
        "category": "氏名",
        "input": "処理対象: 田中太郎さんのデータ",
        "expected": "処理対象: ****さんのデータ",
        "masking_level": "STRICT"
    },
    {
        "category": "氏名",
        "input": "処理対象: 田中太郎さんのデータ",
        "expected": "処理対象: 田中***さんのデータ", 
        "masking_level": "MEDIUM"
    },
    {
        "category": "メールアドレス",
        "input": "連絡先: tanaka@company.com",
        "expected": "連絡先: ***@company.com",
        "masking_level": "MEDIUM"
    },
    {
        "category": "電話番号",
        "input": "電話: 090-1234-5678",
        "expected": "電話: 090-****-5678",
        "masking_level": "MEDIUM"
    },
    {
        "category": "社員ID", 
        "input": "社員ID: EMP001234",
        "expected": "社員ID: EM*****34",
        "masking_level": "MEDIUM"
    }
]
```

#### TC-402-011: マスキングレベル別処理
**目的**: 設定されたマスキングレベルに応じた処理が行われることを確認

**テストケース**:
```python
test_input = "田中太郎 (tanaka@company.com, 090-1234-5678)"

test_cases = [
    {
        "level": "STRICT",
        "expected": "**** (*@company.com, ***-****-****)"
    },
    {
        "level": "MEDIUM", 
        "expected": "田中*** (***@company.com, 090-****-5678)"
    },
    {
        "level": "LOOSE",
        "expected": "田中太郎 (tanaka@company.com, 090-1234-5678)"
    }
]
```

#### TC-402-012: 複合パターンマスキング
**目的**: 複数の個人情報が混在する場合の適切な処理を確認

**テストデータ**:
```python
complex_inputs = [
    {
        "input": "社員 田中太郎 (EMP001234) からメール tanaka@company.com で連絡あり。電話番号: 090-1234-5678",
        "expected": "社員 **** (EM*****34) からメール ***@company.com で連絡あり。電話番号: 090-****-5678"
    },
    {
        "input": "処理結果: 佐藤花子さん、鈴木一郎さん、田中太郎さんのデータを処理完了",
        "expected": "処理結果: ****さん、****さん、****さんのデータを処理完了"
    }
]
```

### 3. パフォーマンス計測テスト

#### TC-402-020: 処理時間計測
**目的**: 各処理の実行時間が正確に計測されることを確認

**テストシナリオ**:
```python
def test_processing_time_measurement():
    # 既知の処理時間を持つダミー処理を実行
    def dummy_process():
        time.sleep(1.0)  # 1秒間の処理
    
    # パフォーマンストラッカーで計測
    with PerformanceTracker() as tracker:
        dummy_process()
    
    # 計測精度確認（±50ms以内）
    assert 950 <= tracker.duration_ms <= 1050
```

#### TC-402-021: メモリ使用量計測
**目的**: メモリ使用量が正確に計測されることを確認

**テストシナリオ**:
```python
def test_memory_usage_measurement():
    # 既知のメモリ使用量を持つ処理
    def memory_intensive_process():
        # 10MB相当のデータを作成
        large_data = [0] * (10 * 1024 * 1024 // 8)
        return large_data
    
    with PerformanceTracker() as tracker:
        data = memory_intensive_process()
    
    # メモリ使用量の増加を確認
    assert tracker.memory_peak_mb >= 10.0
```

#### TC-402-022: パフォーマンス閾値アラート
**目的**: 設定された閾値を超えた場合にアラートが発生することを確認

**テストケース**:
```python
test_cases = [
    {
        "metric": "processing_time",
        "threshold": 30000,  # 30秒
        "test_value": 35000,  # 35秒
        "expected_alert": "WARNING"
    },
    {
        "metric": "memory_usage",
        "threshold": 512,     # 512MB
        "test_value": 800,    # 800MB
        "expected_alert": "WARNING"
    },
    {
        "metric": "error_rate",
        "threshold": 0.05,    # 5%
        "test_value": 0.08,   # 8%
        "expected_alert": "WARNING"
    }
]
```

### 4. 監査ログテスト

#### TC-402-030: 監査イベント記録
**目的**: 主要なイベントが監査ログに適切に記録されることを確認

**テストイベント**:
```python
audit_events = [
    {
        "event_type": "FILE_ACCESS",
        "action": "read",
        "resource": "/data/input.csv",
        "expected_fields": [
            "audit_id", "timestamp", "event_type", "actor",
            "resource", "action", "result", "risk_level"
        ]
    },
    {
        "event_type": "DATA_PROCESSING",
        "action": "process",
        "resource": "employee_data",
        "details": {
            "record_count": 1000,
            "processing_type": "attendance_calculation"
        }
    },
    {
        "event_type": "ERROR_OCCURRED",
        "action": "error_handling",
        "resource": "system",
        "details": {
            "error_type": "ValidationError",
            "error_code": "DATA-001"
        }
    }
]
```

#### TC-402-031: リスクレベル判定
**目的**: イベントのリスクレベルが適切に判定されることを確認

**テストケース**:
```python
risk_assessment_cases = [
    {
        "event": "FILE_ACCESS",
        "action": "read",
        "resource_type": "employee_data",
        "user_role": "admin",
        "expected_risk": "low"
    },
    {
        "event": "FILE_ACCESS", 
        "action": "write",
        "resource_type": "employee_data",
        "user_role": "viewer",
        "expected_risk": "high"
    },
    {
        "event": "ERROR_OCCURRED",
        "error_type": "SecurityError",
        "frequency": "repeated",
        "expected_risk": "high"
    }
]
```

#### TC-402-032: 監査ログ完全性
**目的**: 監査ログが改竄されていないことを検証

**テストシナリオ**:
1. 監査ログエントリを生成
2. ハッシュ値を計算・保存
3. ログファイルの内容確認
4. ハッシュ値による完全性検証

### 5. ログローテーション・管理テスト

#### TC-402-040: サイズベースローテーション
**目的**: ファイルサイズに基づくログローテーションが正常に動作することを確認

**テストシナリオ**:
```python
def test_size_based_rotation():
    config = {
        "max_size": "1MB",
        "max_files": 5
    }
    
    # 1MB超のログを出力
    logger = StructuredLogger(config)
    for i in range(2000):  # 十分なログ量
        logger.info(f"Test log entry {i:04d} with sufficient content to reach size limit")
    
    # ローテーション確認
    log_files = glob.glob("logs/app_*.log*")
    assert len(log_files) >= 2  # 元ファイル + ローテーション済み
    
    # ファイルサイズ確認
    current_log = "logs/app.log"
    assert os.path.getsize(current_log) < 1024 * 1024  # 1MB未満
```

#### TC-402-041: 日付ベースローテーション
**目的**: 日付に基づくログローテーションが正常に動作することを確認

**テストシナリオ**:
1. 日付ベースローテーション設定
2. 複数日にわたるログ出力（模擬）
3. 日付ごとのファイル分割確認

#### TC-402-042: ログファイル圧縮
**目的**: 古いログファイルが適切に圧縮されることを確認

**期待結果**:
- 指定期間経過後のファイルが圧縮される
- 圧縮率が適切（50%以上の削減）
- 圧縮ファイルが読み取り可能

### 6. 統合テスト

#### TC-402-050: エラーハンドリング統合
**目的**: 既存のエラーハンドリングシステムとの統合が正常に動作することを確認

**テストシナリオ**:
```python
def test_error_handling_integration():
    from attendance_tool.errors import ErrorHandler
    
    # エラー発生
    error_handler = ErrorHandler()
    try:
        raise FileNotFoundError("/missing/file.csv")
    except Exception as e:
        classification = error_handler.classify_error(e)
        
    # 監査ログ確認
    audit_logs = read_audit_logs()
    assert any(log["event_type"] == "ERROR_OCCURRED" for log in audit_logs)
    
    # 構造化ログ確認
    structured_logs = read_structured_logs()
    error_log = next(log for log in structured_logs if log["level"] == "ERROR")
    assert error_log["details"]["error_code"] == "SYS-001"
```

#### TC-402-051: パフォーマンス影響測定
**目的**: ログ機能追加によるパフォーマンス影響が許容範囲内であることを確認

**測定方法**:
```python
def test_logging_performance_impact():
    # ログ無効時の処理時間測定
    start_time = time.time()
    process_sample_data_without_logging()
    baseline_time = time.time() - start_time
    
    # ログ有効時の処理時間測定
    start_time = time.time()
    process_sample_data_with_logging()
    with_logging_time = time.time() - start_time
    
    # オーバーヘッド確認（3%以内）
    overhead = (with_logging_time - baseline_time) / baseline_time
    assert overhead <= 0.03  # 3%以内
```

## テスト実行計画

### フェーズ1: 単体テスト（構造化ログ・マスキング）
- 構造化ログ出力の基本機能テスト
- 個人情報マスキングの正確性テスト
- 設定ファイル読み込みテスト

### フェーズ2: 単体テスト（パフォーマンス・監査）
- パフォーマンス計測機能テスト
- 監査ログ生成テスト
- ローテーション機能テスト

### フェーズ3: 統合テスト
- 既存システムとの統合テスト
- エラーハンドリング連携テスト
- パフォーマンス影響測定

### フェーズ4: シナリオテスト
- エンドツーエンドの動作確認
- 実際のデータを使用した総合テスト
- 障害時の動作確認

## 成功基準

### 機能面
- [ ] 全テストケースがパス
- [ ] JSON形式ログの正確性100%
- [ ] 個人情報マスキング精度100%
- [ ] パフォーマンス計測精度95%以上

### 品質面
- [ ] コードカバレッジ90%以上
- [ ] ログ出力オーバーヘッド3%以内
- [ ] 監査ログ完全性100%

### 運用面
- [ ] ローテーション機能正常動作
- [ ] 設定変更の即座反映
- [ ] 障害耐性の確認

## テストデータ準備

### サンプルデータセット
1. **個人情報含有データ**: 氏名、メール、電話番号等を含むテストデータ
2. **大容量データ**: パフォーマンステスト用の大量データ
3. **異常データ**: エラーケーステスト用の不正データ
4. **設定ファイル**: 各種設定パターンのYAMLファイル

### モックオブジェクト
1. **時間制御**: テスト用の時間管理機能
2. **メモリ監視**: メモリ使用量の模擬計測機能
3. **ファイルシステム**: ローテーション動作の模擬機能