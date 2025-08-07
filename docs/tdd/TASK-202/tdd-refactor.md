# TASK-202: 就業規則エンジン - Refactor Phase実装

## Refactor Phase概要

Green Phaseでテストが通る基本実装を完了した後、コードの品質向上とメンテナンス性の改善を行います。
基本的な違反検出機能が動作することを保持しながら、以下の観点でリファクタリングを実施します：

- 残りの違反検出機能の実装
- エラーハンドリングの強化  
- コードの可読性向上
- 設定ファイルとの連携強化
- パフォーマンスの改善

## リファクタリング対象

### 1. 未実装機能の追加実装

#### 1.1 連続勤務日数チェック機能

**実装内容:**
```python
def check_consecutive_work_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """連続勤務日数違反チェック - Refactor Phase実装"""
    violations = []
    
    if not records:
        return violations
    
    # 日付順にソート
    sorted_records = sorted(records, key=lambda r: r.work_date)
    
    # 連続勤務日数をカウント
    consecutive_days = 0
    current_date = None
    
    for record in sorted_records:
        # 出勤日のみをチェック
        work_minutes = record.get_work_duration_minutes()
        is_work_day = (record.work_status == "出勤" or 
                      (work_minutes is not None and work_minutes >= 240))  # 4時間以上
        
        if is_work_day:
            from datetime import timedelta
            if current_date is None:
                consecutive_days = 1
                current_date = record.work_date
            elif record.work_date == current_date + timedelta(days=1):
                consecutive_days += 1
                current_date = record.work_date
            else:
                consecutive_days = 1
                current_date = record.work_date
            
            # 連続勤務日数のチェック
            warning_days = self.get_consecutive_work_warning_days()
            critical_days = self.work_rules.get("consecutive_work_limits", {}).get("critical_days", 10)
            
            if consecutive_days > warning_days:
                from .violations import WorkRuleViolation, ViolationLevel
                
                # 違反レベルの決定
                if consecutive_days >= critical_days:
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
            current_date = None
    
    return violations
```

#### 1.2 月次違反チェック機能

**実装内容:**
```python
def check_monthly_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """月次違反チェック - Refactor Phase実装"""
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
    
    # 月間残業上限チェック
    monthly_limit = self.get_monthly_overtime_limit()
    special_limit = self.work_rules.get("overtime", {}).get("limits", {}).get("special_monthly_limit", 6000)
    
    if total_overtime_minutes > monthly_limit:
        from .violations import WorkRuleViolation, ViolationLevel
        
        if total_overtime_minutes > special_limit:
            level = ViolationLevel.CRITICAL
            violation_type = "monthly_special_limit"
            message = f"特別条項上限を超過しています（{total_overtime_minutes//60:.1f}時間）"
            legal_ref = "労働基準法第36条・特別条項"
            suggestion = "直ちに労働時間の削減が必要です"
            threshold = special_limit
        else:
            level = ViolationLevel.VIOLATION
            violation_type = "monthly_overtime_limit"
            message = f"月間残業時間上限を超過しています（{total_overtime_minutes//60:.1f}時間）"
            legal_ref = "労働基準法第36条"
            suggestion = "残業時間の削減をお願いします"
            threshold = monthly_limit
        
        # 代表日として月の最後の勤務日を使用
        work_records = [r for r in records if r.get_work_duration_minutes() and r.get_work_duration_minutes() > 0]
        if work_records:
            last_work_record = max(work_records, key=lambda r: r.work_date)
            
            violation = WorkRuleViolation(
                violation_type=violation_type,
                level=level,
                message=message,
                affected_date=last_work_record.work_date,
                actual_value=total_overtime_minutes,
                threshold_value=threshold,
                suggestion=suggestion,
                legal_reference=legal_ref,
                employee_id=last_work_record.employee_id
            )
            violations.append(violation)
    
    return violations
```

#### 1.3 深夜労働・休日労働チェック機能

