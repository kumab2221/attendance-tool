# 単体テスト ガイドライン（Unit Test Guidelines）

## 概要

このドキュメントは、勤怠管理ツールの単体テスト作成における品質基準、ベストプラクティス、および実装ガイドラインを定義します。

## 単体テストの原則

### 基本原則

#### 1. **F.I.R.S.T 原則**
- **Fast**: 高速実行（<100ms/テスト）
- **Independent**: 独立性（テスト間の依存なし）
- **Repeatable**: 再現可能（環境に依存しない）
- **Self-validating**: 自己検証（明確な成功/失敗判定）
- **Timely**: 適時性（実装と同時にテスト作成）

#### 2. **AAA パターン**
```python
def test_calculate_working_hours():
    # Arrange: テスト準備
    start_time = datetime(2024, 1, 15, 9, 0)
    end_time = datetime(2024, 1, 15, 18, 0)
    calculator = WorkingHoursCalculator()
    
    # Act: 実行
    result = calculator.calculate(start_time, end_time)
    
    # Assert: 検証
    assert result == 8.0
```

#### 3. **単一責務原則**
- 1つのテストケース = 1つの機能/条件の検証
- テストメソッド名で何をテストするか明確化
- 複数のassertは避ける（関連する場合は例外）

## テスト命名規則

### テストクラス命名
```python
# ✅ 良い例
class TestCSVReader:
    """CSVReader クラスのテスト"""

class TestWorkingHoursCalculator:
    """勤務時間計算機のテスト"""

# ❌ 悪い例  
class CSVTest:  # 何をテストするか不明確
class Tests:    # 汎用的すぎる
```

### テストメソッド命名
```python
# ✅ 良い例
def test_read_csv_with_valid_file_returns_dataframe():
    """正常なCSVファイル読み込みでDataFrameを返す"""

def test_calculate_overtime_hours_when_working_10_hours():
    """10時間勤務時の残業時間計算"""

def test_validate_attendance_data_raises_error_for_invalid_date():
    """不正な日付データでバリデーションエラーが発生する"""

# ❌ 悪い例
def test_csv():              # 何をテストするか不明
def test_calculate():        # 何を計算するか不明
def test_error():           # どのエラーか不明
```

### 命名パターン
```
test_[機能名]_[条件]_[期待結果]()

例:
test_read_csv_with_empty_file_returns_empty_dataframe()
test_calculate_monthly_summary_for_february_handles_leap_year()
test_validate_time_format_with_invalid_format_raises_validation_error()
```

## テストデータ管理

### フィクスチャの活用

#### pytest フィクスチャ
```python
import pytest
from datetime import datetime
from attendance_tool.models import AttendanceRecord

@pytest.fixture
def sample_attendance_record():
    """サンプル勤怠レコード"""
    return AttendanceRecord(
        employee_id="EMP001",
        date=datetime(2024, 1, 15),
        start_time=datetime(2024, 1, 15, 9, 0),
        end_time=datetime(2024, 1, 15, 18, 0),
        break_minutes=60
    )

@pytest.fixture
def csv_sample_data():
    """テスト用CSVデータ"""
    return """employee_id,date,start_time,end_time,break_minutes
EMP001,2024-01-15,09:00,18:00,60
EMP002,2024-01-15,08:30,17:30,60
EMP003,2024-01-15,10:00,19:00,60"""

# テスト内での使用
def test_read_csv_creates_correct_records(csv_sample_data):
    reader = CSVReader()
    records = reader.read_from_string(csv_sample_data)
    assert len(records) == 3
    assert records[0].employee_id == "EMP001"
```

#### クラスレベルフィクスチャ
```python
class TestWorkingHoursCalculator:
    @pytest.fixture(autouse=True)
    def setup_calculator(self):
        """各テスト前に実行される"""
        self.calculator = WorkingHoursCalculator()
        self.standard_work_hours = 8.0
    
    def test_calculate_standard_working_day(self):
        # self.calculator が利用可能
        result = self.calculator.calculate_daily_hours(
            start=datetime(2024, 1, 15, 9, 0),
            end=datetime(2024, 1, 15, 18, 0)
        )
        assert result == self.standard_work_hours
```

