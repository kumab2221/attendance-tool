# TASK-201: 勤怠集計エンジン - テストケース設計

## テスト戦略

### テスト分類
1. **単体テスト**: 各計算ロジックの詳細テスト
2. **統合テスト**: 期間フィルタ連携・設定読み込み連携
3. **境界値テスト**: うるう年、月末、24時間勤務等の特殊ケース
4. **パフォーマンステスト**: 大容量データでの処理性能

### テスト対象クラス
- `AttendanceCalculator`: メイン集計処理
- `AttendanceSummary`: 集計結果モデル
- `WorkRulesEngine`: 就業規則適用
- `OvertimeCalculator`: 残業時間計算
- `VacationTracker`: 休暇管理

## 単体テスト

### T-001: 基本集計機能テスト

#### T-001-01: 出勤日数集計
```python
def test_calculate_attendance_days_normal():
    """通常の出勤日数集計テスト"""
    # Given: 20日間の勤怠データ（18日出勤、2日欠勤）
    records = create_attendance_records([
        {"work_date": "2024-01-01", "work_status": "出勤", "start_time": "09:00", "end_time": "18:00"},
        {"work_date": "2024-01-02", "work_status": "出勤", "start_time": "09:00", "end_time": "18:00"},
        # ... 16日の出勤データ
        {"work_date": "2024-01-19", "work_status": "欠勤"},
        {"work_date": "2024-01-20", "work_status": "欠勤"}
    ])
    
    # When: 出勤日数を集計
    calculator = AttendanceCalculator()
    summary = calculator.calculate(records)
    
    # Then: 18日が出勤日として集計される
    assert summary.attendance_days == 18
    assert summary.attendance_rate == 90.0  # 18/20 * 100
```

#### T-001-02: 最小勤務時間による出勤判定
```python
def test_attendance_by_minimum_work_time():
    """最小勤務時間(4時間)による出勤判定テスト"""
    # Given: work_statusが空だが4時間以上勤務
    records = create_attendance_records([
        {"work_date": "2024-01-01", "start_time": "09:00", "end_time": "13:30", "break_minutes": 30},  # 4時間勤務
        {"work_date": "2024-01-02", "start_time": "09:00", "end_time": "12:00", "break_minutes": 0},   # 3時間勤務
    ])
    
    # When: 出勤日数を集計
    summary = calculator.calculate(records)
    
    # Then: 4時間以上勤務のみ出勤日としてカウント
    assert summary.attendance_days == 1
```

#### T-001-03: 欠勤日数・欠勤率集計
```python
def test_calculate_absence_days_and_rate():
    """欠勤日数・欠勤率集計テスト"""
    # Given: 20営業日のうち3日欠勤
    records = create_business_month_records(
        attendance_days=17,
        absence_days=3
    )
    
    # When: 欠勤集計
    summary = calculator.calculate(records)
    
    # Then: 欠勤日数3日、欠勤率15%
    assert summary.absence_days == 3
    assert summary.absence_rate == 15.0  # 3/20 * 100
```

### T-002: 遅刻・早退集計テスト

#### T-002-01: 遅刻回数・時間集計
```python
def test_calculate_tardiness():
    """遅刻回数・時間集計テスト"""
    # Given: 標準開始時刻09:00、遅刻閾値1分、丸め単位15分
    records = create_attendance_records([
        {"work_date": "2024-01-01", "start_time": "09:00", "end_time": "18:00"},  # 定時
        {"work_date": "2024-01-02", "start_time": "09:05", "end_time": "18:00"},  # 5分遅刻→15分切り上げ
        {"work_date": "2024-01-03", "start_time": "09:20", "end_time": "18:00"},  # 20分遅刻→30分切り上げ
        {"work_date": "2024-01-04", "start_time": "08:59", "end_time": "18:00"},  # 1分早出
    ])
    
    # When: 遅刻集計
    summary = calculator.calculate(records)
    
    # Then: 遅刻2回、遅刻時間45分(15+30)
    assert summary.tardiness_count == 2
    assert summary.tardiness_minutes == 45
```

