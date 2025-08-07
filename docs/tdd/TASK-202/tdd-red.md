# TASK-202: 就業規則エンジン - Red Phase実装

## Red Phase概要

TDDのRed Phaseとして、就業規則違反チェック機能の**失敗するテスト**を実装します。
この段階では、新しいクラスと拡張メソッドのスタブを作成し、テストが確実に失敗することを確認します。

## 実装内容

### 1. 違反情報データクラスの作成

#### 1.1 WorkRuleViolation データクラス (src/attendance_tool/calculation/violations.py)

```python
"""就業規則違反情報モデル - Red Phase実装"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Optional


class ViolationLevel(Enum):
    """違反レベル定義"""
    INFO = "info"           # 情報・推奨事項
    WARNING = "warning"     # 警告・注意事項  
    VIOLATION = "violation" # 違反・即座の対応が必要
    CRITICAL = "critical"   # 重大違反・法的リスク


@dataclass
class WorkRuleViolation:
    """就業規則違反情報
    
    Red Phase: 基本的なデータ構造のみ定義
    """
    
    violation_type: str          # 違反種別
    level: ViolationLevel        # 違反レベル
    message: str                 # 違反メッセージ
    affected_date: date          # 対象日付
    actual_value: Any            # 実際の値
    threshold_value: Any         # 閾値
    suggestion: str              # 改善提案
    legal_reference: str         # 法的根拠
    
    # メタデータ
    detected_at: Optional[datetime] = None
    employee_id: Optional[str] = None
    rule_id: Optional[str] = None
    
    def __post_init__(self):
        """初期化後処理"""
        if self.detected_at is None:
            self.detected_at = datetime.now()


@dataclass
class ComplianceReport:
    """法令遵守レポート
    
    Red Phase: 基本構造のみ定義
    """
    
    employee_id: str
    period_start: date
    period_end: date
    total_violations: int
    critical_violations: int
    warnings: int
    info_items: int
    
    # 違反詳細
    violations: list[WorkRuleViolation]
    
    # 法令遵守スコア（0-100）
    compliance_score: float = 0.0
    
    def __post_init__(self):
        """初期化後処理 - Red Phase: 未実装"""
        # 実装は Green Phase で行う
        pass
```

### 2. WorkRulesEngine拡張メソッドスタブ

#### 2.1 違反チェックメソッド追加 (src/attendance_tool/calculation/work_rules_engine.py)

```python
# 既存のWorkRulesEngineクラスに以下メソッドを追加

def check_daily_work_hour_violations(self, record: 'AttendanceRecord') -> List['WorkRuleViolation']:
    """日次労働時間違反チェック - Red Phase実装"""
    # Red Phase: NotImplementedError を発生
    raise NotImplementedError("check_daily_work_hour_violations not implemented yet")

def check_weekly_work_hour_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """週次労働時間違反チェック - Red Phase実装"""
    raise NotImplementedError("check_weekly_work_hour_violations not implemented yet")

def check_monthly_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """月次違反チェック（残業時間上限等）- Red Phase実装"""
    raise NotImplementedError("check_monthly_violations not implemented yet")

def check_break_time_violations(self, record: 'AttendanceRecord') -> List['WorkRuleViolation']:
    """休憩時間違反チェック - Red Phase実装"""
    raise NotImplementedError("check_break_time_violations not implemented yet")

def check_consecutive_work_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """連続勤務日数違反チェック - Red Phase実装"""
    raise NotImplementedError("check_consecutive_work_violations not implemented yet")

def check_night_work_violations(self, record: 'AttendanceRecord') -> List['WorkRuleViolation']:
    """深夜労働違反チェック - Red Phase実装"""
    raise NotImplementedError("check_night_work_violations not implemented yet")

def check_holiday_work_violations(self, record: 'AttendanceRecord') -> List['WorkRuleViolation']:
    """休日労働違反チェック - Red Phase実装"""
    raise NotImplementedError("check_holiday_work_violations not implemented yet")

def check_all_violations(self, records: List['AttendanceRecord']) -> List['WorkRuleViolation']:
    """全違反チェック統合メソッド - Red Phase実装"""
    raise NotImplementedError("check_all_violations not implemented yet")

def generate_compliance_report(self, records: List['AttendanceRecord']) -> 'ComplianceReport':
    """法令遵守レポート生成 - Red Phase実装"""
    raise NotImplementedError("generate_compliance_report not implemented yet")

# 設定値取得メソッドの追加（Red Phase: デフォルト値返却）

def get_daily_legal_minutes(self) -> int:
    """日次法定労働時間（分）を取得 - Red Phase実装"""
    return self.work_rules.get("work_hour_limits", {}).get("daily_legal_minutes", 480)

def get_daily_warning_minutes(self) -> int:
    """日次警告労働時間（分）を取得 - Red Phase実装"""
    return self.work_rules.get("work_hour_limits", {}).get("daily_warning_minutes", 720)

def get_required_break_minutes(self, work_minutes: int) -> int:
    """必要休憩時間（分）を取得 - Red Phase実装"""
    # 簡単な実装：6時間超で45分、8時間超で60分
    if work_minutes > 8 * 60:  # 8時間超
        return 60
    elif work_minutes > 6 * 60:  # 6時間超
        return 45
    else:
        return 0

def get_consecutive_work_warning_days(self) -> int:
    """連続勤務警告日数を取得 - Red Phase実装"""
    return self.work_rules.get("consecutive_work_limits", {}).get("warning_days", 6)
```