### テストデータビルダーパターン
```python
class AttendanceRecordBuilder:
    """テストデータ構築用ビルダー"""
    
    def __init__(self):
        self._employee_id = "EMP001"
        self._date = datetime.now().date()
        self._start_time = datetime.combine(self._date, time(9, 0))
        self._end_time = datetime.combine(self._date, time(18, 0))
        self._break_minutes = 60
    
    def with_employee_id(self, employee_id: str):
        self._employee_id = employee_id
        return self
    
    def with_overtime(self, overtime_hours: float):
        self._end_time = self._start_time.replace(
            hour=18 + int(overtime_hours)
        )
        return self
    
    def with_late_arrival(self, late_minutes: int):
        self._start_time = self._start_time.replace(
            minute=late_minutes
        )
        return self
    
    def build(self) -> AttendanceRecord:
        return AttendanceRecord(
            employee_id=self._employee_id,
            date=self._date,
            start_time=self._start_time,
            end_time=self._end_time,
            break_minutes=self._break_minutes
        )

# 使用例
def test_calculate_overtime_for_late_employee():
    # Arrange
    record = (AttendanceRecordBuilder()
              .with_employee_id("EMP999")
              .with_late_arrival(30)
              .with_overtime(2.0)
              .build())
    
    calculator = OvertimeCalculator()
    
    # Act
    overtime = calculator.calculate(record)
    
    # Assert
    assert overtime == 2.0
```

## モックとスタブ

### unittest.mock の活用

#### 外部依存のモック
```python
from unittest.mock import Mock, patch, MagicMock
import pytest

class TestCSVReader:
    
    @patch('attendance_tool.data.csv_reader.pd.read_csv')
    def test_read_csv_calls_pandas_with_correct_parameters(self, mock_read_csv):
        # Arrange
        mock_read_csv.return_value = Mock()
        reader = CSVReader()
        
        # Act
        reader.read_file('test.csv')
        
        # Assert
        mock_read_csv.assert_called_once_with(
            'test.csv',
            encoding='utf-8',
            parse_dates=['date']
        )
    
    @patch('attendance_tool.data.csv_reader.Path.exists')
    def test_read_csv_raises_error_when_file_not_exists(self, mock_exists):
        # Arrange
        mock_exists.return_value = False
        reader = CSVReader()
        
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            reader.read_file('nonexistent.csv')
```

#### メソッドレベルモック
```python
class TestAttendanceValidator:
    
    def test_validate_calls_all_validation_rules(self):
        # Arrange
        validator = AttendanceValidator()
        validator.validate_time_format = Mock(return_value=True)
        validator.validate_date_range = Mock(return_value=True)
        validator.validate_work_hours = Mock(return_value=True)
        
        record = AttendanceRecord(...)
        
        # Act
        result = validator.validate(record)
        
        # Assert
        assert result is True
        validator.validate_time_format.assert_called_once_with(record)
        validator.validate_date_range.assert_called_once_with(record)
        validator.validate_work_hours.assert_called_once_with(record)
```

### テストダブルの使い分け

#### 1. Dummy - 引数埋めのみ
```python
def test_process_records_handles_empty_callback():
    processor = RecordProcessor()
    dummy_callback = Mock()  # 呼ばれることはない
    
    result = processor.process([], callback=dummy_callback)
    
    assert result == []
```

#### 2. Stub - 固定値返却
```python
class StubConfigManager:
    def get_work_hours_limit(self):
        return 8.0  # 固定値
    
    def get_overtime_threshold(self):
        return 1.0  # 固定値

def test_overtime_calculation_with_stub():
    config = StubConfigManager()
    calculator = OvertimeCalculator(config)
    
    overtime = calculator.calculate_overtime(9.5)  # 9.5時間勤務
    
    assert overtime == 1.5  # 8.0 - 1.0 = 1.5時間の残業
```

