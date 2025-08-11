"""標準テストデータ - 社員別集計用"""

from datetime import date

from attendance_tool.calculation.department_summary import DepartmentSummary
from attendance_tool.calculation.summary import AttendanceSummary

STANDARD_EMPLOYEE_DATA = [
    AttendanceSummary(
        employee_id="EMP001",
        employee_name="田中太郎",
        department="開発部",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        total_days=31,
        business_days=22,
        attendance_days=20,
        attendance_rate=90.9,
        total_work_minutes=9600,  # 160時間
        scheduled_overtime_minutes=1200,  # 20時間
        tardiness_count=2,
        early_leave_count=1,
        paid_leave_days=1,
        warnings=["遅刻が多いです"],
        violations=[],
    ),
    AttendanceSummary(
        employee_id="EMP002",
        employee_name="佐藤花子",
        department="営業部",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        total_days=31,
        business_days=22,
        attendance_days=22,
        attendance_rate=100.0,
        total_work_minutes=10560,  # 176時間
        scheduled_overtime_minutes=2160,  # 36時間
        tardiness_count=0,
        early_leave_count=0,
        paid_leave_days=0,
        warnings=[],
        violations=["月36時間超過"],
    ),
    AttendanceSummary(
        employee_id="EMP003",
        employee_name="高橋次郎",
        department="総務部",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        total_days=31,
        business_days=22,
        attendance_days=19,
        attendance_rate=86.4,
        total_work_minutes=9120,  # 152時間
        scheduled_overtime_minutes=720,  # 12時間
        tardiness_count=1,
        early_leave_count=0,
        paid_leave_days=2,
        warnings=[],
        violations=[],
    ),
]

STANDARD_DEPARTMENT_DATA = [
    DepartmentSummary(
        department_code="DEV",
        department_name="開発部",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        employee_count=5,
        total_work_minutes=48000,
        total_overtime_minutes=6000,
        attendance_rate=92.0,
        average_work_minutes=9600,
        violation_count=1,
        compliance_score=85.0,
    ),
    DepartmentSummary(
        department_code="SALES",
        department_name="営業部",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        employee_count=3,
        total_work_minutes=31680,
        total_overtime_minutes=6480,
        attendance_rate=98.5,
        average_work_minutes=10560,
        violation_count=2,
        compliance_score=75.0,
    ),
]

# エッジケース用テストデータ
EDGE_CASE_DATA = [
    # 空の名前
    AttendanceSummary(
        employee_id="EDGE001",
        employee_name="",
        department="",
        period_start=date(2024, 2, 1),
        period_end=date(2024, 2, 29),  # うるう年
        total_days=29,
        business_days=21,
        attendance_days=0,
        attendance_rate=0.0,
        total_work_minutes=0,
        scheduled_overtime_minutes=0,
        tardiness_count=0,
        early_leave_count=0,
        paid_leave_days=0,
    ),
    # 特殊文字を含む名前
    AttendanceSummary(
        employee_id="EDGE002",
        employee_name='田中,"太郎"\n課長',
        department="開発\r\n部",
        period_start=date(2024, 1, 1),
        period_end=date(2024, 1, 31),
        total_days=31,
        business_days=22,
        attendance_days=22,
        attendance_rate=100.0,
        total_work_minutes=10560,
        scheduled_overtime_minutes=2160,
        tardiness_count=0,
        early_leave_count=0,
        paid_leave_days=0,
    ),
]
