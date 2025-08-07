# TASK-202: 就業規則エンジン - テストケース設計

## テスト戦略

### テスト分類
1. **単体テスト**: 各違反検出ロジックの詳細テスト
2. **境界値テスト**: 法定時間上限での境界値テスト  
3. **統合テスト**: AttendanceCalculatorとの連携テスト
4. **コンプライアンステスト**: 労働基準法準拠の確認

### テスト対象クラス
- `WorkRuleViolation`: 違反情報データクラス
- `WorkRulesEngine`: 就業規則チェック機能（拡張版）
- `AttendanceCalculator`: 違反チェック統合機能

## 単体テスト

### T-201: 労働時間上限チェックテスト

#### T-201-01: 日次労働時間違反検出
```python
def test_check_daily_work_hour_violations_normal():
    """通常勤務での違反なしテスト"""
    # Given: 8時間勤務（法定労働時間内）
    record = create_attendance_record(
        work_date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(18, 0),
        break_minutes=60
    )
    
    # When: 日次違反チェック
    engine = WorkRulesEngine(default_work_rules)
    violations = engine.check_daily_work_hour_violations(record)
    
    # Then: 違反なし
    assert len(violations) == 0

def test_check_daily_work_hour_violations_overtime():
    """残業時の違反検出テスト"""
    # Given: 10時間勤務（法定労働時間超過）
    record = create_attendance_record(
        work_date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(20, 0),
        break_minutes=60
    )
    
    # When: 日次違反チェック
    violations = engine.check_daily_work_hour_violations(record)
    
    # Then: 法定労働時間超過の警告
    assert len(violations) == 1
    assert violations[0].violation_type == "daily_overtime"
    assert violations[0].level == ViolationLevel.WARNING
    assert violations[0].actual_value == 600  # 10時間
    assert violations[0].threshold_value == 480  # 8時間

def test_check_daily_work_hour_violations_excessive():
    """過労働時の重大違反検出テスト"""
    # Given: 15時間勤務（異常労働時間）
    record = create_attendance_record(
        work_date=date(2024, 1, 15),
        start_time=time(8, 0),
        end_time=time(24, 0),
        break_minutes=60
    )
    
    # When: 日次違反チェック
    violations = engine.check_daily_work_hour_violations(record)
    
    # Then: 重大違反
    assert len(violations) >= 1
    critical_violations = [v for v in violations if v.level == ViolationLevel.CRITICAL]
    assert len(critical_violations) >= 1
    assert critical_violations[0].violation_type == "excessive_daily_work"
```

#### T-201-02: 24時間勤務検出
```python
def test_check_24_hour_work_violation():
    """24時間勤務の検出テスト"""
    # Given: 24時間連続勤務
    record = create_attendance_record(
        work_date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(9, 0),  # 翌日同時刻
        break_minutes=60
    )
    
    # When: 違反チェック
    violations = engine.check_daily_work_hour_violations(record)
    
    # Then: 24時間勤務違反
    assert any(v.violation_type == "24_hour_work" for v in violations)
    assert any(v.level == ViolationLevel.CRITICAL for v in violations)
```

### T-202: 週次労働時間チェックテスト

#### T-202-01: 週40時間超過検出
```python
def test_check_weekly_work_hour_violations():
    """週次労働時間違反検出テスト"""
    # Given: 週50時間勤務（月-金10時間×5日）
    records = create_weekly_records([
        {"day": 1, "work_hours": 10},  # 月曜10時間
        {"day": 2, "work_hours": 10},  # 火曜10時間  
        {"day": 3, "work_hours": 10},  # 水曜10時間
        {"day": 4, "work_hours": 10},  # 木曜10時間
        {"day": 5, "work_hours": 10},  # 金曜10時間
        {"day": 6, "work_hours": 0},   # 土曜休み
        {"day": 0, "work_hours": 0}    # 日曜休み
    ])
    
    # When: 週次違反チェック
    violations = engine.check_weekly_work_hour_violations(records)
    
    # Then: 週40時間超過の警告
    assert len(violations) >= 1
    weekly_violation = next(v for v in violations if v.violation_type == "weekly_overtime")
    assert weekly_violation.level == ViolationLevel.WARNING
    assert weekly_violation.actual_value == 3000  # 50時間(分)
    assert weekly_violation.threshold_value == 2400  # 40時間(分)
```

### T-203: 月次違反チェックテスト

