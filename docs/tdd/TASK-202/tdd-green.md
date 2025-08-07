# TASK-202: 就業規則エンジン - Green Phase実装

## Green Phase概要

Red Phaseで失敗するテストを確認した後、**テストが通る最小限の実装**を行います。
この段階では、美しいコードより「動くコード」を最優先とし、基本的な違反検出ロジックを実装します。

## 実装方針

### 実装優先順位
1. `check_daily_work_hour_violations` の基本実装
2. `check_break_time_violations` の基本実装  
3. `check_consecutive_work_violations` の基本実装
4. `calculate_with_violations` 統合メソッドの基本実装
5. その他のメソッドは最小実装

### Green Phase制約
- **最小実装**: 必要最小限のロジックのみ
- **ハードコード許可**: 閾値の固定値使用OK
- **エラーハンドリング**: 後回し
- **最適化**: 後回し

## 実装内容

### 1. 日次労働時間違反チェック実装

#### 1.1 基本的な残業検出

```python
def check_daily_work_hour_violations(self, record: 'AttendanceRecord') -> List['WorkRuleViolation']:
    """日次労働時間違反チェック - Green Phase最小実装"""
    violations = []
    
    # 勤務時間を取得
    work_minutes = record.get_work_duration_minutes()
    if work_minutes is None:
        return violations
    
    # 法定労働時間チェック（8時間 = 480分）
    legal_limit = self.get_daily_legal_minutes()
    if work_minutes > legal_limit:
        from .violations import WorkRuleViolation, ViolationLevel
        violation = WorkRuleViolation(
            violation_type="daily_overtime",
            level=ViolationLevel.WARNING,
            message=f"法定労働時間を超過しています（{work_minutes//60:.1f}時間）",
            affected_date=record.work_date,
            actual_value=work_minutes,
            threshold_value=legal_limit,
            suggestion="勤務時間の見直しを検討してください",
            legal_reference="労働基準法第32条",
            employee_id=record.employee_id
        )
        violations.append(violation)
    
    # 異常労働時間チェック（12時間 = 720分）
    warning_limit = self.get_daily_warning_minutes()
    if work_minutes > warning_limit:
        violation = WorkRuleViolation(
            violation_type="excessive_daily_work",
            level=ViolationLevel.CRITICAL,
            message=f"異常な長時間労働です（{work_minutes//60:.1f}時間）",
            affected_date=record.work_date,
            actual_value=work_minutes,
            threshold_value=warning_limit,
            suggestion="緊急に労働時間の短縮が必要です",
            legal_reference="労働基準法第32条・安全配慮義務",
            employee_id=record.employee_id
        )
        violations.append(violation)
    
    # 24時間勤務チェック
    if work_minutes >= 1440:  # 24時間 = 1440分
        violation = WorkRuleViolation(
            violation_type="24_hour_work",
            level=ViolationLevel.CRITICAL,
            message=f"24時間以上の連続勤務です（{work_minutes//60:.1f}時間）",
            affected_date=record.work_date,
            actual_value=work_minutes,
            threshold_value=1440,
            suggestion="直ちに勤務体制の見直しが必要です",
            legal_reference="労働基準法第32条・労働安全衛生法",
            employee_id=record.employee_id
        )
        violations.append(violation)
    
    return violations
```

### 2. 休憩時間違反チェック実装

#### 2.1 法定休憩時間チェック

```python
def check_break_time_violations(self, record: 'AttendanceRecord') -> List['WorkRuleViolation']:
    """休憩時間違反チェック - Green Phase最小実装"""
    violations = []
    
    work_minutes = record.get_work_duration_minutes()
    if work_minutes is None:
        return violations
    
    # 必要休憩時間を取得
    required_break = self.get_required_break_minutes(work_minutes)
    actual_break = record.break_minutes or 0
    
    # 休憩時間不足チェック
    if required_break > 0 and actual_break < required_break:
        from .violations import WorkRuleViolation, ViolationLevel
        
        # 法的根拠の決定
        if work_minutes > 8 * 60:  # 8時間超
            legal_ref = "労働基準法第34条（8時間超勤務時60分休憩）"
        elif work_minutes > 6 * 60:  # 6時間超
            legal_ref = "労働基準法第34条（6時間超勤務時45分休憩）"
        else:
            legal_ref = "労働基準法第34条"
        
        violation = WorkRuleViolation(
            violation_type="insufficient_break",
            level=ViolationLevel.WARNING,
            message=f"必要な休憩時間が不足しています（実際：{actual_break}分、必要：{required_break}分）",
            affected_date=record.work_date,
            actual_value=actual_break,
            threshold_value=required_break,
            suggestion="適切な休憩時間の確保をお願いします",
            legal_reference=legal_ref,
            employee_id=record.employee_id
        )
        violations.append(violation)
    
    return violations
```