**実装内容:**
```python
def check_night_work_violations(self, record: 'AttendanceRecord') -> List['WorkRuleViolation']:
    """深夜労働違反チェック - Refactor Phase実装"""
    violations = []
    
    if not record.start_time or not record.end_time:
        return violations
    
    # 深夜労働時間を正確に計算
    night_work_minutes = self._calculate_night_work_minutes(record)
    
    if night_work_minutes > 0:
        from .violations import WorkRuleViolation, ViolationLevel
        
        violation = WorkRuleViolation(
            violation_type="night_work",
            level=ViolationLevel.INFO,
            message=f"深夜労働が検出されました（{night_work_minutes}分）",
            affected_date=record.work_date,
            actual_value=night_work_minutes,
            threshold_value=0,  # 深夜労働は情報として記録
            suggestion="深夜労働による健康影響にご注意ください",
            legal_reference="労働基準法第37条（深夜割増賃金）",
            employee_id=record.employee_id
        )
        violations.append(violation)
    
    return violations

def _calculate_night_work_minutes(self, record: 'AttendanceRecord') -> int:
    """深夜労働時間を正確に計算"""
    from datetime import datetime, time
    
    night_start = time(22, 0)  # 22:00
    night_end = time(5, 0)     # 05:00
    
    start_time = record.start_time
    end_time = record.end_time
    
    # 同日勤務の場合
    if start_time <= end_time:
        # 深夜時間帯との重複計算
        if start_time >= night_start:  # 22:00以降開始
            return min((end_time.hour * 60 + end_time.minute) - (start_time.hour * 60 + start_time.minute), 7 * 60)
        elif end_time <= night_end:  # 05:00以前終了
            return (end_time.hour * 60 + end_time.minute)
        else:
            return 0
    else:
        # 日跨ぎ勤務の場合
        night_minutes = 0
        
        # 22:00から24:00まで
        if start_time >= night_start:
            night_minutes += (24 - start_time.hour) * 60 - start_time.minute
        else:
            night_minutes += 2 * 60  # 22:00-24:00の2時間
        
        # 00:00から05:00まで
        if end_time <= night_end:
            night_minutes += end_time.hour * 60 + end_time.minute
        else:
            night_minutes += 5 * 60  # 00:00-05:00の5時間
        
        return min(night_minutes, record.get_work_duration_minutes() or 0)

def check_holiday_work_violations(self, record: 'AttendanceRecord') -> List['WorkRuleViolation']:
    """休日労働違反チェック - Refactor Phase実装"""
    violations = []
    
    # 祝日・土日判定
    is_weekend = record.work_date.weekday() >= 5  # 土日
    is_national_holiday = self.is_holiday(record.work_date)
    
    if is_weekend or is_national_holiday:
        work_minutes = record.get_work_duration_minutes()
        if work_minutes and work_minutes > 0:
            from .violations import WorkRuleViolation, ViolationLevel
            
            holiday_type = "国民の祝日" if is_national_holiday else "土日"
            violation = WorkRuleViolation(
                violation_type="holiday_work",
                level=ViolationLevel.INFO,
                message=f"{holiday_type}での労働が検出されました（{work_minutes//60:.1f}時間）",
                affected_date=record.work_date,
                actual_value=work_minutes,
                threshold_value=0,
                suggestion="休日労働による健康影響にご注意ください",
                legal_reference="労働基準法第37条（休日割増賃金）",
                employee_id=record.employee_id
            )
            violations.append(violation)
    
    return violations
```

### 2. 統合メソッドの拡充

#### 2.1 全違反チェック統合の完全版

**Before (Green Phase):**
```python
def check_all_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    # 基本的なチェックのみ
    all_violations = []
    for record in records:
        all_violations.extend(self.check_daily_work_hour_violations(record))
        all_violations.extend(self.check_break_time_violations(record))
    return all_violations
```

**After (Refactor Phase):**
```python
def check_all_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """全違反チェック統合メソッド - Refactor Phase完全版"""
    all_violations = []
    
    try:
        # 個別レコードのチェック
        for record in records:
            all_violations.extend(self.check_daily_work_hour_violations(record))
            all_violations.extend(self.check_break_time_violations(record))
            all_violations.extend(self.check_night_work_violations(record))
            all_violations.extend(self.check_holiday_work_violations(record))
        
        # 複数レコードが必要なチェック
        all_violations.extend(self.check_consecutive_work_violations(records))
        all_violations.extend(self.check_monthly_violations(records))
        
        # 週次チェック（簡易版）
        all_violations.extend(self.check_weekly_work_hour_violations(records))
        
    except Exception as e:
        # エラーが発生しても処理を継続（ログに記録）
        import logging
        logging.warning(f"違反チェック中にエラーが発生しました: {e}")
    
    return all_violations
```

#### 2.2 週次労働時間チェック実装