#### T-002-02: 早退回数・時間集計
```python
def test_calculate_early_leave():
    """早退回数・時間集計テスト"""
    # Given: 標準終了時刻18:00、早退閾値1分
    records = create_attendance_records([
        {"work_date": "2024-01-01", "start_time": "09:00", "end_time": "18:00"},  # 定時
        {"work_date": "2024-01-02", "start_time": "09:00", "end_time": "17:50"},  # 10分早退→15分切り上げ
        {"work_date": "2024-01-03", "start_time": "09:00", "end_time": "17:30"},  # 30分早退
    ])
    
    # When: 早退集計
    summary = calculator.calculate(records)
    
    # Then: 早退2回、早退時間45分
    assert summary.early_leave_count == 2
    assert summary.early_leave_minutes == 45
```

### T-003: 残業時間集計テスト

#### T-003-01: 所定残業時間計算
```python
def test_calculate_scheduled_overtime():
    """所定残業時間計算テスト"""
    # Given: 標準勤務8時間、実働10時間
    records = create_attendance_records([
        {"work_date": "2024-01-01", "start_time": "09:00", "end_time": "20:00", "break_minutes": 60}  # 10時間勤務
    ])
    
    # When: 所定残業計算
    summary = calculator.calculate(records)
    
    # Then: 2時間(120分)の所定残業
    assert summary.scheduled_overtime_minutes == 120
```

#### T-003-02: 深夜労働時間計算
```python
def test_calculate_late_night_work():
    """深夜労働時間計算テスト(22:00-5:00)"""
    # Given: 22:00-翌2:00の4時間勤務
    records = create_attendance_records([
        {"work_date": "2024-01-01", "start_time": "22:00", "end_time": "02:00", "break_minutes": 0}
    ])
    
    # When: 深夜労働計算
    summary = calculator.calculate(records)
    
    # Then: 4時間(240分)の深夜労働
    assert summary.late_night_work_minutes == 240
```

#### T-003-03: 休日労働時間計算
```python
def test_calculate_holiday_work():
    """休日労働時間計算テスト"""
    # Given: 2024-01-01(元日・祝日)の8時間勤務
    records = create_attendance_records([
        {"work_date": "2024-01-01", "start_time": "09:00", "end_time": "18:00", "break_minutes": 60}
    ])
    
    # When: 休日労働計算
    summary = calculator.calculate(records)
    
    # Then: 8時間(480分)の休日労働
    assert summary.holiday_work_minutes == 480
```

#### T-003-04: 割増率適用テスト
```python
def test_overtime_premium_rates():
    """残業割増率適用テスト"""
    # Given: 平日10時間+深夜2時間の勤務
    records = create_attendance_records([
        {"work_date": "2024-01-15", "start_time": "09:00", "end_time": "23:00", "break_minutes": 60}  # 平日13時間
    ])
    
    # When: 割増計算
    summary = calculator.calculate(records)
    
    # Then: 
    # - 所定残業: 5時間 * 1.25 = 6.25時間分
    # - 深夜労働: 1時間 * 1.25 = 1.25時間分  
    # - 深夜残業重複: 1時間 * 1.50 = 1.50時間分
    assert summary.overtime_pay_minutes == 375    # 6.25時間
    assert summary.late_night_pay_minutes == 75   # 1.25時間
```

### T-004: 休暇集計テスト

#### T-004-01: 有給休暇集計
```python
def test_calculate_paid_leave():
    """有給休暇集計テスト"""
    # Given: 月内3日の有給取得
    records = create_attendance_records([
        {"work_date": "2024-01-01", "work_status": "有給"},
        {"work_date": "2024-01-02", "work_status": "有給"},  
        {"work_date": "2024-01-03", "work_status": "有給"},
        # 残り17日は通常勤務
    ])
    
    # When: 有給集計
    summary = calculator.calculate(records)
    
    # Then: 有給3日取得、残り17日
    assert summary.paid_leave_days == 3
    assert summary.remaining_paid_leave == 17  # 年間20日 - 3日
```

#### T-004-02: 時間単位有給計算
```python
def test_calculate_hourly_paid_leave():
    """時間単位有給計算テスト"""
    # Given: 4時間勤務+4時間有給の日
    records = create_attendance_records([
        {"work_date": "2024-01-01", "start_time": "09:00", "end_time": "13:00", "work_status": "有給", "break_minutes": 0}
    ])
    
    # When: 時間単位有給計算
    summary = calculator.calculate(records)
    
    # Then: 0.5日分の有給使用
    assert summary.paid_leave_hours == 4.0
```

