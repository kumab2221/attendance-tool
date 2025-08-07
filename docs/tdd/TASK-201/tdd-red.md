# TASK-201: 勤怠集計エンジン - Red Phase実装

## Red Phase概要

TDDのRed Phaseとして、テストケースに基づいて**失敗するテスト**を実装します。
この段階では、本体のクラスは最小限の実装（例外を投げるスタブ）のみで、テストが確実に失敗することを確認します。

## 実装内容

### 1. ディレクトリ構造作成

```bash
# 計算機能用ディレクトリの作成
mkdir -p src/attendance_tool/calculation
mkdir -p tests/unit/calculation
```

### 2. 基本クラススタブの作成

#### 2.1 計算結果モデル (src/attendance_tool/calculation/summary.py)

```python
"""勤怠集計結果モデル - Red Phase実装"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class AttendanceSummary:
    """勤怠集計結果
    
    Red Phase: 必要なフィールドのみ定義、計算ロジックは未実装
    """
    
    # 基本情報
    employee_id: str
    period_start: date
    period_end: date
    total_days: int
    business_days: int
    
    # 出勤関連
    attendance_days: int = 0
    attendance_rate: float = 0.0
    average_work_hours: float = 0.0
    total_work_minutes: int = 0
    
    # 欠勤関連
    absence_days: int = 0
    absence_rate: float = 0.0
    
    # 遅刻・早退
    tardiness_count: int = 0
    early_leave_count: int = 0
    tardiness_minutes: int = 0
    early_leave_minutes: int = 0
    
    # 残業時間
    scheduled_overtime_minutes: int = 0     # 所定残業
    legal_overtime_minutes: int = 0         # 法定残業
    late_night_work_minutes: int = 0        # 深夜労働
    holiday_work_minutes: int = 0           # 休日労働
    
    # 割増残業時間（支給対象）
    overtime_pay_minutes: int = 0
    late_night_pay_minutes: int = 0
    holiday_pay_minutes: int = 0
    
    # 休暇
    paid_leave_days: int = 0
    paid_leave_hours: float = 0.0
    remaining_paid_leave: int = 0
    special_leave_days: int = 0
    
    # 警告・注意事項
    warnings: List[str] = None
    violations: List[str] = None
    
    def __post_init__(self):
        """初期化後処理"""
        if self.warnings is None:
            self.warnings = []
        if self.violations is None:
            self.violations = []
```

#### 2.2 メイン計算クラススタブ (src/attendance_tool/calculation/calculator.py)

```python
"""勤怠集計計算機 - Red Phase実装"""

from typing import List, Optional, Dict, Any
from datetime import date
import pandas as pd

from ..validation.models import AttendanceRecord
from .summary import AttendanceSummary


class AttendanceCalculationError(Exception):
    """勤怠集計エラー"""
    pass


class AttendanceCalculator:
    """勤怠集計計算機
    
    Red Phase: メソッドシグネチャのみ定義、NotImplementedErrorを発生
    """
    
    def __init__(self, work_rules: Optional[Dict[str, Any]] = None):
        """初期化
        
        Args:
            work_rules: 就業規則設定（ConfigManagerから取得想定）
        """
        self.work_rules = work_rules or {}
    
    def calculate(self, records: List[AttendanceRecord], period: Optional[str] = None) -> AttendanceSummary:
        """勤怠集計メイン処理
        
        Args:
            records: 検証済み勤怠レコードリスト
            period: 集計期間（"2024-01"形式）
            
        Returns:
            AttendanceSummary: 集計結果
            
        Raises:
            AttendanceCalculationError: 集計処理エラー
        """
        # Red Phase: 実装なし
        raise NotImplementedError("calculate method not implemented yet")
    
    def calculate_batch(self, records_by_employee: Dict[str, List[AttendanceRecord]]) -> List[AttendanceSummary]:
        """複数社員の一括集計
        
        Args:
            records_by_employee: 社員別勤怠レコード辞書
            
        Returns:
            List[AttendanceSummary]: 社員別集計結果
        """
        # Red Phase: 実装なし
        raise NotImplementedError("calculate_batch method not implemented yet")
    
    def _calculate_attendance_days(self, records: List[AttendanceRecord]) -> int:
        """出勤日数計算"""
        raise NotImplementedError("_calculate_attendance_days method not implemented yet")
    
    def _calculate_overtime_minutes(self, records: List[AttendanceRecord]) -> Dict[str, int]:
        """残業時間計算"""
        raise NotImplementedError("_calculate_overtime_minutes method not implemented yet")
    
    def _calculate_tardiness_and_early_leave(self, records: List[AttendanceRecord]) -> Dict[str, int]:
        """遅刻・早退計算"""
        raise NotImplementedError("_calculate_tardiness_and_early_leave method not implemented yet")
```