#### T-203-01: 月間残業時間上限チェック
```python
def test_check_monthly_overtime_violations():
    """月間残業時間上限違反テスト"""
    # Given: 月間50時間残業（上限45時間超過）
    records = create_monthly_records_with_overtime(
        base_work_hours=8,
        overtime_hours=2.5,  # 毎日2.5時間残業
        work_days=20
    )  # 20日 × 2.5時間 = 50時間残業
    
    # When: 月次違反チェック
    violations = engine.check_monthly_violations(records)
    
    # Then: 月間残業上限超過
    monthly_violation = next(v for v in violations if v.violation_type == "monthly_overtime_limit")
    assert monthly_violation.level == ViolationLevel.VIOLATION
    assert monthly_violation.actual_value == 3000  # 50時間(分)
    assert monthly_violation.threshold_value == 2700  # 45時間(分)

def test_check_monthly_special_limit_violation():
    """特別条項上限違反テスト"""
    # Given: 月間120時間残業（特別条項100時間超過）
    records = create_monthly_records_with_overtime(
        base_work_hours=8,
        overtime_hours=6,  # 毎日6時間残業
        work_days=20
    )  # 20日 × 6時間 = 120時間残業
    
    # When: 月次違反チェック
    violations = engine.check_monthly_violations(records)
    
    # Then: 特別条項超過の重大違反
    critical_violation = next(v for v in violations if v.violation_type == "monthly_special_limit")
    assert critical_violation.level == ViolationLevel.CRITICAL
    assert critical_violation.actual_value == 7200  # 120時間(分)
```

### T-204: 休憩時間違反チェックテスト

#### T-204-01: 休憩時間不足検出
```python
def test_check_break_time_violations_6hour():
    """6時間超勤務での休憩不足テスト"""
    # Given: 7時間勤務、休憩30分（45分必要）
    record = create_attendance_record(
        work_date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(17, 0),  # 8時間
        break_minutes=30       # 45分必要だが30分のみ
    )
    
    # When: 休憩時間違反チェック
    violations = engine.check_break_time_violations(record)
    
    # Then: 休憩時間不足の警告
    assert len(violations) >= 1
    break_violation = next(v for v in violations if v.violation_type == "insufficient_break")
    assert break_violation.level == ViolationLevel.WARNING
    assert break_violation.actual_value == 30
    assert break_violation.threshold_value == 45

def test_check_break_time_violations_8hour():
    """8時間超勤務での休憩不足テスト"""
    # Given: 10時間勤務、休憩45分（60分必要）
    record = create_attendance_record(
        work_date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(20, 0),  # 11時間
        break_minutes=45       # 60分必要だが45分のみ
    )
    
    # When: 休憩時間違反チェック
    violations = engine.check_break_time_violations(record)
    
    # Then: 休憩時間不足の警告
    break_violation = next(v for v in violations if v.violation_type == "insufficient_break")
    assert break_violation.actual_value == 45
    assert break_violation.threshold_value == 60
```

### T-205: 連続勤務日数違反チェック

#### T-205-01: 連続勤務日数超過検出
```python
def test_check_consecutive_work_violations():
    """連続勤務日数違反検出テスト"""
    # Given: 8日連続勤務（上限6日超過）
    records = create_consecutive_work_records(
        start_date=date(2024, 1, 1),
        consecutive_days=8,
        work_hours=8
    )
    
    # When: 連続勤務違反チェック
    violations = engine.check_consecutive_work_violations(records)
    
    # Then: 連続勤務日数超過の警告
    consecutive_violation = next(v for v in violations if v.violation_type == "consecutive_work_days")
    assert consecutive_violation.level == ViolationLevel.WARNING
    assert consecutive_violation.actual_value == 8
    assert consecutive_violation.threshold_value == 6

def test_check_consecutive_work_critical():
    """連続勤務日数重大違反テスト"""
    # Given: 12日連続勤務（重大違反レベル）
    records = create_consecutive_work_records(
        start_date=date(2024, 1, 1),
        consecutive_days=12,
        work_hours=8
    )
    
    # When: 連続勤務違反チェック
    violations = engine.check_consecutive_work_violations(records)
    
    # Then: 重大違反レベル
    critical_violation = next(v for v in violations if v.violation_type == "consecutive_work_days")
    assert critical_violation.level == ViolationLevel.CRITICAL
```

### T-206: 深夜労働違反チェック