```python
def check_weekly_work_hour_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """週次労働時間違反チェック - Refactor Phase実装"""
    violations = []
    
    if not records:
        return violations
    
    # 週ごとにレコードをグループ化
    weekly_groups = self._group_records_by_week(records)
    
    legal_weekly_limit = self.work_rules.get("work_hour_limits", {}).get("weekly_legal_minutes", 2400)  # 40時間
    warning_weekly_limit = self.work_rules.get("work_hour_limits", {}).get("weekly_warning_minutes", 3600)  # 60時間
    
    for week_start, week_records in weekly_groups.items():
        total_week_minutes = sum(
            record.get_work_duration_minutes() or 0 
            for record in week_records
        )
        
        if total_week_minutes > legal_weekly_limit:
            from .violations import WorkRuleViolation, ViolationLevel
            
            level = ViolationLevel.CRITICAL if total_week_minutes > warning_weekly_limit else ViolationLevel.WARNING
            violation_type = "weekly_excessive_work" if total_week_minutes > warning_weekly_limit else "weekly_overtime"
            
            # 週の最後の勤務日を代表日とする
            last_work_record = max(week_records, key=lambda r: r.work_date)
            
            violation = WorkRuleViolation(
                violation_type=violation_type,
                level=level,
                message=f"週間労働時間が上限を超えています（{total_week_minutes//60:.1f}時間）",
                affected_date=last_work_record.work_date,
                actual_value=total_week_minutes,
                threshold_value=legal_weekly_limit,
                suggestion="週間労働時間の削減をお願いします",
                legal_reference="労働基準法第32条（週40時間制）",
                employee_id=last_work_record.employee_id
            )
            violations.append(violation)
    
    return violations

def _group_records_by_week(self, records: List['AttendanceRecord']) -> Dict[date, List['AttendanceRecord']]:
    """レコードを週ごとにグループ化"""
    from datetime import timedelta
    from collections import defaultdict
    
    weekly_groups = defaultdict(list)
    
    for record in records:
        # 週の開始日（月曜日）を計算
        days_since_monday = record.work_date.weekday()
        week_start = record.work_date - timedelta(days=days_since_monday)
        weekly_groups[week_start].append(record)
    
    return dict(weekly_groups)
```

### 3. コンプライアンスレポート生成

#### 3.1 詳細なレポート生成機能

```python
def generate_compliance_report(self, records: List['AttendanceRecord']) -> 'ComplianceReport':
    """法令遵守レポート生成 - Refactor Phase実装"""
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
    from .violations import ViolationLevel
    critical_count = len([v for v in violations if v.level == ViolationLevel.CRITICAL])
    violation_count = len([v for v in violations if v.level == ViolationLevel.VIOLATION])  
    warning_count = len([v for v in violations if v.level == ViolationLevel.WARNING])
    info_count = len([v for v in violations if v.level == ViolationLevel.INFO])
    
    # 期間計算
    dates = [record.work_date for record in records]
    period_start = min(dates)
    period_end = max(dates)
    
    # コンプライアンススコア計算（0-100点）
    compliance_score = self._calculate_compliance_score(
        critical_count, violation_count, warning_count, len(records)
    )
    
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
        compliance_score=compliance_score
    )

def _calculate_compliance_score(self, critical_count: int, violation_count: int, 
                               warning_count: int, total_records: int) -> float:
    """コンプライアンススコア計算"""
    # 基本点100点から減点方式
    base_score = 100.0
    
    # 重大違反: -20点/件
    base_score -= critical_count * 20
    
    # 違反: -10点/件
    base_score -= violation_count * 10
    
    # 警告: -5点/件
    base_score -= warning_count * 5
    
    # 記録数に応じた調整（記録が多い場合は減点を軽減）
    if total_records > 20:
        reduction_factor = min(0.5, 20 / total_records)
        base_score = base_score * reduction_factor + 100 * (1 - reduction_factor)
    
    return max(0.0, min(100.0, base_score))
```

### 4. エラーハンドリング強化

#### 4.1 例外処理の追加