#### 2.3 就業規則エンジンスタブ (src/attendance_tool/calculation/work_rules_engine.py)

```python
"""就業規則エンジン - Red Phase実装"""

from typing import Dict, Any, List
from datetime import date, time

from ..validation.models import AttendanceRecord


class WorkRulesEngine:
    """就業規則適用エンジン
    
    Red Phase: 各種規則チェックメソッドのスタブ
    """
    
    def __init__(self, work_rules: Dict[str, Any]):
        """初期化
        
        Args:
            work_rules: work_rules.yamlから読み込んだ設定
        """
        self.work_rules = work_rules
    
    def get_standard_work_minutes(self) -> int:
        """所定労働時間（分）を取得"""
        raise NotImplementedError("get_standard_work_minutes not implemented yet")
    
    def get_standard_start_time(self) -> time:
        """標準開始時刻を取得"""
        raise NotImplementedError("get_standard_start_time not implemented yet")
    
    def get_standard_end_time(self) -> time:
        """標準終了時刻を取得"""
        raise NotImplementedError("get_standard_end_time not implemented yet")
    
    def is_holiday(self, work_date: date) -> bool:
        """祝日判定"""
        raise NotImplementedError("is_holiday not implemented yet")
    
    def calculate_overtime_premium(self, overtime_minutes: int, work_date: date, 
                                 start_time: time, end_time: time) -> int:
        """残業割増計算"""
        raise NotImplementedError("calculate_overtime_premium not implemented yet")
    
    def check_violations(self, records: List[AttendanceRecord]) -> List[str]:
        """就業規則違反チェック"""
        raise NotImplementedError("check_violations not implemented yet")
```

### 3. 失敗テストの実装

#### 3.1 基本集計テスト (tests/unit/calculation/test_calculator.py)