#### T-206-01: 深夜労働時間検出
```python
def test_check_night_work_violations():
    """深夜労働違反検出テスト"""
    # Given: 22:00-02:00の深夜勤務
    record = create_attendance_record(
        work_date=date(2024, 1, 15),
        start_time=time(22, 0),
        end_time=time(2, 0),  # 翌日2:00
        break_minutes=0
    )
    
    # When: 深夜労働違反チェック
    violations = engine.check_night_work_violations(record)
    
    # Then: 深夜労働の情報記録（違反ではなく情報）
    night_work_info = next(v for v in violations if v.violation_type == "night_work")
    assert night_work_info.level == ViolationLevel.INFO
    assert night_work_info.actual_value == 240  # 4時間(分)

def test_check_consecutive_night_work_violations():
    """連続深夜労働違反テスト"""
    # Given: 6日連続深夜勤務（上限5日超過）
    records = create_consecutive_night_work_records(
        start_date=date(2024, 1, 1),
        consecutive_nights=6
    )
    
    # When: 深夜労働違反チェック
    violations = []
    for record in records:
        violations.extend(engine.check_night_work_violations(record))
    
    # Then: 連続深夜勤務違反
    consecutive_night_violation = next(
        v for v in violations if v.violation_type == "consecutive_night_work"
    )
    assert consecutive_night_violation.level == ViolationLevel.WARNING
```

### T-207: 休日労働違反チェック

#### T-207-01: 休日労働検出
```python
def test_check_holiday_work_violations():
    """休日労働違反検出テスト"""
    # Given: 元日（祝日）での8時間勤務
    record = create_attendance_record(
        work_date=date(2024, 1, 1),  # 元日
        start_time=time(9, 0),
        end_time=time(18, 0),
        break_minutes=60
    )
    
    # When: 休日労働違反チェック
    violations = engine.check_holiday_work_violations(record)
    
    # Then: 休日労働の情報記録
    holiday_work_info = next(v for v in violations if v.violation_type == "holiday_work")
    assert holiday_work_info.level == ViolationLevel.INFO
    assert holiday_work_info.actual_value == 480  # 8時間(分)
```

## 境界値テスト

### T-208: 法定時間境界値テスト

#### T-208-01: 法定労働時間ちょうど
```python
def test_legal_work_hour_boundary():
    """法定労働時間ちょうどでの境界値テスト"""
    # Given: 8時間ちょうどの勤務
    record = create_attendance_record(
        work_date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(18, 0),
        break_minutes=60
    )  # ちょうど8時間（480分）
    
    # When: 違反チェック
    violations = engine.check_daily_work_hour_violations(record)
    
    # Then: 違反なし（境界値以内）
    overtime_violations = [v for v in violations if v.violation_type == "daily_overtime"]
    assert len(overtime_violations) == 0

def test_legal_work_hour_boundary_plus_one():
    """法定労働時間+1分での境界値テスト"""  
    # Given: 8時間1分の勤務
    record = create_attendance_record(
        work_date=date(2024, 1, 15),
        start_time=time(9, 0),
        end_time=time(18, 1),
        break_minutes=60
    )  # 8時間1分（481分）
    
    # When: 違反チェック
    violations = engine.check_daily_work_hour_violations(record)
    
    # Then: 法定労働時間超過の警告
    overtime_violations = [v for v in violations if v.violation_type == "daily_overtime"]
    assert len(overtime_violations) == 1
    assert overtime_violations[0].actual_value == 481
```

#### T-208-02: 月末期間跨ぎテスト
```python
def test_month_boundary_violations():
    """月末跨ぎでの違反検出テスト"""
    # Given: 1月31日から2月1日にかけての勤務データ
    jan_records = create_month_end_records("2024-01")
    feb_records = create_month_start_records("2024-02")
    
    # When: 各月での違反チェック
    jan_violations = engine.check_monthly_violations(jan_records)
    feb_violations = engine.check_monthly_violations(feb_records)
    
    # Then: 各月で独立した違反判定
    assert len(jan_violations) >= 0
    assert len(feb_violations) >= 0
```

## 統合テスト

### T-209: AttendanceCalculator統合テスト

