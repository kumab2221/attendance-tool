# TASK-402: ログ機能・監査対応 - 要件定義

## 概要

構造化ログ出力と個人情報マスキング機能、パフォーマンス計測ログ、監査ログ生成機能を実装する。既存のエラーハンドリングログ機能を拡張し、セキュリティと運用性を向上させる。

## 要件リンク

- **NFR-101**: データ保護・プライバシー（個人情報マスキング）
- **NFR-102**: アクセス制御・監査ログ
- **NFR-202**: 処理進捗表示・ログによる状況表示

## 機能要件

### 1. 構造化ログ出力（JSON形式）

#### 1.1 ログエントリ形式
```json
{
  "timestamp": "2024-01-01T10:30:00.000Z",
  "level": "INFO|DEBUG|WARNING|ERROR|CRITICAL",
  "module": "csv_reader|validator|calculator|exporter",
  "operation": "file_read|data_validation|calculation|export",
  "message": "処理メッセージ",
  "details": {
    "user_id": "masked_user_id",
    "file_path": "/path/to/file.csv",
    "record_count": 1000,
    "processing_time": 1.23,
    "memory_usage": "45MB"
  },
  "performance": {
    "start_time": "2024-01-01T10:30:00.000Z",
    "end_time": "2024-01-01T10:30:01.230Z",
    "duration_ms": 1230,
    "memory_peak_mb": 45.2,
    "cpu_usage_percent": 25.5
  },
  "correlation_id": "uuid-v4-string",
  "session_id": "session-uuid"
}
```

#### 1.2 ログレベル管理
- **DEBUG**: 詳細なデバッグ情報（開発時のみ）
- **INFO**: 通常の処理フロー（処理開始・完了等）
- **WARNING**: 警告事項（データ異常等、処理継続可能）
- **ERROR**: エラー事項（処理失敗、リトライ対象）
- **CRITICAL**: 致命的エラー（システム停止レベル）

### 2. 個人情報マスキング機能

#### 2.1 マスキング対象
- **氏名**: 日本語名前（漢字、ひらがな、カタカナ）
- **メールアドレス**: ローカル部のマスキング
- **電話番号**: 中央部分のマスキング
- **社員ID**: 一部マスキング（最初の2文字以外）
- **住所**: 詳細住所のマスキング

#### 2.2 マスキング規則
```python
マスキング例:
- 氏名: "田中太郎" → "田中***" または "****"
- メール: "tanaka@company.com" → "***@company.com"
- 電話: "090-1234-5678" → "090-****-5678"
- 社員ID: "EMP001234" → "EM*****34"
- 住所: "東京都渋谷区神南1-1-1" → "東京都渋谷区****"
```

#### 2.3 設定可能なマスキングレベル
- **STRICT**: すべて完全マスキング
- **MEDIUM**: 一部情報保持（デバッグ用）
- **LOOSE**: 最小限マスキング（開発環境用）

### 3. パフォーマンス計測ログ

#### 3.1 計測項目
- **処理時間**: 各モジュール・メソッドレベルの実行時間
- **メモリ使用量**: ピーク時とGC後のメモリ使用量
- **CPU使用率**: 処理中のCPU使用率
- **I/O統計**: ファイル読み書き回数・サイズ
- **データ処理量**: 処理件数・エラー件数・スループット

#### 3.2 パフォーマンス閾値アラート
```yaml
performance_thresholds:
  processing_time:
    warning: 30000  # 30秒
    critical: 60000 # 60秒
  memory_usage:
    warning: 512    # 512MB
    critical: 1024  # 1GB
  error_rate:
    warning: 0.05   # 5%
    critical: 0.10  # 10%
```

### 4. 監査ログの生成

#### 4.1 監査対象イベント
- **ファイルアクセス**: 読み込み・書き込み操作
- **データ処理**: 集計処理・変換処理
- **設定変更**: 設定ファイル変更・環境変数変更
- **エラー発生**: エラー・例外の発生
- **システムイベント**: 開始・終了・異常終了

#### 4.2 監査ログエントリ形式
```json
{
  "audit_id": "audit-uuid-v4",
  "timestamp": "2024-01-01T10:30:00.000Z",
  "event_type": "FILE_ACCESS|DATA_PROCESSING|CONFIG_CHANGE|ERROR_OCCURRED|SYSTEM_EVENT",
  "actor": {
    "user_id": "masked_user_id",
    "session_id": "session-uuid",
    "client_info": "attendance-tool v1.0.0"
  },
  "resource": {
    "type": "file|data|config|system",
    "identifier": "masked_resource_path",
    "properties": {}
  },
  "action": "read|write|create|update|delete|process|start|stop",
  "result": "success|failure|partial",
  "details": {
    "before_state": {},
    "after_state": {},
    "error_info": {},
    "performance_metrics": {}
  },
  "risk_level": "low|medium|high",
  "compliance_tags": ["GDPR", "SOX", "internal"]
}
```