### 3. AttendanceCalculator統合メソッドスタブ

#### 3.1 違反チェック統合 (src/attendance_tool/calculation/calculator.py)

```python
# AttendanceCalculatorクラスに以下メソッドを追加

def calculate_with_violations(self, records: List[AttendanceRecord]) -> Tuple[AttendanceSummary, List[WorkRuleViolation]]:
    """集計結果と違反情報を同時生成 - Red Phase実装"""
    # Red Phase: NotImplementedError を発生
    raise NotImplementedError("calculate_with_violations not implemented yet")

def _integrate_violation_warnings(self, summary: AttendanceSummary, violations: List[WorkRuleViolation]) -> AttendanceSummary:
    """違反情報をサマリーに統合 - Red Phase実装"""
    raise NotImplementedError("_integrate_violation_warnings not implemented yet")
```

### 4. 失敗テストの実装

#### 4.1 WorkRuleViolationテスト (tests/unit/calculation/test_work_rule_violation.py)

```python
"""就業規則違反情報テスト - Red Phase実装

このテストは失敗することを確認するためのもの
"""

import pytest
from datetime import date, datetime
from src.attendance_tool.calculation.violations import (
    WorkRuleViolation, ViolationLevel, ComplianceReport
)


class TestWorkRuleViolation:
    """WorkRuleViolation データクラステスト"""
    
    def test_violation_creation():
        """WorkRuleViolation作成テスト - 現在は成功する"""
        # Given: 違反情報の基本データ
        violation = WorkRuleViolation(
            violation_type="daily_overtime",
            level=ViolationLevel.WARNING,
            message="法定労働時間を超過しています",
            affected_date=date(2024, 1, 15),
            actual_value=600,  # 10時間
            threshold_value=480,  # 8時間
            suggestion="労働時間の見直しを検討してください",
            legal_reference="労働基準法第32条"
        )
        
        # Then: オブジェクトが正常に作成される
        assert violation.violation_type == "daily_overtime"
        assert violation.level == ViolationLevel.WARNING
        assert violation.actual_value == 600
        assert violation.detected_at is not None


class TestComplianceReport:
    """ComplianceReport データクラステスト"""
    
    def test_compliance_report_creation():
        """ComplianceReport作成テスト - 現在は成功する"""
        # Given: コンプライアンスレポートの基本データ
        violations = [
            WorkRuleViolation(
                violation_type="daily_overtime",
                level=ViolationLevel.WARNING,
                message="Test violation",
                affected_date=date(2024, 1, 15),
                actual_value=600,
                threshold_value=480,
                suggestion="Test suggestion",
                legal_reference="Test reference"
            )
        ]
        
        report = ComplianceReport(
            employee_id="EMP001",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            total_violations=1,
            critical_violations=0,
            warnings=1,
            info_items=0,
            violations=violations
        )
        
        # Then: レポートが正常に作成される
        assert report.employee_id == "EMP001"
        assert report.total_violations == 1
        assert len(report.violations) == 1
```