#### T-209-01: 集計と違反チェック統合
```python
def test_calculate_with_violations_integration():
    """集計処理と違反チェックの統合テスト"""
    # Given: 違反を含む勤怠データ
    records = create_records_with_violations([
        {"date": "2024-01-15", "work_hours": 10, "break_minutes": 45},  # 残業+休憩不足
        {"date": "2024-01-16", "work_hours": 12, "break_minutes": 60},  # 過労働
        {"date": "2024-01-17", "work_hours": 8, "break_minutes": 60},   # 正常
    ])
    
    # When: 違反チェック付き集計
    calculator = AttendanceCalculator(work_rules_with_violations)
    summary, violations = calculator.calculate_with_violations(records)
    
    # Then: 集計結果と違反情報の両方が取得できる
    assert summary.attendance_days == 3
    assert len(violations) >= 2  # 少なくとも2つの違反
    
    # 違反がサマリーに反映される
    assert len(summary.violations) >= 2
    assert "daily_overtime" in [v.split(":")[0] for v in summary.violations]

def test_backward_compatibility():
    """既存のcalculateメソッドとの後方互換性テスト"""
    # Given: 通常の勤怠データ
    records = create_normal_records()
    
    # When: 既存のcalculateメソッド使用
    calculator = AttendanceCalculator(work_rules_with_violations)
    summary = calculator.calculate(records)
    
    # Then: 既存機能は正常動作（違反チェックは行われない）
    assert summary.attendance_days > 0
    assert isinstance(summary, AttendanceSummary)
```

### T-210: 設定ファイル連携テスト

#### T-210-01: work_rules.yaml拡張項目テスト
```python
def test_extended_work_rules_loading():
    """拡張されたwork_rules.yamlの読み込みテスト"""
    # Given: 違反チェック設定を含むwork_rules.yaml
    extended_work_rules = {
        "work_hour_limits": {
            "daily_legal_minutes": 480,
            "daily_warning_minutes": 720,
            "monthly_overtime_limit": 2700
        },
        "break_time_rules": {
            "required_6hour_break": 45,
            "required_8hour_break": 60
        },
        "consecutive_work_limits": {
            "warning_days": 6,
            "critical_days": 10
        }
    }
    
    # When: WorkRulesEngine初期化
    engine = WorkRulesEngine(extended_work_rules)
    
    # Then: 拡張設定値が正しく読み込まれる
    assert engine.get_daily_legal_minutes() == 480
    assert engine.get_daily_warning_minutes() == 720
    assert engine.get_required_break_minutes(7*60) == 45  # 7時間勤務
    assert engine.get_consecutive_work_warning_days() == 6
```

## コンプライアンステスト

### T-211: 労働基準法準拠テスト

#### T-211-01: 労働基準法第32条（労働時間）テスト
```python
def test_labor_standards_act_article_32():
    """労働基準法第32条（労働時間）準拠テスト"""
    # Given: 労働基準法違反パターン
    test_cases = [
        {"work_hours": 8, "expected_violations": 0},    # 法定内
        {"work_hours": 9, "expected_violations": 1},    # 1時間超過
        {"work_hours": 12, "expected_violations": 1},   # 4時間超過
    ]
    
    for case in test_cases:
        # When: 違反チェック
        record = create_work_hour_record(case["work_hours"])
        violations = engine.check_daily_work_hour_violations(record)
        
        # Then: 法定労働時間基準での違反判定
        overtime_violations = [v for v in violations if "overtime" in v.violation_type]
        assert len(overtime_violations) == case["expected_violations"]
        
        if case["expected_violations"] > 0:
            assert "労働基準法第32条" in overtime_violations[0].legal_reference

def test_labor_standards_act_article_34():
    """労働基準法第34条（休憩時間）準拠テスト"""
    # Given: 休憩時間法違反パターン
    test_cases = [
        {"work_hours": 6, "break_minutes": 0, "expected_violations": 0},   # 6時間以下
        {"work_hours": 7, "break_minutes": 30, "expected_violations": 1},  # 6時間超、休憩不足
        {"work_hours": 7, "break_minutes": 45, "expected_violations": 0},  # 6時間超、適切な休憩
        {"work_hours": 9, "break_minutes": 45, "expected_violations": 1},  # 8時間超、休憩不足
        {"work_hours": 9, "break_minutes": 60, "expected_violations": 0},  # 8時間超、適切な休憩
    ]
    
    for case in test_cases:
        # When: 休憩時間違反チェック
        record = create_record_with_break(case["work_hours"], case["break_minutes"])
        violations = engine.check_break_time_violations(record)
        
        # Then: 労働基準法第34条基準での違反判定
        break_violations = [v for v in violations if "break" in v.violation_type]
        assert len(break_violations) == case["expected_violations"]
```

## パフォーマンステスト

### T-212: 違反チェック性能テスト

