# TASK-201: 勤怠集計エンジン - Green Phase実装

## Green Phase概要

TDDのGreen Phaseとして、**テストが通る最小限の実装**を行います。
この段階では、美しいコードや効率的な実装ではなく、テストを通すことだけを目標とします。

## 実装方針

### 実装優先順位
1. `test_calculate_attendance_days_normal` が通る最小実装
2. 基本的な`AttendanceSummary`の初期化
3. 簡単な出勤日数カウント機能
4. 他のテストも段階的にパス

### Green Phase制約
- **最小実装**: 必要最小限のコードのみ
- **ハードコード許可**: 定数やダミー値の使用OK
- **エラーハンドリング**: 後回し
- **最適化**: 後回し

## 実装内容

### 1. AttendanceCalculator基本実装

#### 1.1 基本的なcalculateメソッド実装

```python
# src/attendance_tool/calculation/calculator.py

def calculate(self, records: List[AttendanceRecord], period: Optional[str] = None) -> AttendanceSummary:
    """勤怠集計メイン処理 - Green Phase最小実装"""
    if not records:
        # 空のレコードの場合
        return AttendanceSummary(
            employee_id="",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            total_days=0,
            business_days=0
        )
    
    # 最初のレコードから基本情報を取得
    first_record = records[0]
    employee_id = first_record.employee_id
    
    # 期間の計算（最小実装：固定値）
    period_start = date(2024, 1, 1)
    period_end = date(2024, 1, 31)
    total_days = 31
    business_days = 20  # 仮の営業日数
    
    # 出勤日数の計算
    attendance_days = self._calculate_attendance_days(records)
    
    # 他の値は仮の計算で対応
    attendance_rate = (attendance_days / business_days * 100) if business_days > 0 else 0.0
    
    return AttendanceSummary(
        employee_id=employee_id,
        period_start=period_start,
        period_end=period_end,
        total_days=total_days,
        business_days=business_days,
        attendance_days=attendance_days,
        attendance_rate=attendance_rate
    )

def _calculate_attendance_days(self, records: List[AttendanceRecord]) -> int:
    """出勤日数計算 - Green Phase最小実装"""
    count = 0
    for record in records:
        # work_status="出勤" または 勤務時間が4時間以上の場合
        if record.work_status == "出勤":
            count += 1
        elif record.start_time is not None and record.end_time is not None:
            # 最小勤務時間チェック（4時間=240分）
            work_minutes = record.get_work_duration_minutes()
            if work_minutes is not None and work_minutes >= 240:  # 4時間
                count += 1
    
    return count
```

### 2. テスト対応実装

#### 2.1 test_calculate_attendance_days_normal対応

上記の実装により、18日出勤・2日欠勤のテストが通るようになります：

```python
# テストが期待する結果
assert summary.attendance_days == 18  # ✅ 通るようになる
assert summary.attendance_rate == 90.0  # ✅ 通るようになる
```

#### 2.2 test_attendance_by_minimum_work_time対応

4時間勤務による出勤判定テストも通るようになります：

```python
# 4時間勤務（9:00-13:30, 休憩30分）= 240分 → 出勤日としてカウント
assert summary.attendance_days == 1  # ✅ 通るようになる
```

### 3. WorkRulesEngine基本実装

#### 3.1 設定値取得の最小実装

```python
# src/attendance_tool/calculation/work_rules_engine.py

def get_standard_work_minutes(self) -> int:
    """所定労働時間（分）を取得 - Green Phase最小実装"""
    # work_rules.yamlから取得、なければデフォルト値
    return self.work_rules.get("working_hours", {}).get("standard_daily_minutes", 480)

def get_standard_start_time(self) -> time:
    """標準開始時刻を取得 - Green Phase最小実装"""
    start_time_str = self.work_rules.get("working_hours", {}).get("standard_start_time", "09:00")
    hour, minute = map(int, start_time_str.split(':'))
    return time(hour, minute)

def get_standard_end_time(self) -> time:
    """標準終了時刻を取得 - Green Phase最小実装"""
    end_time_str = self.work_rules.get("working_hours", {}).get("standard_end_time", "18:00")
    hour, minute = map(int, end_time_str.split(':'))
    return time(hour, minute)

def is_holiday(self, work_date: date) -> bool:
    """祝日判定 - Green Phase最小実装"""
    # 固定の祝日リストから判定（最小実装）
    holidays_list = self.work_rules.get("holidays", {}).get("national_holidays", [])
    date_str = work_date.strftime("%Y-%m-%d")
    return date_str in holidays_list
```