#### 4.2 WorkRulesEngine拡張テスト (tests/unit/calculation/test_work_rules_engine_violations.py)

```python
"""WorkRulesEngine違反チェック機能テスト - Red Phase実装"""

import pytest
from datetime import date, time
from src.attendance_tool.calculation.work_rules_engine import WorkRulesEngine
from src.attendance_tool.calculation.violations import WorkRuleViolation, ViolationLevel


class TestWorkRulesEngineViolations:
    """WorkRulesEngine違反チェック機能テスト"""
    
    def setup_method(self):
        """各テストメソッド前の準備"""
        self.work_rules = {
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
        self.engine = WorkRulesEngine(self.work_rules)
    
    def test_check_daily_work_hour_violations_not_implemented():
        """日次労働時間違反チェック - 現在は失敗する"""
        # Given: テスト用勤怠レコード
        mock_record = self._create_mock_record(work_hours=10)
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            violations = self.engine.check_daily_work_hour_violations(mock_record)
    
    def test_check_weekly_work_hour_violations_not_implemented():
        """週次労働時間違反チェック - 現在は失敗する"""
        # Given: テスト用週次レコード
        mock_records = [self._create_mock_record(work_hours=10) for _ in range(5)]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            violations = self.engine.check_weekly_work_hour_violations(mock_records)
    
    def test_check_monthly_violations_not_implemented():
        """月次違反チェック - 現在は失敗する"""
        # Given: テスト用月次レコード
        mock_records = [self._create_mock_record(work_hours=10) for _ in range(20)]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            violations = self.engine.check_monthly_violations(mock_records)
    
    def test_check_break_time_violations_not_implemented():
        """休憩時間違反チェック - 現在は失敗する"""
        # Given: 休憩時間不足レコード
        mock_record = self._create_mock_record(work_hours=8, break_minutes=30)
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            violations = self.engine.check_break_time_violations(mock_record)
    
    def test_check_consecutive_work_violations_not_implemented():
        """連続勤務違反チェック - 現在は失敗する"""
        # Given: 連続勤務レコード
        mock_records = [self._create_mock_record(work_hours=8) for _ in range(8)]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            violations = self.engine.check_consecutive_work_violations(mock_records)
    
    def test_check_night_work_violations_not_implemented():
        """深夜労働違反チェック - 現在は失敗する"""
        # Given: 深夜勤務レコード
        mock_record = self._create_mock_record_with_times(time(22, 0), time(2, 0))
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            violations = self.engine.check_night_work_violations(mock_record)
    
    def test_check_holiday_work_violations_not_implemented():
        """休日労働違反チェック - 現在は失敗する"""
        # Given: 休日勤務レコード（元日）
        mock_record = self._create_mock_record_on_date(date(2024, 1, 1))
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            violations = self.engine.check_holiday_work_violations(mock_record)
    
    def test_check_all_violations_not_implemented():
        """全違反チェック統合 - 現在は失敗する"""
        # Given: 複数の違反を含むレコード
        mock_records = [
            self._create_mock_record(work_hours=12),  # 過労働
            self._create_mock_record(work_hours=8, break_minutes=30)  # 休憩不足
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            violations = self.engine.check_all_violations(mock_records)
    
    def test_generate_compliance_report_not_implemented():
        """法令遵守レポート生成 - 現在は失敗する"""
        # Given: 月次勤怠レコード
        mock_records = [self._create_mock_record(work_hours=9) for _ in range(20)]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            report = self.engine.generate_compliance_report(mock_records)
    
    def test_new_configuration_methods():
        """新しい設定取得メソッド - 現在は成功する"""
        # When: 設定値取得
        daily_legal = self.engine.get_daily_legal_minutes()
        daily_warning = self.engine.get_daily_warning_minutes()
        required_break_6h = self.engine.get_required_break_minutes(7 * 60)
        required_break_8h = self.engine.get_required_break_minutes(9 * 60)
        consecutive_warning = self.engine.get_consecutive_work_warning_days()
        
        # Then: 設定値が正しく取得される
        assert daily_legal == 480
        assert daily_warning == 720
        assert required_break_6h == 45
        assert required_break_8h == 60
        assert consecutive_warning == 6
    
    def _create_mock_record(self, work_hours=8, break_minutes=60):
        """モック勤怠レコード作成"""
        class MockRecord:
            def __init__(self):
                self.employee_id = "EMP001"
                self.work_date = date(2024, 1, 15)
                self.start_time = time(9, 0)
                self.end_time = time(9 + work_hours, 0)
                self.break_minutes = break_minutes
                self.work_status = "出勤"
            
            def get_work_duration_minutes(self):
                return work_hours * 60
        
        return MockRecord()
    
    def _create_mock_record_with_times(self, start_time, end_time):
        """時刻指定モックレコード作成"""
        class MockRecord:
            def __init__(self):
                self.employee_id = "EMP001"
                self.work_date = date(2024, 1, 15)
                self.start_time = start_time
                self.end_time = end_time
                self.break_minutes = 0
                self.work_status = "出勤"
            
            def get_work_duration_minutes(self):
                # 簡単な計算（日跨ぎ考慮）
                if start_time <= end_time:
                    duration_hours = end_time.hour - start_time.hour
                else:
                    duration_hours = (24 - start_time.hour) + end_time.hour
                return duration_hours * 60
        
        return MockRecord()
    
    def _create_mock_record_on_date(self, work_date):
        """日付指定モックレコード作成"""
        class MockRecord:
            def __init__(self):
                self.employee_id = "EMP001"
                self.work_date = work_date
                self.start_time = time(9, 0)
                self.end_time = time(18, 0)
                self.break_minutes = 60
                self.work_status = "出勤"
            
            def get_work_duration_minutes(self):
                return 8 * 60
        
        return MockRecord()
```