### 3. 連続勤務日数違反チェック実装

#### 3.1 基本的な連続勤務検出

```python
def check_consecutive_work_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """連続勤務日数違反チェック - Green Phase最小実装"""
    violations = []
    
    if not records:
        return violations
    
    # 日付順にソート
    sorted_records = sorted(records, key=lambda r: r.work_date)
    
    # 連続勤務日数をカウント
    consecutive_days = 0
    current_streak = []
    
    for i, record in enumerate(sorted_records):
        # 出勤日のみをチェック
        work_minutes = record.get_work_duration_minutes()
        is_work_day = (record.work_status == "出勤" or 
                      (work_minutes is not None and work_minutes >= 240))  # 4時間以上
        
        if is_work_day:
            if i == 0:
                consecutive_days = 1
                current_streak = [record]
            else:
                prev_date = sorted_records[i-1].work_date
                current_date = record.work_date
                
                # 前日から連続かチェック
                from datetime import timedelta
                if current_date == prev_date + timedelta(days=1):
                    consecutive_days += 1
                    current_streak.append(record)
                else:
                    consecutive_days = 1
                    current_streak = [record]
            
            # 連続勤務日数のチェック
            warning_days = self.get_consecutive_work_warning_days()
            if consecutive_days > warning_days:
                from .violations import WorkRuleViolation, ViolationLevel
                
                # 違反レベルの決定
                if consecutive_days >= 10:
                    level = ViolationLevel.CRITICAL
                    message = f"危険な連続勤務です（{consecutive_days}日連続）"
                    suggestion = "直ちに休日を取得してください"
                else:
                    level = ViolationLevel.WARNING
                    message = f"連続勤務日数が上限を超えています（{consecutive_days}日連続）"
                    suggestion = "適切な休日の確保をお願いします"
                
                violation = WorkRuleViolation(
                    violation_type="consecutive_work_days",
                    level=level,
                    message=message,
                    affected_date=record.work_date,
                    actual_value=consecutive_days,
                    threshold_value=warning_days,
                    suggestion=suggestion,
                    legal_reference="労働基準法第35条（休日の確保）",
                    employee_id=record.employee_id
                )
                violations.append(violation)
        else:
            # 休日で連続勤務がリセット
            consecutive_days = 0
            current_streak = []
    
    return violations
```

### 4. 月次違反チェック実装

#### 4.1 月間残業時間チェック

```python
def check_monthly_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """月次違反チェック - Green Phase最小実装"""
    violations = []
    
    if not records:
        return violations
    
    # 月間総残業時間を計算
    total_overtime_minutes = 0
    standard_work_minutes = self.get_standard_work_minutes()
    
    for record in records:
        work_minutes = record.get_work_duration_minutes()
        if work_minutes and work_minutes > standard_work_minutes:
            overtime = work_minutes - standard_work_minutes
            total_overtime_minutes += overtime
    
    # 月間残業上限チェック（45時間 = 2700分）
    monthly_limit = self.get_monthly_overtime_limit()
    if total_overtime_minutes > monthly_limit:
        from .violations import WorkRuleViolation, ViolationLevel
        
        # 特別条項上限チェック（100時間 = 6000分）
        special_limit = self.work_rules.get("overtime", {}).get("limits", {}).get("special_monthly_limit", 6000)
        
        if total_overtime_minutes > special_limit:
            level = ViolationLevel.CRITICAL
            violation_type = "monthly_special_limit"
            message = f"特別条項上限を超過しています（{total_overtime_minutes//60:.1f}時間）"
            legal_ref = "労働基準法第36条・特別条項"
            suggestion = "直ちに労働時間の削減が必要です"
        else:
            level = ViolationLevel.VIOLATION
            violation_type = "monthly_overtime_limit"
            message = f"月間残業時間上限を超過しています（{total_overtime_minutes//60:.1f}時間）"
            legal_ref = "労働基準法第36条"
            suggestion = "残業時間の削減をお願いします"
        
        # 代表日として月の最後の勤務日を使用
        last_work_record = max(records, key=lambda r: r.work_date)
        
        violation = WorkRuleViolation(
            violation_type=violation_type,
            level=level,
            message=message,
            affected_date=last_work_record.work_date,
            actual_value=total_overtime_minutes,
            threshold_value=monthly_limit if level == ViolationLevel.VIOLATION else special_limit,
            suggestion=suggestion,
            legal_reference=legal_ref,
            employee_id=last_work_record.employee_id
        )
        violations.append(violation)
    
    return violations
```