#### 3. Spy - 呼び出し監視
```python
def test_logger_called_on_error():
    logger_spy = Mock()
    processor = DataProcessor(logger=logger_spy)
    
    processor.process_invalid_data("invalid")
    
    # 呼び出し確認
    logger_spy.error.assert_called_once()
    args, kwargs = logger_spy.error.call_args
    assert "invalid data" in args[0].lower()
```

#### 4. Mock - 振る舞い定義
```python
def test_database_save_retry_on_failure():
    mock_db = Mock()
    # 1回目失敗、2回目成功のシミュレーション
    mock_db.save.side_effect = [ConnectionError(), True]
    
    repository = AttendanceRepository(db=mock_db)
    
    result = repository.save_with_retry(record)
    
    assert result is True
    assert mock_db.save.call_count == 2
```

## 例外テストのベストプラクティス

### pytest.raises の活用
```python
def test_csv_reader_raises_validation_error_for_invalid_format():
    reader = CSVReader()
    
    with pytest.raises(ValidationError) as exc_info:
        reader.read_file('invalid_format.csv')
    
    # 例外メッセージの検証
    assert "Invalid CSV format" in str(exc_info.value)
    
    # 例外の詳細属性検証
    assert exc_info.value.error_code == "CSV_FORMAT_ERROR"

def test_calculator_raises_value_error_for_negative_hours():
    calculator = WorkingHoursCalculator()
    
    with pytest.raises(ValueError, match=r"Working hours cannot be negative"):
        calculator.calculate(-1.5)
```

### 例外の詳細テスト
```python
def test_attendance_validator_provides_detailed_error_info():
    validator = AttendanceValidator()
    invalid_record = AttendanceRecord(
        employee_id="",  # 空のID
        date=datetime(2024, 13, 1),  # 不正な月
        start_time=None  # 欠損時刻
    )
    
    with pytest.raises(ValidationError) as exc_info:
        validator.validate(invalid_record)
    
    error = exc_info.value
    assert len(error.errors) == 3  # 3つのエラー
    assert any("employee_id" in err.field for err in error.errors)
    assert any("date" in err.field for err in error.errors)
    assert any("start_time" in err.field for err in error.errors)
```

## パラメータ化テスト

### pytest.mark.parametrize の活用
```python
@pytest.mark.parametrize("start_time,end_time,expected_hours", [
    ("09:00", "18:00", 8.0),    # 標準勤務
    ("08:30", "17:30", 8.0),    # 早出早退
    ("10:00", "19:00", 8.0),    # 遅出遅退
    ("09:00", "20:00", 10.0),   # 残業
    ("14:00", "18:00", 3.0),    # 短時間勤務
])
def test_working_hours_calculation(start_time, end_time, expected_hours):
    calculator = WorkingHoursCalculator()
    
    result = calculator.calculate_from_strings(start_time, end_time)
    
    assert result == expected_hours
```

### 複雑なパラメータ化
```python
@pytest.mark.parametrize("test_case", [
    {
        "name": "standard_workday",
        "input": {"start": "09:00", "end": "18:00", "break": 60},
        "expected": {"work_hours": 8.0, "overtime": 0.0}
    },
    {
        "name": "overtime_workday", 
        "input": {"start": "09:00", "end": "20:00", "break": 60},
        "expected": {"work_hours": 10.0, "overtime": 2.0}
    },
    {
        "name": "short_workday",
        "input": {"start": "10:00", "end": "15:00", "break": 30},
        "expected": {"work_hours": 4.5, "overtime": 0.0}
    }
])
def test_comprehensive_work_calculation(test_case):
    calculator = WorkingHoursCalculator()
    
    result = calculator.calculate_comprehensive(
        start_time=test_case["input"]["start"],
        end_time=test_case["input"]["end"],
        break_minutes=test_case["input"]["break"]
    )
    
    assert result.work_hours == test_case["expected"]["work_hours"]
    assert result.overtime == test_case["expected"]["overtime"]
```