#### 4.3 AttendanceCalculator統合テスト (tests/unit/calculation/test_calculator_violations.py)

```python
"""AttendanceCalculator違反チェック統合テスト - Red Phase実装"""

import pytest
from datetime import date, time
from src.attendance_tool.calculation.calculator import AttendanceCalculator


class TestAttendanceCalculatorViolations:
    """AttendanceCalculator違反チェック統合テスト"""
    
    def setup_method(self):
        """各テストメソッド前の準備"""
        self.work_rules = {
            "work_hour_limits": {
                "daily_legal_minutes": 480,
                "monthly_overtime_limit": 2700
            }
        }
        self.calculator = AttendanceCalculator(self.work_rules)
    
    def test_calculate_with_violations_not_implemented():
        """違反チェック付き集計 - 現在は失敗する"""
        # Given: 違反を含む勤怠データ
        mock_records = [self._create_mock_record(work_hours=12)]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary, violations = self.calculator.calculate_with_violations(mock_records)
    
    def test_integrate_violation_warnings_not_implemented():
        """違反情報統合 - 現在は失敗する"""
        # Given: サマリーと違反情報
        mock_summary = self._create_mock_summary()
        mock_violations = [self._create_mock_violation()]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            updated_summary = self.calculator._integrate_violation_warnings(
                mock_summary, mock_violations
            )
    
    def test_backward_compatibility():
        """既存機能の後方互換性 - 現在は成功する"""
        # Given: 通常の勤怠データ
        mock_records = [self._create_mock_record(work_hours=8)]
        
        # When: 既存のcalculateメソッド使用
        summary = self.calculator.calculate(mock_records)
        
        # Then: 既存機能は正常動作
        assert summary.employee_id == "EMP001"
        assert summary.attendance_days > 0
    
    def _create_mock_record(self, work_hours=8):
        """モックレコード作成"""
        class MockRecord:
            def __init__(self):
                self.employee_id = "EMP001"
                self.employee_name = "テスト社員"
                self.work_date = date(2024, 1, 15)
                self.start_time = time(9, 0)
                self.end_time = time(9 + work_hours, 0)
                self.break_minutes = 60
                self.work_status = "出勤"
            
            def get_work_duration_minutes(self):
                return work_hours * 60
        
        return MockRecord()
    
    def _create_mock_summary(self):
        """モックサマリー作成"""
        from src.attendance_tool.calculation.summary import AttendanceSummary
        return AttendanceSummary(
            employee_id="EMP001",
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            total_days=31,
            business_days=20,
            attendance_days=20
        )
    
    def _create_mock_violation(self):
        """モック違反情報作成"""
        from src.attendance_tool.calculation.violations import (
            WorkRuleViolation, ViolationLevel
        )
        return WorkRuleViolation(
            violation_type="daily_overtime",
            level=ViolationLevel.WARNING,
            message="Test violation",
            affected_date=date(2024, 1, 15),
            actual_value=720,
            threshold_value=480,
            suggestion="Test suggestion",
            legal_reference="Test reference"
        )
```