### 5. その他のメソッド最小実装

#### 5.1 深夜労働・休日労働（情報レベル）

```python
def check_night_work_violations(self, record: 'AttendanceRecord') -> List['WorkRuleViolation']:
    """深夜労働違反チェック - Green Phase最小実装"""
    violations = []
    
    if not record.start_time or not record.end_time:
        return violations
    
    # 深夜時間帯かどうかの簡単な判定
    night_start = 22  # 22:00
    night_end = 5     # 05:00
    
    start_hour = record.start_time.hour
    end_hour = record.end_time.hour
    
    # 深夜時間帯での勤務かチェック
    is_night_work = False
    if record.start_time <= record.end_time:  # 同日勤務
        if start_hour >= night_start or end_hour <= night_end:
            is_night_work = True
    else:  # 日跨ぎ勤務
        is_night_work = True  # 日跨ぎは深夜労働とみなす
    
    if is_night_work:
        from .violations import WorkRuleViolation, ViolationLevel
        work_minutes = record.get_work_duration_minutes() or 0
        
        violation = WorkRuleViolation(
            violation_type="night_work",
            level=ViolationLevel.INFO,
            message=f"深夜労働が検出されました（{start_hour}:00-{end_hour}:00）",
            affected_date=record.work_date,
            actual_value=work_minutes,
            threshold_value=0,  # 深夜労働は情報として記録
            suggestion="深夜労働による健康影響にご注意ください",
            legal_reference="労働基準法第37条（深夜割増賃金）",
            employee_id=record.employee_id
        )
        violations.append(violation)
    
    return violations

def check_holiday_work_violations(self, record: 'AttendanceRecord') -> List['WorkRuleViolation']:
    """休日労働違反チェック - Green Phase最小実装"""
    violations = []
    
    # 祝日判定
    if self.is_holiday(record.work_date):
        work_minutes = record.get_work_duration_minutes()
        if work_minutes and work_minutes > 0:
            from .violations import WorkRuleViolation, ViolationLevel
            
            violation = WorkRuleViolation(
                violation_type="holiday_work",
                level=ViolationLevel.INFO,
                message=f"休日労働が検出されました（{work_minutes//60:.1f}時間）",
                affected_date=record.work_date,
                actual_value=work_minutes,
                threshold_value=0,  # 休日労働は情報として記録
                suggestion="休日労働による健康影響にご注意ください",
                legal_reference="労働基準法第37条（休日割増賃金）",
                employee_id=record.employee_id
            )
            violations.append(violation)
    
    return violations
```

### 6. 統合メソッドの実装

#### 6.1 全違反チェック統合

```python
def check_all_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """全違反チェック統合メソッド - Green Phase最小実装"""
    all_violations = []
    
    # 個別レコードのチェック
    for record in records:
        all_violations.extend(self.check_daily_work_hour_violations(record))
        all_violations.extend(self.check_break_time_violations(record))
        all_violations.extend(self.check_night_work_violations(record))
        all_violations.extend(self.check_holiday_work_violations(record))
    
    # 複数レコードが必要なチェック
    all_violations.extend(self.check_consecutive_work_violations(records))
    all_violations.extend(self.check_monthly_violations(records))
    
    # 週次チェックは後回し（Green Phase: 空実装）
    # all_violations.extend(self.check_weekly_work_hour_violations(records))
    
    return all_violations

def check_weekly_work_hour_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """週次労働時間違反チェック - Green Phase最小実装（空実装）"""
    # Green Phase: 最小実装として空のリストを返す
    return []
```

### 7. AttendanceCalculator統合実装

