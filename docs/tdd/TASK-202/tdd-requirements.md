# TASK-202: 就業規則エンジン - 詳細要件定義

## タスク概要

既存のWorkRulesEngineを拡張し、労働基準法に基づく就業規則違反の検出・警告機能を実装する。法定労働時間上限チェック、休憩時間不足、連続勤務日数制限などの詳細な就業規則適用を行う。

## 要件リンク

- **REQ-404**: 就業規則準拠（労働基準法違反の検出）
- **REQ-105**: 労働時間上限チェック
- **EDGE-201-205**: エラーハンドリング強化

## 依存関係

- **TASK-201**: 勤怠集計エンジン（完了済み）
- **WorkRulesEngine**: 基本構造（実装済み）
- **AttendanceCalculator**: 統合対象（実装済み）

## 詳細要件

### 1. 労働時間上限チェック機能

#### 1.1 日次労働時間チェック
- **法定労働時間**: 1日8時間（480分）を超過した場合の検出
- **上限労働時間**: 1日12時間（720分）を超過した場合の警告
- **24時間勤務**: 1日24時間を超過した場合のエラー
- **最小勤務時間**: 4時間未満の場合の警告

#### 1.2 週次労働時間チェック
- **法定週労働時間**: 週40時間（2400分）を超過した場合の検出
- **週最大労働時間**: 週60時間（3600分）を超過した場合の警告

#### 1.3 月次労働時間チェック
- **月間残業上限**: 月45時間（2700分）を超過した場合の警告
- **特別条項適用**: 月100時間（6000分）を超過した場合の重大警告
- **月間総労働時間**: 月200時間を超過した場合の警告

#### 1.4 年次労働時間チェック
- **年間残業上限**: 年720時間（43200分）を超過した場合の違反
- **年間有給取得**: 年5日未満の場合の警告

### 2. 休憩時間規則チェック

#### 2.1 法定休憩時間
- **6時間超勤務**: 45分以上の休憩時間が必要
- **8時間超勤務**: 60分以上の休憩時間が必要
- **休憩時間不足**: 法定休憩時間を下回る場合の警告

#### 2.2 休憩時間分散
- **連続休憩**: 休憩時間が適切に分散されているかのチェック
- **休憩時間帯**: 勤務時間の中間付近での休憩取得推奨

### 3. 連続勤務日数制限

#### 3.1 連続勤務日数チェック
- **推奨上限**: 6日連続勤務を超過した場合の警告
- **法定上限**: 労働基準法上の連続勤務制限
- **休日確保**: 週1日以上の休日確保チェック

### 4. 深夜労働・休日労働規則

#### 4.1 深夜労働規則
- **深夜労働時間帯**: 22:00-5:00の勤務時間検出
- **深夜労働制限**: 深夜労働の連続制限
- **割増率適用**: 深夜労働割増（25%以上）の適用確認

#### 4.2 休日労働規則
- **法定休日**: 祝日・土日での労働検出
- **休日労働制限**: 休日労働時間の上限
- **代休取得**: 休日労働に対する代休取得推奨

### 5. 就業規則違反レベル定義

#### 5.1 警告レベル（Warning）
```python
class ViolationLevel(Enum):
    INFO = "info"           # 情報・推奨事項
    WARNING = "warning"     # 警告・注意事項  
    VIOLATION = "violation" # 違反・即座の対応が必要
    CRITICAL = "critical"   # 重大違反・法的リスク
```

#### 5.2 違反種別定義
```python
@dataclass
class WorkRuleViolation:
    """就業規則違反情報"""
    
    violation_type: str          # 違反種別
    level: ViolationLevel        # 違反レベル
    message: str                 # 違反メッセージ
    affected_date: date          # 対象日付
    actual_value: Any            # 実際の値
    threshold_value: Any         # 閾値
    suggestion: str              # 改善提案
    legal_reference: str         # 法的根拠
    
    # メタデータ
    detected_at: datetime
    employee_id: str
    rule_id: str
```

### 6. 実装対象メソッド

#### 6.1 WorkRulesEngine拡張メソッド

```python
def check_daily_work_hour_violations(self, record: AttendanceRecord) -> List[WorkRuleViolation]:
    """日次労働時間違反チェック"""

def check_weekly_work_hour_violations(self, records: List[AttendanceRecord]) -> List[WorkRuleViolation]:
    """週次労働時間違反チェック"""

def check_monthly_violations(self, records: List[AttendanceRecord]) -> List[WorkRuleViolation]:
    """月次違反チェック（残業時間上限等）"""

def check_break_time_violations(self, record: AttendanceRecord) -> List[WorkRuleViolation]:
    """休憩時間違反チェック"""

def check_consecutive_work_violations(self, records: List[AttendanceRecord]) -> List[WorkRuleViolation]:
    """連続勤務日数違反チェック"""

def check_night_work_violations(self, record: AttendanceRecord) -> List[WorkRuleViolation]:
    """深夜労働違反チェック"""

def check_holiday_work_violations(self, record: AttendanceRecord) -> List[WorkRuleViolation]:
    """休日労働違反チェック"""

def generate_compliance_report(self, records: List[AttendanceRecord]) -> ComplianceReport:
    """法令遵守レポート生成"""
```