```python
"""勤怠集計計算機テスト - Red Phase実装

このテストは失敗することを確認するためのもの
"""

import pytest
from datetime import date, time
from src.attendance_tool.calculation.calculator import AttendanceCalculator, AttendanceCalculationError
from src.attendance_tool.calculation.summary import AttendanceSummary
from src.attendance_tool.validation.models import AttendanceRecord


class TestAttendanceCalculatorBasic:
    """基本集計機能テスト"""
    
    def setup_method(self):
        """各テストメソッド前の準備"""
        self.calculator = AttendanceCalculator()
    
    def test_calculate_attendance_days_normal(self):
        """通常の出勤日数集計テスト - 現在は失敗する"""
        # Given: 20日間の勤怠データ（18日出勤、2日欠勤）
        records = self._create_test_records()
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def test_attendance_by_minimum_work_time(self):
        """最小勤務時間(4時間)による出勤判定テスト - 現在は失敗する"""
        # Given: work_statusが空だが4時間以上勤務
        records = [
            self._create_attendance_record(
                work_date=date(2024, 1, 1),
                start_time=time(9, 0),
                end_time=time(13, 30),
                break_minutes=30
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def test_calculate_absence_days_and_rate(self):
        """欠勤日数・欠勤率集計テスト - 現在は失敗する"""
        # Given: 欠勤データを含む勤怠レコード
        records = [
            self._create_attendance_record(
                work_date=date(2024, 1, 1),
                work_status="欠勤"
            ),
            self._create_attendance_record(
                work_date=date(2024, 1, 2),
                work_status="出勤",
                start_time=time(9, 0),
                end_time=time(18, 0)
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def test_calculate_tardiness(self):
        """遅刻回数・時間集計テスト - 現在は失敗する"""
        # Given: 遅刻データを含むレコード
        records = [
            self._create_attendance_record(
                work_date=date(2024, 1, 1),
                start_time=time(9, 5),  # 5分遅刻
                end_time=time(18, 0)
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def test_calculate_overtime(self):
        """残業時間計算テスト - 現在は失敗する"""
        # Given: 10時間勤務（2時間残業）
        records = [
            self._create_attendance_record(
                work_date=date(2024, 1, 1),
                start_time=time(9, 0),
                end_time=time(20, 0),  # 11時間後（休憩1時間込み）
                break_minutes=60
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def _create_test_records(self) -> list[AttendanceRecord]:
        """テスト用レコード作成"""
        records = []
        
        # 18日出勤データ
        for day in range(1, 19):
            record = self._create_attendance_record(
                work_date=date(2024, 1, day),
                work_status="出勤",
                start_time=time(9, 0),
                end_time=time(18, 0),
                break_minutes=60
            )
            records.append(record)
        
        # 2日欠勤データ
        for day in range(19, 21):
            record = self._create_attendance_record(
                work_date=date(2024, 1, day),
                work_status="欠勤"
            )
            records.append(record)
        
        return records
    
    def _create_attendance_record(self, work_date: date, work_status: str = None,
                                start_time: time = None, end_time: time = None,
                                break_minutes: int = None) -> AttendanceRecord:
        """テスト用AttendanceRecord作成"""
        return AttendanceRecord(
            employee_id="EMP001",
            employee_name="テスト太郎",
            work_date=work_date,
            work_status=work_status,
            start_time=start_time,
            end_time=end_time,
            break_minutes=break_minutes
        )


class TestAttendanceCalculatorEdgeCases:
    """境界値テスト"""
    
    def setup_method(self):
        """各テストメソッド前の準備"""
        self.calculator = AttendanceCalculator()
    
    def test_zero_work_time(self):
        """0分勤務処理テスト - 現在は失敗する"""
        # Given: 同一時刻の出退勤
        records = [
            AttendanceRecord(
                employee_id="EMP001",
                employee_name="テスト太郎",
                work_date=date(2024, 1, 1),
                start_time=time(9, 0),
                end_time=time(9, 0)
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def test_24_hour_work(self):
        """24時間勤務処理テスト - 現在は失敗する"""
        # Given: 24時間連続勤務（日跨ぎ）
        records = [
            AttendanceRecord(
                employee_id="EMP001",
                employee_name="テスト太郎",
                work_date=date(2024, 1, 1),
                start_time=time(9, 0),
                end_time=time(9, 0),  # 翌日同時刻
                break_minutes=60
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)


class TestAttendanceCalculatorBatch:
    """バッチ処理テスト"""
    
    def setup_method(self):
        """各テストメソッド前の準備"""
        self.calculator = AttendanceCalculator()
    
    def test_calculate_batch_multiple_employees(self):
        """複数社員一括処理テスト - 現在は失敗する"""
        # Given: 複数社員のデータ
        records_by_employee = {
            "EMP001": [
                AttendanceRecord(
                    employee_id="EMP001",
                    employee_name="社員１",
                    work_date=date(2024, 1, 1),
                    start_time=time(9, 0),
                    end_time=time(18, 0)
                )
            ],
            "EMP002": [
                AttendanceRecord(
                    employee_id="EMP002",
                    employee_name="社員２",
                    work_date=date(2024, 1, 1),
                    start_time=time(9, 0),
                    end_time=time(17, 0)
                )
            ]
        }
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summaries = self.calculator.calculate_batch(records_by_employee)
```