### エッジケースのパラメータ化
```python
@pytest.mark.parametrize("invalid_date,expected_error", [
    ("2024-02-30", "Invalid day"),      # 存在しない日
    ("2024-13-01", "Invalid month"),    # 不正な月
    ("2023-02-29", "Not a leap year"),  # 非うるう年
    ("", "Empty date"),                 # 空文字
    ("invalid", "Invalid format"),      # 不正フォーマット
])
def test_date_validation_errors(invalid_date, expected_error):
    validator = DateValidator()
    
    with pytest.raises(ValidationError, match=expected_error):
        validator.validate(invalid_date)
```

## 境界値テスト

### 境界値の網羅的テスト
```python
class TestWorkingHoursValidation:
    """勤務時間バリデーションの境界値テスト"""
    
    @pytest.mark.parametrize("hours,is_valid", [
        # 正常な境界値
        (0.0, True),     # 最小値
        (0.1, True),     # 最小値付近
        (23.9, True),    # 最大値付近  
        (24.0, True),    # 最大値
        
        # 異常な境界値
        (-0.1, False),   # 最小値未満
        (24.1, False),   # 最大値超過
        (-1.0, False),   # 明らかに異常
        (25.0, False),   # 明らかに異常
    ])
    def test_working_hours_boundary_validation(self, hours, is_valid):
        validator = WorkingHoursValidator()
        
        if is_valid:
            validator.validate(hours)  # 例外が発生しない
        else:
            with pytest.raises(ValidationError):
                validator.validate(hours)
```

### 日付境界値テスト
```python
@pytest.mark.parametrize("year,month,day,is_valid", [
    # 月末の境界値
    (2024, 1, 31, True),    # 1月末
    (2024, 1, 32, False),   # 1月末+1
    (2024, 2, 29, True),    # うるう年2月末
    (2024, 2, 30, False),   # うるう年2月末+1
    (2023, 2, 28, True),    # 平年2月末
    (2023, 2, 29, False),   # 平年2月末+1
    
    # 年境界値
    (1999, 12, 31, True),   # 20世紀最後
    (2000, 1, 1, True),     # 21世紀最初
    (9999, 12, 31, True),   # システム上限
])
def test_date_boundary_values(year, month, day, is_valid):
    date_validator = DateValidator()
    date_str = f"{year:04d}-{month:02d}-{day:02d}"
    
    if is_valid:
        result = date_validator.parse(date_str)
        assert result.year == year
        assert result.month == month
        assert result.day == day
    else:
        with pytest.raises(ValidationError):
            date_validator.parse(date_str)
```

## パフォーマンステスト

### 実行時間測定
```python
import time
import pytest

def test_large_data_processing_performance():
    """大容量データ処理のパフォーマンステスト"""
    # Arrange
    processor = DataProcessor()
    large_dataset = generate_test_data(10000)  # 10,000件
    
    # Act
    start_time = time.time()
    result = processor.process_all(large_dataset)
    end_time = time.time()
    
    # Assert
    execution_time = end_time - start_time
    assert execution_time < 5.0  # 5秒以内
    assert len(result) == 10000
    assert all(record.is_valid for record in result)

# pytest-benchmark 使用例
def test_calculation_performance(benchmark):
    """計算処理のベンチマークテスト"""
    calculator = WorkingHoursCalculator()
    test_data = create_calculation_test_data()
    
    # benchmark関数で測定
    result = benchmark(calculator.calculate_monthly_summary, test_data)
    
    assert result.total_hours > 0
```

### メモリ使用量テスト
```python
import psutil
import os

def test_memory_usage_within_limit():
    """メモリ使用量制限テスト"""
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss
    
    # 大容量データ処理
    processor = LargeDataProcessor()
    large_data = generate_large_dataset(50000)
    
    processor.process(large_data)
    
    final_memory = process.memory_info().rss
    memory_increase = final_memory - initial_memory
    
    # メモリ増加が500MB以下
    assert memory_increase < 500 * 1024 * 1024
```

## テストの保守性