### 5. パッケージ初期化ファイル更新

#### 5.1 violations.py をパッケージに追加

```python
# src/attendance_tool/calculation/__init__.py に追加

from .violations import WorkRuleViolation, ViolationLevel, ComplianceReport

__all__ = [
    'AttendanceCalculator',
    'AttendanceCalculationError', 
    'AttendanceSummary',
    'WorkRulesEngine',
    'WorkRuleViolation',      # 追加
    'ViolationLevel',         # 追加
    'ComplianceReport'        # 追加
]
```

### 6. Red Phase実装手順

#### Step 1: 違反情報クラス作成
```bash
# 新しいファイル作成
touch src/attendance_tool/calculation/violations.py

# WorkRuleViolation, ViolationLevel, ComplianceReport を実装
```

#### Step 2: WorkRulesEngine拡張
```bash
# 既存ファイルに新メソッド追加
# 全てNotImplementedError を発生させる
```

#### Step 3: AttendanceCalculator拡張  
```bash
# 既存ファイルに統合メソッド追加
# 全てNotImplementedError を発生させる
```

#### Step 4: 失敗テスト作成
```bash
# 新しいテストファイル作成
touch tests/unit/calculation/test_work_rule_violation.py
touch tests/unit/calculation/test_work_rules_engine_violations.py
touch tests/unit/calculation/test_calculator_violations.py
```

### 7. Red Phase確認実行

```bash
# 新しい違反情報クラスのテスト（成功する）
python3 -c "
import sys
sys.path.append('src')
from attendance_tool.calculation.violations import WorkRuleViolation, ViolationLevel
print('✅ WorkRuleViolation クラス作成成功')
"

# 拡張メソッドの失敗確認（NotImplementedError）
python3 -c "
import sys
sys.path.append('src')
from attendance_tool.calculation.work_rules_engine import WorkRulesEngine
try:
    engine = WorkRulesEngine({})
    engine.check_daily_work_hour_violations(None)
    print('❌ エラーが発生していません')
except NotImplementedError as e:
    print('✅ 期待通りNotImplementedError:', str(e))
"

# 統合メソッドの失敗確認（NotImplementedError）
python3 -c "
import sys
sys.path.append('src')
from attendance_tool.calculation.calculator import AttendanceCalculator
try:
    calc = AttendanceCalculator({})
    calc.calculate_with_violations([])
    print('❌ エラーが発生していません')
except NotImplementedError as e:
    print('✅ 期待通りNotImplementedError:', str(e))
"
```

### 8. Red Phase完了基準

- [x] WorkRuleViolation データクラスが作成される
- [x] ViolationLevel Enum が定義される  
- [x] ComplianceReport データクラスが作成される
- [ ] WorkRulesEngine の全拡張メソッドが NotImplementedError を発生させる
- [ ] AttendanceCalculator の統合メソッドが NotImplementedError を発生させる
- [ ] テストが適切にセットアップされ、例外が期待通りキャッチされる
- [ ] 既存機能への影響がない（後方互換性維持）

Red Phaseでは、新機能のスケルトンを作成し、テストが確実に失敗することを確認することが目的です。
実際の違反検出ロジックは Green Phase で実装します。