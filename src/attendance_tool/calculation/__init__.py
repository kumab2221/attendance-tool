"""勤怠集計機能パッケージ - Red Phase"""

from .calculator import AttendanceCalculationError, AttendanceCalculator
from .department import Department
from .department_aggregator import DepartmentAggregator
from .department_summary import (
    DepartmentComparison,
    DepartmentReport,
    DepartmentSummary,
)
from .summary import AttendanceSummary
from .violations import ComplianceReport, ViolationLevel, WorkRuleViolation
from .work_rules_engine import WorkRulesEngine

__all__ = [
    "AttendanceCalculator",
    "AttendanceCalculationError",
    "AttendanceSummary",
    "WorkRulesEngine",
    "WorkRuleViolation",
    "ViolationLevel",
    "ComplianceReport",
    "Department",
    "DepartmentAggregator",
    "DepartmentSummary",
    "DepartmentComparison",
    "DepartmentReport",
]