## 非機能要件

### 1. パフォーマンス
- **ログ出力オーバーヘッド**: 全体処理時間の3%以内
- **非同期処理**: メインスレッドをブロックしない
- **バッファリング**: 高頻度ログの効率的な処理

### 2. 可用性
- **ログローテーション**: ファイルサイズ・日付ベースでのローテーション
- **冗長化**: 複数出力先への同時書き込み
- **障害耐性**: ログ出力エラーによるメイン処理への影響回避

### 3. セキュリティ
- **暗号化**: 機密ログファイルの暗号化保存
- **アクセス制御**: ログファイルへの適切な権限設定
- **完全性保証**: ログ改竄検知機能

### 4. 運用性
- **設定管理**: YAML設定ファイルによる柔軟な設定変更
- **モニタリング**: ログ出力状況の監視機能
- **ディスク使用量制御**: ログサイズ制限・自動削除

## アクセプタンスクライテリア

### AC-1: 構造化ログ出力
- [ ] JSON形式でのログ出力が正常に行われる
- [ ] 必須フィールドがすべて含まれている
- [ ] ログレベルに応じて適切な出力先に記録される
- [ ] 相関IDとセッションIDが正しく管理される

### AC-2: 個人情報マスキング
- [ ] 氏名、メール、電話番号が適切にマスキングされる
- [ ] マスキングレベルに応じた処理が行われる
- [ ] マスキング前の情報が出力されない
- [ ] 設定変更によりマスキングルールが変更される

### AC-3: パフォーマンス計測
- [ ] 処理時間、メモリ、CPU使用率が正確に計測される
- [ ] 閾値超過時にアラートが発生する
- [ ] パフォーマンスデータが構造化ログに含まれる
- [ ] 計測処理自体のオーバーヘッドが3%以内

### AC-4: 監査ログ
- [ ] 主要なイベントが監査ログに記録される
- [ ] 監査ログが改竄耐性を持つ
- [ ] コンプライアンス要件を満たす情報が記録される
- [ ] リスクレベルが適切に判定される

### AC-5: 運用機能
- [ ] ログローテーションが正常に動作する
- [ ] 設定ファイルによるログ制御が可能
- [ ] ディスク使用量が制限内に収まる
- [ ] 異常時でもログ出力が継続される

## 技術仕様

### 1. 実装ファイル構造
```
src/attendance_tool/logging/
├── __init__.py
├── structured_logger.py      # 構造化ログ機能
├── masking.py               # 個人情報マスキング
├── performance_tracker.py   # パフォーマンス計測
├── audit_logger.py          # 監査ログ
├── log_rotator.py          # ログローテーション
└── formatters.py           # ログフォーマッター
```

### 2. 設定ファイル拡張
```yaml
# config/logging_extended.yaml
logging:
  structured:
    enabled: true
    format: "json"
    fields:
      - timestamp
      - level
      - module
      - operation
      - message
      - details
      - performance
      - correlation_id
      
  masking:
    enabled: true
    level: "MEDIUM"  # STRICT|MEDIUM|LOOSE
    rules:
      - type: "name"
        pattern: "[一-龯]{2,4}"
        replacement: "****"
      - type: "email"
        pattern: "([\\w.-]+)@"
        replacement: "***@"
        
  performance:
    enabled: true
    thresholds:
      processing_time_ms: 30000
      memory_usage_mb: 512
      error_rate: 0.05
      
  audit:
    enabled: true
    events:
      - FILE_ACCESS
      - DATA_PROCESSING
      - ERROR_OCCURRED
    risk_assessment: true
    
  rotation:
    max_size: "100MB"
    max_files: 30
    compress: true
```

### 3. 既存システムとの統合
- **ErrorHandlerとの連携**: エラーログを監査ログに自動転送
- **ConfigManagerとの統合**: 統一設定管理
- **CLIとの連携**: プログレスバー更新とログ連携

## 期待される成果

1. **セキュリティ向上**
   - 個人情報漏洩リスクの最小化
   - 監査証跡の完全性保証

2. **運用性向上**
   - 問題発生時の迅速な原因特定
   - パフォーマンス問題の早期発見

3. **コンプライアンス対応**
   - GDPR、SOX法等への対応
   - 内部統制強化

4. **開発効率向上**
   - 構造化ログによるデバッグ効率化
   - 自動化されたパフォーマンス監視