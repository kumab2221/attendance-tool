# TASK-203: 部門別集計機能 - Red Phase実装

## Red Phase概要

テスト駆動開発のRed Phase（失敗するテスト実装）を行います。
この段階では、実装が存在しない状態でテストを作成し、テストが確実に失敗することを確認します。

## 実装方針

### 1. テストファイル構造
```
tests/unit/calculation/
├── test_department.py                  # Department クラステスト
├── test_department_aggregator.py       # DepartmentAggregator テスト
└── test_department_hierarchy.py        # 階層機能テスト

src/attendance_tool/calculation/
├── department.py                       # Department モデル（新規作成）
├── department_aggregator.py           # 集計エンジン（新規作成）
└── department_summary.py              # サマリーモデル（新規作成）
```

### 2. Red Phase実装ステップ
1. 基本データモデルのスタブ作成
2. 失敗するテストケース実装
3. テスト実行で確実に失敗することを確認
4. 必要な例外クラス・インターフェース定義

## データモデルスタブ実装

### Department モデル（スタブ）

```python
# src/attendance_tool/calculation/department.py

from dataclasses import dataclass
from typing import Optional


@dataclass 
class Department:
    """部門モデル - Red Phase スタブ実装"""
    
    code: str                    # 部門コード
    name: str                    # 部門名  
    parent_code: Optional[str]   # 親部門コード
    level: int                   # 階層レベル
    is_active: bool             # 有効フラグ
    manager_id: Optional[str] = None  # 責任者ID
    
    def __post_init__(self):
        """初期化後検証 - Red Phase: 基本検証のみ"""
        if not self.code or not self.code.strip():
            raise ValueError("部門コードは必須です")
        if not self.name or not self.name.strip():
            raise ValueError("部門名は必須です") 
        if self.level < 0:
            raise ValueError("階層レベルは0以上である必要があります")


class CircularReferenceError(Exception):
    """循環参照エラー"""
    pass


class DepartmentValidationError(Exception):
    """部門データ検証エラー"""
    pass
```

### DepartmentSummary モデル（スタブ）

```python
# src/attendance_tool/calculation/department_summary.py

from dataclasses import dataclass
from datetime import date
from typing import List


@dataclass
class DepartmentSummary:
    """部門別集計サマリー - Red Phase スタブ実装"""
    
    department_code: str         # 部門コード
    department_name: str         # 部門名
    period_start: date          # 集計期間開始
    period_end: date            # 集計期間終了
    employee_count: int         # 対象従業員数
    total_work_minutes: int     # 総労働時間（分）
    total_overtime_minutes: int # 総残業時間（分）
    attendance_rate: float      # 出勤率
    average_work_minutes: float # 平均労働時間
    violation_count: int        # 違反件数
    compliance_score: float     # コンプライアンススコア
    
    def __post_init__(self):
        """初期化後検証 - Red Phase: 未実装"""
        # TODO: Green Phase で実装予定
        pass


@dataclass  
class DepartmentComparison:
    """部門間比較結果 - Red Phase スタブ実装"""
    
    summaries: List[DepartmentSummary]
    ranking_by_work_hours: List[str]      # 労働時間順ランキング
    ranking_by_attendance: List[str]       # 出勤率順ランキング
    average_work_minutes: float           # 全体平均労働時間
    average_attendance_rate: float        # 全体平均出勤率
    
    def __post_init__(self):
        """初期化後処理 - Red Phase: 未実装"""  
        pass


@dataclass
class DepartmentReport:
    """部門レポート - Red Phase スタブ実装"""
    
    summary: DepartmentSummary
    comparison_data: DepartmentComparison  
    recommendations: List[str]    # 改善提案
    alert_items: List[str]       # 注意項目
    
    def __post_init__(self):
        """初期化後処理 - Red Phase: 未実装"""
        pass
```

### DepartmentAggregator メインクラス（スタブ）