#### 6.2 AttendanceCalculator統合メソッド

```python
def calculate_with_violations(self, records: List[AttendanceRecord]) -> Tuple[AttendanceSummary, List[WorkRuleViolation]]:
    """集計結果と違反情報を同時生成"""

def _integrate_violation_warnings(self, summary: AttendanceSummary, violations: List[WorkRuleViolation]) -> AttendanceSummary:
    """違反情報をサマリーに統合"""
```

### 7. 設定ファイル拡張

#### 7.1 work_rules.yaml拡張項目

```yaml
# 労働時間上限設定
work_hour_limits:
  daily_legal_minutes: 480        # 法定労働時間(8時間)
  daily_warning_minutes: 720      # 警告労働時間(12時間)
  daily_critical_minutes: 1080    # 重大警告(18時間)
  
  weekly_legal_minutes: 2400      # 週40時間
  weekly_warning_minutes: 3600    # 週60時間
  
  monthly_overtime_limit: 2700    # 月45時間残業
  monthly_special_limit: 6000     # 月100時間特別条項
  
  annual_overtime_limit: 43200    # 年720時間残業

# 休憩時間規則
break_time_rules:
  required_6hour_break: 45        # 6時間超勤務の必要休憩(分)
  required_8hour_break: 60        # 8時間超勤務の必要休憩(分)
  break_timing_window: 30         # 休憩時間の許容誤差(分)

# 連続勤務制限
consecutive_work_limits:
  warning_days: 6                 # 警告日数
  critical_days: 10               # 重大警告日数
  
# 深夜労働制限  
night_work_rules:
  night_start_time: "22:00"       # 深夜労働開始時刻
  night_end_time: "05:00"         # 深夜労働終了時刻
  max_consecutive_nights: 5       # 連続深夜勤務上限

# 違反メッセージ設定
violation_messages:
  daily_overtime: "法定労働時間を超過しています"
  break_shortage: "必要な休憩時間が確保されていません"
  consecutive_work: "連続勤務日数が上限を超えています"
```

### 8. エラーハンドリング要件

#### 8.1 違反検出時の動作
- 違反レベルに応じた適切なログ出力
- 集計処理は継続（違反があっても処理停止しない）
- 違反情報のAttendanceSummaryへの統合
- 法的リスクが高い場合の特別処理

#### 8.2 設定エラーハンドリング
- 不正な設定値に対するデフォルト値適用
- 設定ファイル読み込みエラーの適切な処理
- 設定値の妥当性検証

### 9. パフォーマンス要件

- **チェック処理性能**: 100名×1か月データで追加5秒以内
- **メモリ使用量**: 違反情報で追加50MB以内
- **違反検出精度**: 99%以上の正確性

### 10. アクセプタンスクライテリア

#### 10.1 正常フロー
- [ ] 日次・週次・月次の労働時間上限が正確にチェックされる
- [ ] 休憩時間不足が適切に検出される
- [ ] 連続勤務日数制限が正しく適用される
- [ ] 深夜・休日労働が正確に判定される
- [ ] 違反レベルが適切に分類される

#### 10.2 境界値・異常フロー
- [ ] 法定労働時間ちょうどでの境界値処理
- [ ] 月末・年末の期間跨ぎでの正確な計算
- [ ] 設定値の上限・下限での適切な動作
- [ ] 無効な設定値でのデフォルト値適用

#### 10.3 統合性
- [ ] AttendanceCalculatorとの正常な連携
- [ ] 既存の集計処理に影響を与えない
- [ ] 設定ファイルの動的読み込み
- [ ] 違反情報のCSV出力対応

#### 10.4 法的要件
- [ ] 労働基準法第32条（労働時間）準拠
- [ ] 労働基準法第34条（休憩時間）準拠  
- [ ] 労働基準法第35条（休日）準拠
- [ ] 労働基準法第37条（割増賃金）準拠

## 実装制約

- 既存のWorkRulesEngineクラスを拡張（破壊的変更なし）
- AttendanceCalculatorとの後方互換性維持
- 設定ファイルの既存項目との整合性
- 検出処理による集計パフォーマンスへの影響最小化

## テスト戦略

- **単体テスト**: 各違反検出ロジックの詳細テスト
- **境界値テスト**: 法定時間上限での境界値テスト  
- **統合テスト**: AttendanceCalculatorとの連携テスト
- **コンプライアンステスト**: 労働基準法準拠の確認