#### T-004-03: 特別休暇集計
```python
def test_calculate_special_leave():
    """特別休暇集計テスト"""
    # Given: 特別休暇2日
    records = create_attendance_records([
        {"work_date": "2024-01-01", "work_status": "特別休暇"},
        {"work_date": "2024-01-02", "work_status": "特別休暇"}
    ])
    
    # When: 特別休暇集計
    summary = calculator.calculate(records)
    
    # Then: 特別休暇2日
    assert summary.special_leave_days == 2
```

## 境界値テスト

### T-005: エッジケーステスト

#### T-005-01: 0分勤務処理
```python
def test_zero_work_time():
    """0分勤務データの処理テスト"""
    # Given: 同一時刻の出退勤
    records = create_attendance_records([
        {"work_date": "2024-01-01", "start_time": "09:00", "end_time": "09:00"}
    ])
    
    # When: 集計処理
    summary = calculator.calculate(records)
    
    # Then: 出勤日としてカウントされない
    assert summary.attendance_days == 0
    assert summary.total_work_minutes == 0
```

#### T-005-02: 24時間勤務処理
```python
def test_24_hour_work():
    """24時間勤務データの処理テスト"""
    # Given: 24時間連続勤務
    records = create_attendance_records([
        {"work_date": "2024-01-01", "start_time": "09:00", "end_time": "09:00", "break_minutes": 60}  # 日跨ぎ
    ])
    
    # When: 集計処理
    summary = calculator.calculate(records)
    
    # Then: 警告付きで処理される
    assert summary.total_work_minutes == 1380  # 23時間
    assert "24時間勤務" in summary.warnings
```

#### T-005-03: 月末・月初処理
```python  
def test_month_boundary_processing():
    """月末・月初の日跨ぎ勤務処理テスト"""
    # Given: 1月31日23:00-2月1日02:00の勤務
    records = create_attendance_records([
        {"work_date": "2024-01-31", "start_time": "23:00", "end_time": "02:00"}
    ])
    
    # When: 1月分として集計
    summary = calculator.calculate(records, period="2024-01")
    
    # Then: 正しく3時間勤務として処理
    assert summary.total_work_minutes == 180
```

#### T-005-04: うるう年2月29日処理
```python
def test_leap_year_february_29():
    """うるう年2月29日の処理テスト"""
    # Given: 2024年2月29日の勤怠データ
    records = create_attendance_records([
        {"work_date": "2024-02-29", "start_time": "09:00", "end_time": "18:00", "break_minutes": 60}
    ])
    
    # When: 2月分として集計
    summary = calculator.calculate(records, period="2024-02")
    
    # Then: 正常に処理される
    assert summary.attendance_days == 1
    assert summary.total_work_minutes == 480
```

### T-006: 就業規則上限チェックテスト

#### T-006-01: 月間残業上限チェック
```python
def test_monthly_overtime_limit_check():
    """月間残業時間上限チェックテスト"""
    # Given: 月間50時間(3000分)の残業
    records = create_overtime_records(total_overtime_minutes=3000)
    
    # When: 集計処理（上限45時間=2700分）
    summary = calculator.calculate(records)
    
    # Then: 上限超過警告
    assert "月間残業時間上限超過" in summary.violations
    assert summary.scheduled_overtime_minutes == 3000
```

#### T-006-02: 連続勤務日数チェック
```python
def test_consecutive_work_days_check():
    """連続勤務日数チェックテスト"""
    # Given: 7日連続勤務
    records = create_consecutive_work_records(days=7)
    
    # When: 集計処理（上限6日）
    summary = calculator.calculate(records)
    
    # Then: 連続勤務警告
    assert "連続勤務日数超過" in summary.warnings
```

## 統合テスト

### T-007: 期間フィルタリング連携テスト

#### T-007-01: 月次集計統合
```python
def test_monthly_calculation_integration():
    """月次集計の統合テスト"""
    # Given: 3か月分のデータから1月分をフィルタリング
    all_records = create_multi_month_records(["2023-12", "2024-01", "2024-02"])
    filtered_result = date_filter.filter_by_month(all_records, "2024-01")
    
    # When: フィルタ結果で集計
    summary = calculator.calculate(filtered_result.filtered_data)
    
    # Then: 1月分のみ集計される
    assert summary.period_start == date(2024, 1, 1)
    assert summary.period_end == date(2024, 1, 31)
```