#### 7.1 違反チェック付き集計

```python
def calculate_with_violations(self, records: List[AttendanceRecord], period: Optional[str] = None) -> tuple[AttendanceSummary, List['WorkRuleViolation']]:
    """集計結果と違反情報を同時生成 - Green Phase最小実装"""
    # 通常の集計を実行
    summary = self.calculate(records, period)
    
    # 違反チェックを実行
    violations = self.rules_engine.check_all_violations(records)
    
    # 違反情報をサマリーに統合
    updated_summary = self._integrate_violation_warnings(summary, violations)
    
    return updated_summary, violations

def _integrate_violation_warnings(self, summary: AttendanceSummary, violations: List['WorkRuleViolation']) -> AttendanceSummary:
    """違反情報をサマリーに統合 - Green Phase最小実装"""
    # 違反情報を文字列リストに変換してサマリーに追加
    violation_messages = []
    
    for violation in violations:
        message = f"{violation.violation_type}: {violation.message}"
        violation_messages.append(message)
    
    # 既存のwarningsとviolationsに追加
    if summary.warnings is None:
        summary.warnings = []
    if summary.violations is None:
        summary.violations = []
    
    # 違反レベル別に分類
    for violation in violations:
        if violation.level in [ViolationLevel.WARNING, ViolationLevel.INFO]:
            summary.warnings.append(f"{violation.violation_type}: {violation.message}")
        elif violation.level in [ViolationLevel.VIOLATION, ViolationLevel.CRITICAL]:
            summary.violations.append(f"{violation.violation_type}: {violation.message}")
    
    return summary
```

### 8. レポート生成（最小実装）

```python
def generate_compliance_report(self, records: List['AttendanceRecord']) -> 'ComplianceReport':
    """法令遵守レポート生成 - Green Phase最小実装"""
    if not records:
        from .violations import ComplianceReport
        return ComplianceReport(
            employee_id="",
            period_start=date.today(),
            period_end=date.today(),
            total_violations=0,
            critical_violations=0,
            warnings=0,
            info_items=0,
            violations=[]
        )
    
    # 全違反をチェック
    violations = self.check_all_violations(records)
    
    # 統計計算
    critical_count = len([v for v in violations if v.level == ViolationLevel.CRITICAL])
    violation_count = len([v for v in violations if v.level == ViolationLevel.VIOLATION])
    warning_count = len([v for v in violations if v.level == ViolationLevel.WARNING])
    info_count = len([v for v in violations if v.level == ViolationLevel.INFO])
    
    # 期間計算
    dates = [record.work_date for record in records]
    period_start = min(dates)
    period_end = max(dates)
    
    from .violations import ComplianceReport
    return ComplianceReport(
        employee_id=records[0].employee_id,
        period_start=period_start,
        period_end=period_end,
        total_violations=len(violations),
        critical_violations=critical_count,
        warnings=warning_count,
        info_items=info_count,
        violations=violations,
        compliance_score=max(0, 100 - (critical_count * 20 + violation_count * 10 + warning_count * 5))
    )
```

### 9. Green Phase実装順序

#### Step 1: 基本違反検出実装
- [x] `check_daily_work_hour_violations` 基本実装
- [x] `check_break_time_violations` 基本実装
- [x] 設定取得メソッドの活用

#### Step 2: 複合チェック実装
- [x] `check_consecutive_work_violations` 基本実装
- [x] `check_monthly_violations` 基本実装

#### Step 3: 情報レベル実装
- [x] `check_night_work_violations` 情報レベル実装
- [x] `check_holiday_work_violations` 情報レベル実装

#### Step 4: 統合機能実装
- [x] `check_all_violations` 統合実装
- [x] `calculate_with_violations` 統合実装
- [x] `generate_compliance_report` 最小実装

### 10. Green Phase制約事項

#### 許可されるハードコード・簡略化
- 深夜労働時間の簡単な判定（22:00-5:00固定）
- 週次チェックの未実装（空実装）
- 詳細な法的チェックの省略
- エラーハンドリングの最小化

#### 後回しにする項目
- 週次労働時間の詳細チェック
- 複雑な深夜労働時間計算
- 年次違反チェック
- 高度なエラーハンドリング
- パフォーマンス最適化

Green Phaseでは「動くコード」を最優先とし、リファクタリングは次の Refactor Phase で行います。