### DRYの原則
```python
class TestAttendanceCalculator:
    """勤怠計算機のテストクラス"""
    
    def setup_method(self):
        """各テストメソッド前の共通処理"""
        self.calculator = AttendanceCalculator()
        self.standard_config = WorkRulesConfig(
            standard_hours=8.0,
            overtime_threshold=8.0,
            max_daily_hours=12.0
        )
    
    def create_attendance_record(self, **kwargs):
        """テスト用勤怠レコード作成ヘルパー"""
        defaults = {
            "employee_id": "EMP001",
            "date": datetime(2024, 1, 15),
            "start_time": datetime(2024, 1, 15, 9, 0),
            "end_time": datetime(2024, 1, 15, 18, 0),
            "break_minutes": 60
        }
        defaults.update(kwargs)
        return AttendanceRecord(**defaults)
    
    def test_standard_workday_calculation(self):
        # ヘルパーメソッド使用で簡潔に
        record = self.create_attendance_record()
        result = self.calculator.calculate(record, self.standard_config)
        assert result.regular_hours == 8.0
        assert result.overtime_hours == 0.0
    
    def test_overtime_workday_calculation(self):
        # 残業ケース：終了時刻のみ変更
        record = self.create_attendance_record(
            end_time=datetime(2024, 1, 15, 20, 0)  # 20時まで
        )
        result = self.calculator.calculate(record, self.standard_config)
        assert result.regular_hours == 8.0
        assert result.overtime_hours == 2.0
```

### テスト可読性の向上
```python
def test_monthly_summary_calculation_for_mixed_attendance_patterns():
    """
    混在する勤務パターンでの月次集計テスト
    
    テストケース:
    - 標準勤務日: 20日
    - 残業勤務日: 5日 (平均2時間残業)  
    - 遅刻日: 3日
    - 有給日: 2日
    """
    # Given: 多様な勤務パターンのデータ
    attendance_data = AttendanceDataBuilder() \
        .add_standard_days(20) \
        .add_overtime_days(5, average_overtime=2.0) \
        .add_late_days(3, average_late_minutes=15) \
        .add_paid_leave_days(2) \
        .for_month(2024, 1) \
        .build()
    
    calculator = MonthlyCalculator()
    
    # When: 月次集計実行
    summary = calculator.calculate_monthly_summary(attendance_data)
    
    # Then: 期待される結果
    assert summary.total_work_days == 28  # 30日 - 有給2日
    assert summary.total_regular_hours == 224.0  # 28日 × 8時間
    assert summary.total_overtime_hours == 10.0  # 5日 × 2時間
    assert summary.late_count == 3
    assert summary.paid_leave_days == 2
    
    # 品質指標の確認
    assert summary.attendance_rate >= 0.95  # 95%以上の出勤率
```

## テスト品質チェックリスト

### ✅ テスト作成時のチェック項目

#### 基本事項
- [ ] テスト名が機能・条件・期待結果を表現している
- [ ] AAA パターンに従っている
- [ ] 1テスト1機能の原則を守っている
- [ ] テストが独立している（他のテストに依存しない）

#### カバレッジ
- [ ] 正常系がカバーされている
- [ ] 異常系がカバーされている  
- [ ] 境界値がテストされている
- [ ] エッジケースが考慮されている

#### 品質
- [ ] テストが高速（<100ms）
- [ ] 期待値がハードコードされていない
- [ ] モックが適切に使用されている
- [ ] テストデータが意味を持っている

#### 保守性
- [ ] 重複コードが排除されている
- [ ] ヘルパーメソッドが適切に使用されている
- [ ] テストの意図が明確
- [ ] 将来の変更に対して耐性がある

### 🔍 レビュー時のチェック項目

#### コードレビュー
- [ ] テストケースの網羅性
- [ ] アサーションの妥当性
- [ ] テストデータの適切性
- [ ] パフォーマンスへの配慮

#### 設計レビュー
- [ ] テスト戦略との整合性
- [ ] 他のテストとの整合性
- [ ] 将来の拡張性
- [ ] メンテナンス負荷

---

**作成日**: 2025-08-11  
**最終更新**: 2025-08-11  
**バージョン**: 1.0  
**作成者**: Development Team  
**レビュー者**: QA Team Lead