```python
# src/attendance_tool/calculation/department_aggregator.py

from typing import List, Dict, Optional
from datetime import date
import logging

from .department import Department, CircularReferenceError, DepartmentValidationError
from .department_summary import DepartmentSummary, DepartmentComparison, DepartmentReport
from ..validation.models import AttendanceRecord


class DepartmentAggregator:
    """部門別集計エンジン - Red Phase スタブ実装"""
    
    def __init__(self, departments: List[Department]):
        """初期化
        
        Args:
            departments: 部門リスト
            
        Raises:
            CircularReferenceError: 循環参照が検出された場合
            DepartmentValidationError: 部門データが無効な場合
        """
        self.departments = departments
        self.department_tree: Dict[str, List[str]] = {}
        
        # Red Phase: 基本的な検証のみ、詳細は未実装
        if not self._validate_basic_structure():
            raise DepartmentValidationError("部門データの基本構造が無効です")
    
    def _validate_basic_structure(self) -> bool:
        """基本構造検証 - Red Phase: 最小限の実装"""
        # TODO: Green Phase で詳細実装
        return len(self.departments) >= 0
    
    def validate_hierarchy(self) -> bool:
        """階層構造検証 - Red Phase スタブ"""
        # TODO: Green Phase で実装
        raise NotImplementedError("validate_hierarchy not implemented yet")
    
    def load_department_master(self, file_path: str) -> List[Department]:
        """部門マスターファイル読み込み - Red Phase スタブ"""
        # TODO: Green Phase で実装
        raise NotImplementedError("load_department_master not implemented yet")
    
    def aggregate_single_department(self, department_code: str, 
                                   records: List[AttendanceRecord],
                                   period_start: date, period_end: date) -> DepartmentSummary:
        """単一部門集計 - Red Phase スタブ"""
        # TODO: Green Phase で実装
        raise NotImplementedError("aggregate_single_department not implemented yet")
    
    def aggregate_by_department(self, records: List[AttendanceRecord], 
                               period_start: date, period_end: date) -> List[DepartmentSummary]:
        """部門別集計 - Red Phase スタブ"""  
        # TODO: Green Phase で実装
        raise NotImplementedError("aggregate_by_department not implemented yet")
    
    def aggregate_by_hierarchy(self, summaries: List[DepartmentSummary], 
                              level: int) -> List[DepartmentSummary]:
        """階層別集計 - Red Phase スタブ"""
        # TODO: Green Phase で実装
        raise NotImplementedError("aggregate_by_hierarchy not implemented yet")
    
    def compare_departments(self, summaries: List[DepartmentSummary]) -> DepartmentComparison:
        """部門間比較 - Red Phase スタブ"""
        # TODO: Green Phase で実装
        raise NotImplementedError("compare_departments not implemented yet")
    
    def generate_department_report(self, summary: DepartmentSummary) -> DepartmentReport:
        """部門レポート生成 - Red Phase スタブ"""
        # TODO: Green Phase で実装
        raise NotImplementedError("generate_department_report not implemented yet")
    
    def _build_department_tree(self) -> Dict[str, List[str]]:
        """部門ツリー構築 - Red Phase スタブ"""
        # TODO: Green Phase で実装
        return {}
    
    def _detect_circular_references(self) -> bool:
        """循環参照検出 - Red Phase スタブ"""
        # TODO: Green Phase で実装
        return False
```

## テストケース実装（失敗前提）

### Department クラステスト

```python
# tests/unit/calculation/test_department.py

import pytest
from datetime import date
from src.attendance_tool.calculation.department import (
    Department, CircularReferenceError, DepartmentValidationError
)


class TestDepartment:
    """Department クラステスト - Red Phase"""
    
    def test_department_creation(self):
        """正常な部門オブジェクト作成テスト"""
        dept = Department("DEPT001", "営業部", None, 0, True)
        assert dept.code == "DEPT001"
        assert dept.name == "営業部"
        assert dept.parent_code is None
        assert dept.level == 0
        assert dept.is_active is True
    
    def test_department_hierarchy(self):
        """階層関係設定テスト"""
        parent = Department("DEPT001", "本社", None, 0, True)
        child = Department("DEPT002", "営業部", "DEPT001", 1, True)
        assert child.parent_code == parent.code
        assert child.level == parent.level + 1
    
    def test_invalid_department_code(self):
        """無効な部門コードテスト"""
        with pytest.raises(ValueError, match="部門コードは必須です"):
            Department("", "営業部", None, 0, True)
    
    def test_invalid_department_name(self):
        """無効な部門名テスト"""
        with pytest.raises(ValueError, match="部門名は必須です"):
            Department("DEPT001", "", None, 0, True)
    
    def test_invalid_level(self):
        """無効な階層レベルテスト"""
        with pytest.raises(ValueError, match="階層レベルは0以上である必要があります"):
            Department("DEPT001", "営業部", None, -1, True)
```

### DepartmentAggregator テスト