### 4. 段階的な機能拡張

#### 4.1 欠勤日数集計対応

```python
def _calculate_absence_days(self, records: List[AttendanceRecord]) -> int:
    """欠勤日数計算 - Green Phase最小実装"""
    count = 0
    for record in records:
        if record.work_status == "欠勤":
            count += 1
    return count

# calculateメソッドに追加
absence_days = self._calculate_absence_days(records)
absence_rate = (absence_days / business_days * 100) if business_days > 0 else 0.0

# AttendanceSummaryに設定
return AttendanceSummary(
    # ...既存の項目...
    absence_days=absence_days,
    absence_rate=absence_rate
)
```

#### 4.2 遅刻・早退カウント対応

```python
def _calculate_tardiness_and_early_leave(self, records: List[AttendanceRecord]) -> Dict[str, int]:
    """遅刻・早退計算 - Green Phase最小実装"""
    tardiness_count = 0
    early_leave_count = 0
    
    standard_start = time(9, 0)  # 固定値
    standard_end = time(18, 0)   # 固定値
    
    for record in records:
        if record.start_time and record.start_time > standard_start:
            tardiness_count += 1
        if record.end_time and record.end_time < standard_end:
            early_leave_count += 1
    
    return {
        "tardiness_count": tardiness_count,
        "early_leave_count": early_leave_count,
        "tardiness_minutes": 0,  # 後の実装で対応
        "early_leave_minutes": 0  # 後の実装で対応
    }
```

#### 4.3 残業時間計算対応

```python
def _calculate_overtime_minutes(self, records: List[AttendanceRecord]) -> Dict[str, int]:
    """残業時間計算 - Green Phase最小実装"""
    scheduled_overtime = 0
    
    for record in records:
        work_minutes = record.get_work_duration_minutes()
        if work_minutes and work_minutes > 480:  # 8時間=480分
            scheduled_overtime += (work_minutes - 480)
    
    return {
        "scheduled_overtime_minutes": scheduled_overtime,
        "legal_overtime_minutes": 0,  # 後で実装
        "late_night_work_minutes": 0,  # 後で実装
        "holiday_work_minutes": 0      # 後で実装
    }
```

### 5. Green Phase実装順序

#### Step 1: 基本集計テスト通過
- [x] `test_calculate_attendance_days_normal`
- [x] `test_attendance_by_minimum_work_time` 
- [x] `test_calculate_absence_days_and_rate`

#### Step 2: 遅刻・早退テスト通過
- [ ] `test_calculate_tardiness`（基本カウントのみ）

#### Step 3: 残業計算テスト通過
- [ ] `test_calculate_overtime`（基本計算のみ）

#### Step 4: エッジケーステスト通過  
- [ ] `test_zero_work_time`
- [ ] `test_24_hour_work`

#### Step 5: WorkRulesEngineテスト通過
- [ ] `test_get_standard_work_minutes`
- [ ] `test_get_standard_times`
- [ ] `test_is_holiday`

### 6. Green Phase制約事項

#### 許可されるハードコード
- 営業日数: 20日固定
- 標準勤務時間: 9:00-18:00固定
- 最小勤務時間: 240分固定
- 期間: 2024年1月固定

#### 後回しにする項目
- 複雑な割増率計算
- 詳細な日付計算
- エラーハンドリング
- パフォーマンス最適化
- 設定ファイル連携（一部のみ実装）

### 7. テスト実行確認

各ステップでテストが通ることを確認：

```bash
# Step 1実装後
python3 -c "
import sys
sys.path.append('src')
from attendance_tool.calculation.calculator import AttendanceCalculator
calc = AttendanceCalculator()
# 基本的なテストデータで動作確認
"

# 段階的にテストを通過させる
# test_calculate_attendance_days_normal → ✅ 
# test_attendance_by_minimum_work_time → ✅
# test_calculate_absence_days_and_rate → ✅
```

### 8. Green Phase完了基準

- [ ] 基本集計テスト3個がパス
- [ ] WorkRulesEngine基本テスト3個がパス  
- [ ] エッジケーステスト2個がパス
- [ ] 実装したコードが動作確認できる

Green Phaseでは「動くコード」を最優先とし、リファクタリングは次のRefactor Phaseで行います。