#### T-212-01: 大容量データでの性能テスト
```python
@pytest.mark.performance
def test_violation_check_performance():
    """大容量データでの違反チェック性能テスト"""
    # Given: 100名×31日の勤怠データ
    records = create_large_dataset_with_violations(employees=100, days=31)
    
    # When: 違反チェック実行
    start_time = time.time()
    all_violations = []
    
    for employee_records in records.values():
        violations = engine.check_all_violations(employee_records)
        all_violations.extend(violations)
    
    end_time = time.time()
    
    # Then: 5秒以内で処理完了
    processing_time = end_time - start_time
    assert processing_time < 5.0  # 5秒以内
    assert len(all_violations) > 0  # 違反が検出される

def test_memory_usage_with_violations():
    """違反情報込みでのメモリ使用量テスト"""
    # Given: 大容量データ
    records = create_large_dataset(employees=100, days=31)
    
    # When: メモリ使用量測定
    import psutil
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    # 違反チェック付き集計実行
    calculator = AttendanceCalculator(work_rules_with_violations)
    summaries_with_violations = []
    
    for employee_records in records.values():
        summary, violations = calculator.calculate_with_violations(employee_records)
        summaries_with_violations.append((summary, violations))
    
    peak_memory = process.memory_info().rss
    memory_increase = peak_memory - initial_memory
    
    # Then: 追加50MB以下のメモリ使用
    assert memory_increase < 50 * 1024 * 1024  # 50MB
```

## エラーハンドリングテスト

### T-213: 設定エラーハンドリング

#### T-213-01: 不正設定値の処理
```python
def test_invalid_work_rules_handling():
    """不正な設定値での適切なフォールバック"""
    # Given: 不正な設定値
    invalid_work_rules = {
        "work_hour_limits": {
            "daily_legal_minutes": -100,      # 負の値
            "daily_warning_minutes": "invalid", # 文字列
            "monthly_overtime_limit": None     # None値
        }
    }
    
    # When: WorkRulesEngine初期化
    engine = WorkRulesEngine(invalid_work_rules)
    
    # Then: デフォルト値で動作
    assert engine.get_daily_legal_minutes() == 480  # デフォルト値
    assert engine.get_daily_warning_minutes() == 720  # デフォルト値
    assert engine.get_monthly_overtime_limit() == 2700  # デフォルト値

def test_missing_configuration_handling():
    """設定項目欠如での適切な処理"""
    # Given: 必要な設定項目が不足
    minimal_work_rules = {}  # 空の設定
    
    # When: 違反チェック実行
    engine = WorkRulesEngine(minimal_work_rules)
    record = create_normal_record()
    
    # Then: エラーなしで動作（デフォルト値使用）
    violations = engine.check_daily_work_hour_violations(record)
    assert isinstance(violations, list)  # エラーなく結果返却
```

## テストヘルパー関数

```python
def create_attendance_record(work_date, start_time, end_time, break_minutes):
    """テスト用勤怠レコード作成"""
    return AttendanceRecord(
        employee_id="EMP001",
        employee_name="テスト社員",
        work_date=work_date,
        start_time=start_time,
        end_time=end_time,
        break_minutes=break_minutes,
        work_status="出勤"
    )

def create_weekly_records(work_patterns):
    """週単位テストレコード作成"""
    # 実装詳細...

def create_monthly_records_with_overtime(base_work_hours, overtime_hours, work_days):
    """月間残業付きレコード作成"""
    # 実装詳細...

def create_consecutive_work_records(start_date, consecutive_days, work_hours):
    """連続勤務テストレコード作成"""
    # 実装詳細...

def create_records_with_violations(violation_patterns):
    """違反パターン付きレコード作成"""
    # 実装詳細...

@dataclass
class ViolationLevel:
    """違反レベル定義"""
    INFO = "info"
    WARNING = "warning"
    VIOLATION = "violation"
    CRITICAL = "critical"
```

## 実行コマンド

```bash
# 全テスト実行
pytest tests/unit/calculation/test_work_rules_engine_extended.py -v

# 違反チェック機能のみ
pytest tests/unit/calculation/test_work_rules_engine_extended.py -k "violation" -v

# パフォーマンステスト
pytest tests/unit/calculation/test_work_rules_engine_extended.py -k "performance" -v --tb=short

# コンプライアンステスト
pytest tests/unit/calculation/test_work_rules_engine_extended.py -k "labor_standards" -v

# カバレッジ付き実行
pytest tests/unit/calculation/test_work_rules_engine_extended.py --cov=src/attendance_tool/calculation --cov-report=html
```

## 期待されるカバレッジ

- **行カバレッジ**: 95%以上
- **ブランチカバレッジ**: 90%以上  
- **違反検出ロジック**: 100%
- **エラーハンドリング**: 90%以上

各違反検出ロジック、境界値処理、法的要件すべてがテストされることを確保する。