```python
def check_daily_work_hour_violations(self, record: 'AttendanceRecord') -> List['WorkRuleViolation']:
    """日次労働時間違反チェック - エラーハンドリング強化版"""
    violations = []
    
    try:
        # 入力検証
        if not hasattr(record, 'get_work_duration_minutes'):
            return violations
        
        work_minutes = record.get_work_duration_minutes()
        if work_minutes is None or work_minutes < 0:
            return violations
        
        # 異常値チェック
        if work_minutes > 2880:  # 48時間を超える場合はエラーデータとして扱う
            import logging
            logging.warning(f"異常な勤務時間データ: {work_minutes}分 (従業員ID: {record.employee_id})")
            return violations
        
        # 既存の違反チェックロジック...
        legal_limit = self.get_daily_legal_minutes()
        # ... (既存コード)
        
    except Exception as e:
        import logging
        logging.error(f"日次労働時間チェック中にエラー: {e} (従業員ID: {getattr(record, 'employee_id', 'unknown')})")
        return violations
    
    return violations
```

### 5. 設定ファイル連携強化

#### 5.1 詳細設定項目の対応

```python
# 新しい設定取得メソッドの追加

def get_weekly_legal_minutes(self) -> int:
    """週次法定労働時間（分）を取得"""
    return self.work_rules.get("work_hour_limits", {}).get("weekly_legal_minutes", 2400)

def get_weekly_warning_minutes(self) -> int:
    """週次警告労働時間（分）を取得"""
    return self.work_rules.get("work_hour_limits", {}).get("weekly_warning_minutes", 3600)

def get_night_work_start_time(self) -> time:
    """深夜労働開始時刻を取得"""
    time_str = self.work_rules.get("night_work_rules", {}).get("night_start_time", "22:00")
    hour, minute = map(int, time_str.split(':'))
    return time(hour, minute)

def get_night_work_end_time(self) -> time:
    """深夜労働終了時刻を取得"""
    time_str = self.work_rules.get("night_work_rules", {}).get("night_end_time", "05:00")
    hour, minute = map(int, time_str.split(':'))
    return time(hour, minute)

def get_consecutive_work_critical_days(self) -> int:
    """連続勤務重大違反日数を取得"""
    return self.work_rules.get("consecutive_work_limits", {}).get("critical_days", 10)
```

### 6. パフォーマンス最適化

#### 6.1 効率的なチェック処理

```python
def check_all_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """全違反チェック統合メソッド - パフォーマンス最適化版"""
    if not records:
        return []
    
    all_violations = []
    
    # レコード前処理（一度だけソート）
    sorted_records = sorted(records, key=lambda r: r.work_date)
    
    # バッチ処理でチェック項目を最適化
    try:
        # 個別レコードのチェック（並列処理可能）
        individual_violations = []
        for record in records:
            record_violations = []
            record_violations.extend(self.check_daily_work_hour_violations(record))
            record_violations.extend(self.check_break_time_violations(record))
            record_violations.extend(self.check_night_work_violations(record))
            record_violations.extend(self.check_holiday_work_violations(record))
            individual_violations.extend(record_violations)
        
        all_violations.extend(individual_violations)
        
        # 集約チェック（一度だけ実行）
        aggregate_violations = []
        aggregate_violations.extend(self.check_consecutive_work_violations(sorted_records))
        aggregate_violations.extend(self.check_monthly_violations(sorted_records))
        aggregate_violations.extend(self.check_weekly_work_hour_violations(sorted_records))
        
        all_violations.extend(aggregate_violations)
        
    except Exception as e:
        import logging
        logging.warning(f"違反チェック中にエラーが発生しました: {e}")
    
    return all_violations
```

### 7. Refactor Phase実装順序

#### Step 1: 未実装機能の完全実装
- [x] `check_consecutive_work_violations` 完全実装
- [x] `check_monthly_violations` 完全実装
- [x] `check_weekly_work_hour_violations` 実装

#### Step 2: 情報レベル機能の詳細化
- [x] `check_night_work_violations` 詳細実装
- [x] `check_holiday_work_violations` 詳細実装

#### Step 3: エラーハンドリング強化
- [x] 例外処理の追加
- [x] 異常データの適切な処理
- [x] ログ出力の追加

#### Step 4: 統合機能の強化
- [x] `check_all_violations` パフォーマンス最適化
- [x] `generate_compliance_report` 詳細実装

### 8. リファクタリング後の確認項目

- [ ] 全機能が正常に動作する
- [ ] パフォーマンスが向上している
- [ ] エラーハンドリングが強化されている
- [ ] 設定ファイル連携が充実している
- [ ] コードの可読性が向上している
- [ ] テストが全て通る
- [ ] 既存機能への影響がない

Refactor Phase完了後、就業規則エンジンは労働基準法に準拠した包括的な違反検出機能を提供し、
実用的なコンプライアンスチェックシステムとして機能します。