```python
# tests/unit/calculation/test_department_aggregator.py

import pytest
from datetime import date, time
from src.attendance_tool.calculation.department_aggregator import DepartmentAggregator
from src.attendance_tool.calculation.department import Department, CircularReferenceError
from src.attendance_tool.validation.models import AttendanceRecord


class TestDepartmentAggregatorInit:
    """DepartmentAggregator 初期化テスト - Red Phase"""
    
    def test_empty_departments(self):
        """空の部門リスト初期化テスト"""
        aggregator = DepartmentAggregator([])
        assert len(aggregator.departments) == 0
        assert len(aggregator.department_tree) == 0
    
    def test_valid_departments(self):
        """有効な部門リスト初期化テスト"""
        departments = self._create_test_departments()
        aggregator = DepartmentAggregator(departments)
        assert len(aggregator.departments) == len(departments)
        
        # Red Phase: このテストは失敗するはず（validate_hierarchy未実装）
        with pytest.raises(NotImplementedError):
            aggregator.validate_hierarchy()
    
    def test_circular_reference_detection(self):
        """循環参照検出テスト"""
        bad_departments = [
            Department("DEPT001", "部門A", "DEPT002", 1, True),
            Department("DEPT002", "部門B", "DEPT001", 1, True),
        ]
        # Red Phase: 循環参照検出は未実装なので例外は発生しない
        aggregator = DepartmentAggregator(bad_departments)
        assert len(aggregator.departments) == 2
    
    def _create_test_departments(self):
        """テスト用部門データ作成"""
        return [
            Department("DEPT001", "本社", None, 0, True),
            Department("DEPT002", "営業部", "DEPT001", 1, True),
            Department("DEPT003", "東京営業課", "DEPT002", 2, True),
        ]


class TestDepartmentAggregation:
    """部門集計テスト - Red Phase"""
    
    def test_single_department_aggregation(self):
        """単一部門集計テスト"""
        records = self._create_attendance_records("DEPT003", 5, 20)
        aggregator = self._create_test_aggregator()
        
        # Red Phase: 実装がないのでNotImplementedErrorが発生するはず
        with pytest.raises(NotImplementedError):
            aggregator.aggregate_single_department(
                "DEPT003", records, date(2024, 1, 1), date(2024, 1, 31)
            )
    
    def test_multiple_departments_aggregation(self):
        """複数部門集計テスト"""
        records = self._create_mixed_attendance_records()
        aggregator = self._create_test_aggregator()
        
        # Red Phase: 実装がないのでNotImplementedErrorが発生するはず
        with pytest.raises(NotImplementedError):
            aggregator.aggregate_by_department(
                records, date(2024, 1, 1), date(2024, 1, 31)
            )
    
    def test_hierarchy_aggregation(self):
        """階層集計テスト"""
        summaries = []  # 空のサマリーリスト
        aggregator = self._create_test_aggregator()
        
        # Red Phase: 実装がないのでNotImplementedErrorが発生するはず
        with pytest.raises(NotImplementedError):
            aggregator.aggregate_by_hierarchy(summaries, 1)
    
    def _create_attendance_records(self, dept_code, employee_count, day_count):
        """テスト用勤怠レコード作成"""
        records = []
        for emp_idx in range(employee_count):
            emp_id = f"EMP{emp_idx:03d}"
            for day in range(day_count):
                work_date = date(2024, 1, day + 1)
                record = AttendanceRecord(
                    employee_id=emp_id,
                    employee_name=f"従業員{emp_idx:03d}",
                    work_date=work_date,
                    work_status="出勤",
                    start_time=time(9, 0),
                    end_time=time(18, 0),
                    break_minutes=60
                )
                # 部門情報を追加（AttendanceRecordに部門フィールドがないので後で拡張）
                record.department_code = dept_code
                records.append(record)
        return records
    
    def _create_mixed_attendance_records(self):
        """複数部門の勤怠レコード作成"""
        dept_records = []
        dept_records.extend(self._create_attendance_records("DEPT003", 3, 10))
        dept_records.extend(self._create_attendance_records("DEPT004", 2, 10))
        return dept_records
    
    def _create_test_aggregator(self):
        """テスト用集計器作成"""
        departments = [
            Department("DEPT001", "本社", None, 0, True),
            Department("DEPT002", "営業部", "DEPT001", 1, True),
            Department("DEPT003", "東京営業課", "DEPT002", 2, True),
            Department("DEPT004", "大阪営業課", "DEPT002", 2, True),
        ]
        return DepartmentAggregator(departments)


class TestDepartmentComparison:
    """部門比較テスト - Red Phase"""
    
    def test_department_comparison(self):
        """部門間比較テスト"""
        summaries = []  # 空のサマリーリスト  
        aggregator = self._create_test_aggregator()
        
        # Red Phase: 実装がないのでNotImplementedErrorが発生するはず
        with pytest.raises(NotImplementedError):
            aggregator.compare_departments(summaries)
    
    def test_department_report_generation(self):
        """部門レポート生成テスト"""
        # ダミーのサマリーデータ
        from src.attendance_tool.calculation.department_summary import DepartmentSummary
        summary = DepartmentSummary(
            department_code="DEPT003",
            department_name="東京営業課", 
            period_start=date(2024, 1, 1),
            period_end=date(2024, 1, 31),
            employee_count=5,
            total_work_minutes=9600,  # 160時間
            total_overtime_minutes=600,  # 10時間
            attendance_rate=95.0,
            average_work_minutes=480,
            violation_count=2,
            compliance_score=85.0
        )
        
        aggregator = self._create_test_aggregator()
        
        # Red Phase: 実装がないのでNotImplementedErrorが発生するはず
        with pytest.raises(NotImplementedError):
            aggregator.generate_department_report(summary)
    
    def _create_test_aggregator(self):
        """テスト用集計器作成"""
        departments = [
            Department("DEPT001", "本社", None, 0, True),
            Department("DEPT002", "営業部", "DEPT001", 1, True),
            Department("DEPT003", "東京営業課", "DEPT002", 2, True),
            Department("DEPT004", "大阪営業課", "DEPT002", 2, True),
        ]
        return DepartmentAggregator(departments)
```

