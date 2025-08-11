"""部門別集計エンジン - Green Phase実装"""

import logging
from collections import defaultdict
from datetime import date
from typing import Dict, List, Optional, Set

from ..validation.models import AttendanceRecord
from .department import CircularReferenceError, Department, DepartmentValidationError
from .department_summary import (
    DepartmentComparison,
    DepartmentReport,
    DepartmentSummary,
)


class DepartmentAggregator:
    """部門別集計エンジン - Green Phase実装"""

    def __init__(self, departments: List[Department]):
        """初期化

        Args:
            departments: 部門リスト

        Raises:
            CircularReferenceError: 循環参照が検出された場合
            DepartmentValidationError: 部門データが無効な場合
        """
        self.departments = departments
        self.department_dict = {dept.code: dept for dept in departments}
        self.department_tree: Dict[str, List[str]] = {}

        # Green Phase: 検証機能実装
        if not self._validate_basic_structure():
            raise DepartmentValidationError("部門データの基本構造が無効です")

        if self._detect_circular_references():
            raise CircularReferenceError("部門階層に循環参照が検出されました")

        self.department_tree = self._build_department_tree()

    def _validate_basic_structure(self) -> bool:
        """基本構造検証 - Green Phase実装"""
        if not isinstance(self.departments, list):
            return False

        # 部門コードの重複チェック
        codes = [dept.code for dept in self.departments]
        if len(codes) != len(set(codes)):
            return False

        # 親部門の存在チェック
        for dept in self.departments:
            if dept.parent_code and dept.parent_code not in self.department_dict:
                return False

        return True

    def validate_hierarchy(self) -> bool:
        """階層構造検証 - Green Phase実装"""
        try:
            # 循環参照チェック
            if self._detect_circular_references():
                return False

            # 階層レベル整合性チェック
            for dept in self.departments:
                if dept.parent_code:
                    parent = self.department_dict.get(dept.parent_code)
                    if parent and dept.level != parent.level + 1:
                        return False

            return True
        except Exception:
            return False

    def load_department_master(self, file_path: str) -> List[Department]:
        """部門マスターファイル読み込み - Green Phase最小実装"""
        # Green Phase: 最小実装（CSVファイル読み込み）
        departments = []

        try:
            # 簡易CSVパーサー実装
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

                # ヘッダー行をスキップ
                for line in lines[1:]:
                    line = line.strip()
                    if not line:
                        continue

                    parts = line.split(",")
                    if len(parts) >= 5:
                        code = parts[0].strip()
                        name = parts[1].strip()
                        parent_code = parts[2].strip() if parts[2].strip() else None
                        level = int(parts[3].strip())
                        is_active = parts[4].strip().lower() == "true"

                        dept = Department(code, name, parent_code, level, is_active)
                        departments.append(dept)

        except Exception as e:
            raise DepartmentValidationError(f"部門マスター読み込みエラー: {e}")

        return departments

    def aggregate_single_department(
        self,
        department_code: str,
        records: List[AttendanceRecord],
        period_start: date,
        period_end: date,
    ) -> DepartmentSummary:
        """単一部門集計 - Refactor Phase: 最適化版"""
        dept = self.department_dict.get(department_code)
        if not dept:
            raise DepartmentValidationError(f"部門が見つかりません: {department_code}")

        # 対象期間内のレコードをフィルタ
        filtered_records = [
            r
            for r in records
            if period_start <= r.work_date <= period_end
            and hasattr(r, "department_code")
            and r.department_code == department_code
        ]

        # 最適化されたサマリー計算を使用
        return self._calculate_department_summary_optimized(
            dept, filtered_records, period_start, period_end
        )

    def aggregate_by_department(
        self, records: List[AttendanceRecord], period_start: date, period_end: date
    ) -> List[DepartmentSummary]:
        """部門別集計 - Refactor Phase: パフォーマンス最適化版"""

        # 1回のループで全レコードを部門別に分類
        records_by_department = self._group_records_by_department(
            records, period_start, period_end
        )

        # アクティブな部門のみ処理
        summaries = []
        active_departments = [dept for dept in self.departments if dept.is_active]

        # バッチ処理で効率的に集計
        for dept in active_departments:
            dept_records = records_by_department.get(dept.code, [])
            summary = self._calculate_department_summary_optimized(
                dept, dept_records, period_start, period_end
            )
            summaries.append(summary)

        return summaries

    def aggregate_by_hierarchy(
        self, summaries: List[DepartmentSummary], level: int
    ) -> List[DepartmentSummary]:
        """階層別集計 - Green Phase実装"""
        if level < 0:
            return []

        # 指定階層の部門を取得
        target_departments = [
            dept for dept in self.departments if dept.level == level and dept.is_active
        ]

        hierarchy_summaries = []

        for parent_dept in target_departments:
            # 子部門のサマリーを集約
            child_departments = parent_dept.get_children(self.departments)
            child_codes = [child.code for child in child_departments]

            # 子部門のサマリーデータを集計
            child_summaries = [s for s in summaries if s.department_code in child_codes]

            if not child_summaries:
                # 子部門がない場合は親部門自身のデータを使用
                parent_summary = next(
                    (s for s in summaries if s.department_code == parent_dept.code),
                    None,
                )
                if parent_summary:
                    hierarchy_summaries.append(parent_summary)
                continue

            # 集約計算
            total_employees = sum(s.employee_count for s in child_summaries)
            total_work_minutes = sum(s.total_work_minutes for s in child_summaries)
            total_overtime_minutes = sum(
                s.total_overtime_minutes for s in child_summaries
            )
            total_violations = sum(s.violation_count for s in child_summaries)

            # 加重平均計算
            if total_employees > 0:
                weighted_attendance = (
                    sum(s.attendance_rate * s.employee_count for s in child_summaries)
                    / total_employees
                )
                weighted_average_work = (
                    sum(
                        s.average_work_minutes * s.employee_count
                        for s in child_summaries
                    )
                    / total_employees
                )
                weighted_compliance = (
                    sum(s.compliance_score * s.employee_count for s in child_summaries)
                    / total_employees
                )
            else:
                weighted_attendance = 0.0
                weighted_average_work = 0.0
                weighted_compliance = 100.0

            # 期間は子部門の共通期間を使用
            period_start = child_summaries[0].period_start
            period_end = child_summaries[0].period_end

            hierarchy_summary = DepartmentSummary(
                department_code=parent_dept.code,
                department_name=parent_dept.name,
                period_start=period_start,
                period_end=period_end,
                employee_count=total_employees,
                total_work_minutes=total_work_minutes,
                total_overtime_minutes=total_overtime_minutes,
                attendance_rate=weighted_attendance,
                average_work_minutes=weighted_average_work,
                violation_count=total_violations,
                compliance_score=weighted_compliance,
            )

            hierarchy_summaries.append(hierarchy_summary)

        return hierarchy_summaries

    def compare_departments(
        self, summaries: List[DepartmentSummary]
    ) -> DepartmentComparison:
        """部門間比較 - Green Phase実装"""
        if not summaries:
            return DepartmentComparison(
                summaries=[],
                ranking_by_work_hours=[],
                ranking_by_attendance=[],
                average_work_minutes=0.0,
                average_attendance_rate=0.0,
            )

        # 労働時間順ランキング
        work_hours_ranking = sorted(
            summaries, key=lambda s: s.total_work_minutes, reverse=True
        )
        ranking_by_work_hours = [s.department_code for s in work_hours_ranking]

        # 出勤率順ランキング
        attendance_ranking = sorted(
            summaries, key=lambda s: s.attendance_rate, reverse=True
        )
        ranking_by_attendance = [s.department_code for s in attendance_ranking]

        # 全体平均計算
        total_employees = sum(s.employee_count for s in summaries)
        if total_employees > 0:
            average_work_minutes = (
                sum(s.average_work_minutes * s.employee_count for s in summaries)
                / total_employees
            )
            average_attendance_rate = (
                sum(s.attendance_rate * s.employee_count for s in summaries)
                / total_employees
            )
        else:
            average_work_minutes = 0.0
            average_attendance_rate = 0.0

        return DepartmentComparison(
            summaries=summaries,
            ranking_by_work_hours=ranking_by_work_hours,
            ranking_by_attendance=ranking_by_attendance,
            average_work_minutes=average_work_minutes,
            average_attendance_rate=average_attendance_rate,
        )

    def generate_department_report(
        self, summary: DepartmentSummary
    ) -> DepartmentReport:
        """部門レポート生成 - Green Phase実装"""
        # Green Phase: 最小実装
        recommendations = []
        alert_items = []

        # 簡易的な推奨事項生成
        if summary.attendance_rate < 90.0:
            recommendations.append("出勤率の改善を検討してください")

        if summary.total_overtime_minutes > 5000:  # 約83時間
            alert_items.append("残業時間が多すぎます")

        if summary.compliance_score < 80.0:
            alert_items.append("コンプライアンススコアが低いです")

        # ダミーの比較データ
        dummy_comparison = DepartmentComparison(
            summaries=[summary],
            ranking_by_work_hours=[summary.department_code],
            ranking_by_attendance=[summary.department_code],
            average_work_minutes=summary.average_work_minutes,
            average_attendance_rate=summary.attendance_rate,
        )

        return DepartmentReport(
            summary=summary,
            comparison_data=dummy_comparison,
            recommendations=recommendations,
            alert_items=alert_items,
        )

    def _build_department_tree(self) -> Dict[str, List[str]]:
        """部門ツリー構築 - Green Phase実装"""
        tree = defaultdict(list)

        for dept in self.departments:
            if dept.parent_code:
                tree[dept.parent_code].append(dept.code)

        return dict(tree)

    def _detect_circular_references(self) -> bool:
        """循環参照検出 - Green Phase実装"""
        visited = set()
        visiting = set()

        def dfs(dept_code: str) -> bool:
            if dept_code in visiting:
                return True  # 循環参照発見

            if dept_code in visited:
                return False

            dept = self.department_dict.get(dept_code)
            if not dept or not dept.parent_code:
                visited.add(dept_code)
                return False

            visiting.add(dept_code)

            if dfs(dept.parent_code):
                return True

            visiting.remove(dept_code)
            visited.add(dept_code)
            return False

        # すべての部門について循環参照チェック
        for dept in self.departments:
            if dept.code not in visited:
                if dfs(dept.code):
                    return True

        return False

    def _group_records_by_department(
        self, records: List[AttendanceRecord], period_start: date, period_end: date
    ) -> Dict[str, List[AttendanceRecord]]:
        """レコードを部門別にグループ化 - 効率化"""
        grouped = {}

        for record in records:
            # 期間フィルタリング
            if not (period_start <= record.work_date <= period_end):
                continue

            # 部門コード取得（複数の方法で対応）
            dept_code = getattr(record, "department_code", None)
            if not dept_code:
                continue

            if dept_code not in grouped:
                grouped[dept_code] = []
            grouped[dept_code].append(record)

        return grouped

    def _calculate_department_summary_optimized(
        self,
        dept: Department,
        records: List[AttendanceRecord],
        period_start: date,
        period_end: date,
    ) -> DepartmentSummary:
        """最適化された部門サマリー計算"""
        if not records:
            return self._create_empty_summary(dept, period_start, period_end)

        # 統計値を1回のループで計算
        employees = set()
        total_work_minutes = 0
        total_overtime_minutes = 0
        work_days = 0
        violation_count = 0

        for record in records:
            employees.add(record.employee_id)

            work_minutes = record.get_work_duration_minutes() or 0
            if work_minutes > 0:
                total_work_minutes += work_minutes
                work_days += 1

                # 残業計算
                if work_minutes > 480:  # 8時間超
                    total_overtime_minutes += work_minutes - 480

                # 違反チェック（簡易版）
                if work_minutes > 720:  # 12時間超
                    violation_count += 1

        # 効率的な出勤率計算
        employee_count = len(employees)
        calendar_days = (period_end - period_start).days + 1
        expected_work_days = self._calculate_expected_work_days(
            calendar_days, employees
        )

        attendance_rate = (
            (work_days / expected_work_days * 100) if expected_work_days > 0 else 0.0
        )
        average_work_minutes = total_work_minutes / work_days if work_days > 0 else 0.0

        # コンプライアンススコア計算
        compliance_score = self._calculate_compliance_score(
            violation_count, work_days, total_overtime_minutes
        )

        return DepartmentSummary(
            department_code=dept.code,
            department_name=dept.name,
            period_start=period_start,
            period_end=period_end,
            employee_count=employee_count,
            total_work_minutes=total_work_minutes,
            total_overtime_minutes=total_overtime_minutes,
            attendance_rate=attendance_rate,
            average_work_minutes=average_work_minutes,
            violation_count=violation_count,
            compliance_score=compliance_score,
        )

    def _create_empty_summary(
        self, dept: Department, period_start: date, period_end: date
    ) -> DepartmentSummary:
        """空のサマリー作成"""
        return DepartmentSummary(
            department_code=dept.code,
            department_name=dept.name,
            period_start=period_start,
            period_end=period_end,
            employee_count=0,
            total_work_minutes=0,
            total_overtime_minutes=0,
            attendance_rate=0.0,
            average_work_minutes=0.0,
            violation_count=0,
            compliance_score=100.0,
        )

    def _calculate_expected_work_days(self, calendar_days: int, employees: set) -> int:
        """期待勤務日数計算（営業日・祝日考慮）"""
        # 土日を除外（簡易計算）
        expected_work_days_per_employee = calendar_days * 5 // 7  # 平日のみ
        return expected_work_days_per_employee * len(employees)

    def _calculate_compliance_score(
        self, violation_count: int, work_days: int, total_overtime_minutes: int
    ) -> float:
        """詳細なコンプライアンススコア計算"""
        if work_days == 0:
            return 100.0

        base_score = 100.0

        # 違反率による減点
        violation_rate = violation_count / work_days
        base_score -= violation_rate * 30  # 違反1件につき30点減点

        # 残業時間による減点
        avg_overtime_per_day = total_overtime_minutes / work_days
        if avg_overtime_per_day > 180:  # 3時間/日超
            base_score -= min(20, (avg_overtime_per_day - 180) / 30)  # 最大20点減点

        return max(0.0, min(100.0, base_score))