### T-008: 設定ファイル連携テスト

#### T-008-01: 就業規則設定適用
```python  
def test_work_rules_integration():
    """就業規則設定適用統合テスト"""
    # Given: カスタム就業規則（所定労働時間7時間）
    work_rules = {"working_hours": {"standard_daily_minutes": 420}}
    calculator = AttendanceCalculator(work_rules=work_rules)
    
    records = create_attendance_records([
        {"work_date": "2024-01-01", "start_time": "09:00", "end_time": "18:00", "break_minutes": 60}  # 8時間
    ])
    
    # When: 集計（7時間基準）
    summary = calculator.calculate(records)
    
    # Then: 1時間の残業として計算
    assert summary.scheduled_overtime_minutes == 60
```

## パフォーマンステスト

### T-009: 大容量データ処理テスト

#### T-009-01: 100名×1か月処理性能
```python
@pytest.mark.performance
def test_large_data_processing():
    """大容量データ処理性能テスト"""
    # Given: 100名×31日=3100レコード
    records = create_large_dataset(employees=100, days=31)
    
    # When: 処理時間測定
    start_time = time.time()
    summaries = calculator.calculate_batch(records)
    end_time = time.time()
    
    # Then: 5分以内で処理完了
    processing_time = end_time - start_time
    assert processing_time < 300  # 5分 = 300秒
    assert len(summaries) == 100
```

#### T-009-02: メモリ使用量テスト
```python
@pytest.mark.performance  
def test_memory_usage():
    """メモリ使用量テスト"""
    # Given: 大容量データ
    records = create_large_dataset(employees=100, days=31)
    
    # When: メモリ使用量監視しながら処理
    import psutil
    process = psutil.Process()
    initial_memory = process.memory_info().rss
    
    summaries = calculator.calculate_batch(records)
    
    peak_memory = process.memory_info().rss
    memory_usage = peak_memory - initial_memory
    
    # Then: 1GB以下のメモリ使用
    assert memory_usage < 1024 * 1024 * 1024  # 1GB
```

## エラーハンドリングテスト

### T-010: 異常データ処理テスト

#### T-010-01: 不正データスキップ
```python
def test_invalid_data_handling():
    """不正データの処理テスト"""
    # Given: 正常データ + 不正データの混在
    records = [
        create_valid_record("2024-01-01"),
        create_invalid_record("2024-01-02", "負の勤務時間"),
        create_valid_record("2024-01-03")
    ]
    
    # When: 集計処理
    summary = calculator.calculate(records)
    
    # Then: 不正データをスキップして処理
    assert summary.attendance_days == 2
    assert "データエラー" in summary.warnings
```

## テストヘルパー関数

```python
def create_attendance_records(data_list):
    """テスト用勤怠レコード作成"""
    records = []
    for data in data_list:
        record = AttendanceRecord(
            employee_id="EMP001",
            employee_name="テスト太郎", 
            **data
        )
        records.append(record)
    return records

def create_business_month_records(attendance_days, absence_days):
    """営業月のレコード作成（出勤・欠勤日数指定）"""
    # 実装詳細...
    
def create_overtime_records(total_overtime_minutes):
    """残業時間指定レコード作成"""  
    # 実装詳細...

def create_large_dataset(employees, days):
    """大容量テストデータ作成"""
    # 実装詳細...
```

## 実行コマンド

```bash
# 全テスト実行
pytest tests/unit/calculation/ -v

# 単体テストのみ
pytest tests/unit/calculation/test_calculator.py -v

# 境界値テストのみ  
pytest tests/unit/calculation/ -k "boundary" -v

# パフォーマンステスト
pytest tests/unit/calculation/ -k "performance" -v --tb=short

# カバレッジ付き実行
pytest tests/unit/calculation/ --cov=src/attendance_tool/calculation --cov-report=html
```

## 期待されるカバレッジ

- **行カバレッジ**: 95%以上
- **ブランチカバレッジ**: 90%以上  
- **関数カバレッジ**: 100%

各計算ロジック、エラーハンドリング、境界値処理すべてがテストされることを確保する。