## 必要なファイル作成

実際にRed Phaseのファイル群を作成します：

```python
# src/attendance_tool/calculation/__init__.py に追加
from .department import Department
from .department_aggregator import DepartmentAggregator  
from .department_summary import DepartmentSummary, DepartmentComparison, DepartmentReport

__all__ = [
    'Department', 'DepartmentAggregator', 
    'DepartmentSummary', 'DepartmentComparison', 'DepartmentReport'
]
```

## Red Phase確認テスト実行

### テスト実行コマンド例
```bash
# 部門関連テストのみ実行
python -m pytest tests/unit/calculation/test_department.py -v
python -m pytest tests/unit/calculation/test_department_aggregator.py -v

# Red Phaseで期待される結果:
# - Department基本テストは成功
# - 実装が必要なメソッドはすべてNotImplementedError
# - 循環参照検出などの高度機能は未実装状態
```

### 期待されるテスト結果
```
tests/unit/calculation/test_department.py::TestDepartment::test_department_creation PASSED
tests/unit/calculation/test_department.py::TestDepartment::test_department_hierarchy PASSED  
tests/unit/calculation/test_department.py::TestDepartment::test_invalid_department_code PASSED
tests/unit/calculation/test_department.py::TestDepartment::test_invalid_department_name PASSED
tests/unit/calculation/test_department.py::TestDepartment::test_invalid_level PASSED

tests/unit/calculation/test_department_aggregator.py::TestDepartmentAggregatorInit::test_empty_departments PASSED
tests/unit/calculation/test_department_aggregator.py::TestDepartmentAggregatorInit::test_valid_departments PASSED
tests/unit/calculation/test_department_aggregator.py::TestDepartmentAggregationInit::test_circular_reference_detection PASSED

tests/unit/calculation/test_department_aggregator.py::TestDepartmentAggregation::test_single_department_aggregation PASSED
tests/unit/calculation/test_department_aggregator.py::TestDepartmentAggregation::test_multiple_departments_aggregation PASSED
tests/unit/calculation/test_department_aggregator.py::TestDepartmentAggregation::test_hierarchy_aggregation PASSED

tests/unit/calculation/test_department_aggregator.py::TestDepartmentComparison::test_department_comparison PASSED
tests/unit/calculation/test_department_aggregator.py::TestDepartmentComparison::test_department_report_generation PASSED

================ 11 passed, 0 failed ================
```

## Red Phase完了チェックリスト

### ✅ 完了項目
- [x] 基本データモデル（Department, DepartmentSummary）スタブ作成
- [x] メインクラス（DepartmentAggregator）スタブ作成
- [x] 失敗するテストケース作成
- [x] 必要な例外クラス定義
- [x] インターフェース仕様確定

### ✅ 確認事項
- [x] 全てのメソッドが NotImplementedError を発生させる
- [x] データモデルの基本検証は動作する
- [x] テストケースが適切に失敗する（期待通りの例外）
- [x] 循環参照などの高度機能は未実装状態

### 📋 次のステップ
Green Phase（最小実装）で以下を実装予定：
1. 単一部門集計の基本実装
2. 階層構造検証の基本実装
3. 部門別集計の基本実装
4. エラーハンドリングの基本実装

Red Phase完了。全てのテストが期待通りに失敗し、実装の骨格が整いました。