#### 3.2 就業規則エンジンテスト (tests/unit/calculation/test_work_rules_engine.py)

```python
"""就業規則エンジンテスト - Red Phase実装"""

import pytest
from datetime import date, time
from src.attendance_tool.calculation.work_rules_engine import WorkRulesEngine


class TestWorkRulesEngine:
    """就業規則エンジンテスト"""
    
    def setup_method(self):
        """各テストメソッド前の準備"""
        # テスト用就業規則設定
        self.work_rules = {
            "working_hours": {
                "standard_daily_minutes": 480,
                "standard_start_time": "09:00",
                "standard_end_time": "18:00"
            },
            "holidays": {
                "national_holidays": ["2024-01-01", "2024-01-08"]
            },
            "overtime": {
                "rates": {
                    "weekday_overtime": 1.25,
                    "legal_overtime": 1.25,
                    "late_night": 1.25,
                    "holiday_work": 1.35
                }
            }
        }
        self.engine = WorkRulesEngine(self.work_rules)
    
    def test_get_standard_work_minutes(self):
        """所定労働時間取得テスト - 現在は失敗する"""
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            minutes = self.engine.get_standard_work_minutes()
    
    def test_get_standard_times(self):
        """標準勤務時間取得テスト - 現在は失敗する"""
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            start_time = self.engine.get_standard_start_time()
        
        with pytest.raises(NotImplementedError):
            end_time = self.engine.get_standard_end_time()
    
    def test_is_holiday(self):
        """祝日判定テスト - 現在は失敗する"""
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            result = self.engine.is_holiday(date(2024, 1, 1))
    
    def test_calculate_overtime_premium(self):
        """残業割増計算テスト - 現在は失敗する"""
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            premium = self.engine.calculate_overtime_premium(
                120, date(2024, 1, 15), time(9, 0), time(20, 0)
            )
```

### 4. パッケージ初期化ファイル

#### 4.1 calculation/__init__.py

```python
"""勤怠集計機能パッケージ - Red Phase"""

from .calculator import AttendanceCalculator, AttendanceCalculationError
from .summary import AttendanceSummary
from .work_rules_engine import WorkRulesEngine

__all__ = [
    'AttendanceCalculator',
    'AttendanceCalculationError', 
    'AttendanceSummary',
    'WorkRulesEngine'
]
```

#### 4.2 tests/unit/calculation/__init__.py

```python
"""勤怠集計機能テストパッケージ"""
# 空のファイル
```

### 5. テスト実行とRed確認

```bash
# 新規作成したテストを実行（すべて失敗することを確認）
cd /home/kuma/dev/attendance-tool

# 計算機能テストを実行
pytest tests/unit/calculation/ -v

# 期待される結果：
# - すべてのテストがNotImplementedErrorで失敗
# - テストの構造とセットアップが正常に動作
# - エラーメッセージが適切に表示される
```

### 6. Red Phase確認項目

- [ ] `AttendanceCalculator.calculate()` が `NotImplementedError` を発生させる
- [ ] `AttendanceCalculator.calculate_batch()` が `NotImplementedError` を発生させる
- [ ] `WorkRulesEngine` の各メソッドが `NotImplementedError` を発生させる
- [ ] テストが適切にセットアップされ、例外が期待通りキャッチされる
- [ ] テストカバレッジツールが新しいクラスを認識する

### 7. 次のGreen Phaseへの準備

Red Phaseでの確認が完了したら、次のGreen Phaseで：

1. `AttendanceCalculator.calculate()` の最小実装
2. 基本的な出勤日数計算の実装
3. `AttendanceSummary` の基本データ設定
4. 1つのテストが通るまでの最小限実装

Red Phaseはここで完了となります。実装コードは意図的に未完成のままで、テストが確実に失敗することを確認することが目的です。