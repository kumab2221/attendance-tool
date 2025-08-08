# TASK-203: 部門別集計機能 - テストケース設計

## テストケース設計方針

### 1. テスト戦略
- **単体テスト**: 各メソッドの個別機能テスト
- **統合テスト**: 部門階層と勤怠データの連携テスト
- **境界値テスト**: 極端なケース（大量データ、深い階層等）
- **エラーテスト**: 不正データ・例外条件への対応

### 2. テストデータ構造
```python
# 基本部門構造（3階層）
TEST_DEPARTMENTS = [
    Department("DEPT001", "本社", None, 0, True),
    Department("DEPT002", "営業部", "DEPT001", 1, True),
    Department("DEPT003", "東京営業課", "DEPT002", 2, True),
    Department("DEPT004", "大阪営業課", "DEPT002", 2, True),
    Department("DEPT005", "技術部", "DEPT001", 1, True),
    Department("DEPT006", "開発課", "DEPT005", 2, True),
]

# テスト従業員データ（各部門に配置）
TEST_EMPLOYEES = [
    ("EMP001", "田中太郎", "DEPT003"),  # 東京営業課
    ("EMP002", "佐藤花子", "DEPT003"),  # 東京営業課
    ("EMP003", "鈴木次郎", "DEPT004"),  # 大阪営業課
    ("EMP004", "山田三郎", "DEPT006"),  # 開発課
    # ...
]
```

## 単体テストケース

### TC-203-001: Department クラステスト
```python
class TestDepartment:
    def test_department_creation(self):
        # 正常な部門オブジェクト作成
        dept = Department("DEPT001", "営業部", None, 0, True)
        assert dept.code == "DEPT001"
        assert dept.name == "営業部"
        assert dept.parent_code is None
        assert dept.level == 0
        assert dept.is_active is True
    
    def test_department_hierarchy(self):
        # 階層関係の設定
        parent = Department("DEPT001", "本社", None, 0, True)
        child = Department("DEPT002", "営業部", "DEPT001", 1, True)
        assert child.parent_code == parent.code
        assert child.level == parent.level + 1
    
    def test_invalid_department_code(self):
        # 無効な部門コードのテスト
        with pytest.raises(ValueError):
            Department("", "営業部", None, 0, True)
        with pytest.raises(ValueError):
            Department("INVALID", "営業部", None, 0, True)
```

### TC-203-002: DepartmentAggregator 初期化テスト
```python
class TestDepartmentAggregatorInit:
    def test_empty_departments(self):
        # 空の部門リストで初期化
        aggregator = DepartmentAggregator([])
        assert len(aggregator.departments) == 0
        assert len(aggregator.department_tree) == 0
    
    def test_valid_departments(self):
        # 有効な部門リストで初期化
        departments = self.create_test_departments()
        aggregator = DepartmentAggregator(departments)
        assert len(aggregator.departments) == len(departments)
        assert aggregator.validate_hierarchy() is True
    
    def test_circular_reference_detection(self):
        # 循環参照の検出
        bad_departments = [
            Department("DEPT001", "部門A", "DEPT002", 1, True),
            Department("DEPT002", "部門B", "DEPT001", 1, True),
        ]
        with pytest.raises(CircularReferenceError):
            DepartmentAggregator(bad_departments)
```

### TC-203-003: 部門別集計テスト
```python
class TestDepartmentAggregation:
    def test_single_department_aggregation(self):
        # 単一部門の集計
        records = self.create_attendance_records("DEPT003", 5, 20)  # 5人×20日
        aggregator = self.create_test_aggregator()
        
        summary = aggregator.aggregate_single_department(
            "DEPT003", records, date(2024, 1, 1), date(2024, 1, 31)
        )
        
        assert summary.department_code == "DEPT003"
        assert summary.employee_count == 5
        assert summary.total_work_minutes > 0
        assert 0.0 <= summary.attendance_rate <= 100.0
    
    def test_multiple_departments_aggregation(self):
        # 複数部門の一括集計
        records = self.create_mixed_attendance_records()
        aggregator = self.create_test_aggregator()
        
        summaries = aggregator.aggregate_by_department(
            records, date(2024, 1, 1), date(2024, 1, 31)
        )
        
        assert len(summaries) > 0
        dept_codes = {s.department_code for s in summaries}
        assert "DEPT003" in dept_codes
        assert "DEPT004" in dept_codes
    
    def test_empty_department_handling(self):
        # 従業員が0人の部門
        records = []
        aggregator = self.create_test_aggregator()
        
        summary = aggregator.aggregate_single_department(
            "DEPT999", records, date(2024, 1, 1), date(2024, 1, 31)
        )
        
        assert summary.employee_count == 0
        assert summary.total_work_minutes == 0
        assert summary.attendance_rate == 0.0
```

### TC-203-004: 階層集計テスト
```python
class TestHierarchicalAggregation:
    def test_parent_child_aggregation(self):
        # 親部門への子部門集約
        records = self.create_hierarchical_records()
        aggregator = self.create_test_aggregator()
        
        # 課レベル集計
        child_summaries = aggregator.aggregate_by_department(records, 
            date(2024, 1, 1), date(2024, 1, 31))
        
        # 部レベル集計
        parent_summaries = aggregator.aggregate_by_hierarchy(child_summaries, 1)
        
        # 営業部の値は東京営業課+大阪営業課の合計であることを確認
        sales_summary = next(s for s in parent_summaries if s.department_code == "DEPT002")
        tokyo_summary = next(s for s in child_summaries if s.department_code == "DEPT003")  
        osaka_summary = next(s for s in child_summaries if s.department_code == "DEPT004")
        
        expected_work_minutes = tokyo_summary.total_work_minutes + osaka_summary.total_work_minutes
        assert sales_summary.total_work_minutes == expected_work_minutes
    
    def test_deep_hierarchy_aggregation(self):
        # 深い階層の集計
        deep_departments = self.create_deep_hierarchy(5)  # 5階層
        records = self.create_deep_hierarchy_records(deep_departments)
        aggregator = DepartmentAggregator(deep_departments)
        
        # 各階層レベルでの集計
        for level in range(5):
            summaries = aggregator.aggregate_by_hierarchy(records, level)
            assert len(summaries) > 0
    
    def test_hierarchy_validation(self):
        # 階層構造の妥当性検証
        aggregator = self.create_test_aggregator()
        
        # 正常な階層
        assert aggregator.validate_hierarchy() is True
        
        # 存在しない親部門参照
        bad_dept = Department("DEPT999", "テスト", "NONEXISTENT", 1, True)
        aggregator.departments.append(bad_dept)
        assert aggregator.validate_hierarchy() is False
```

## 統合テストケース

### TC-203-101: エンドツーエンド集計テスト
```python
class TestEndToEndAggregation:
    def test_full_aggregation_flow(self):
        # 完全な集計フローのテスト
        # 1. 部門マスター読み込み
        departments = self.load_test_department_master()
        aggregator = DepartmentAggregator(departments)
        
        # 2. 勤怠データ読み込み  
        records = self.load_test_attendance_data()
        
        # 3. 部門別集計実行
        summaries = aggregator.aggregate_by_department(
            records, date(2024, 1, 1), date(2024, 1, 31)
        )
        
        # 4. 階層集計実行
        hierarchy_summaries = {}
        for level in range(3):
            hierarchy_summaries[level] = aggregator.aggregate_by_hierarchy(summaries, level)
        
        # 5. 結果検証
        assert len(summaries) > 0
        assert all(s.employee_count >= 0 for s in summaries)
        assert all(s.total_work_minutes >= 0 for s in summaries)
        
    def test_period_filtering_integration(self):
        # 期間フィルタリングとの統合テスト
        records = self.create_multi_month_records()
        aggregator = self.create_test_aggregator()
        
        # 1月のみ
        jan_summaries = aggregator.aggregate_by_department(
            records, date(2024, 1, 1), date(2024, 1, 31)
        )
        
        # 2月のみ  
        feb_summaries = aggregator.aggregate_by_department(
            records, date(2024, 2, 1), date(2024, 2, 29)
        )
        
        # 1-2月通し
        q1_summaries = aggregator.aggregate_by_department(
            records, date(2024, 1, 1), date(2024, 2, 29)
        )
        
        # 期間別で結果が異なることを確認
        jan_total = sum(s.total_work_minutes for s in jan_summaries)
        feb_total = sum(s.total_work_minutes for s in feb_summaries)  
        q1_total = sum(s.total_work_minutes for s in q1_summaries)
        
        assert q1_total >= jan_total + feb_total  # 完全一致は期待しない（異動等考慮）
```

## 境界値・エラーテストケース

### TC-203-201: 境界値テスト
```python
class TestBoundaryValues:
    def test_large_department_count(self):
        # 大量部門数のテスト（100部門）
        large_departments = self.create_large_department_structure(100)
        aggregator = DepartmentAggregator(large_departments)
        
        records = self.create_large_attendance_dataset(100, 100, 30)  # 100部門×100名×30日
        start_time = time.time()
        
        summaries = aggregator.aggregate_by_department(
            records, date(2024, 1, 1), date(2024, 1, 31)
        )
        
        elapsed_time = time.time() - start_time
        assert elapsed_time < 300  # 5分以内
        assert len(summaries) <= 100
    
    def test_deep_hierarchy_limit(self):
        # 最大階層深度のテスト（10階層）
        deep_departments = self.create_deep_hierarchy(10)
        aggregator = DepartmentAggregator(deep_departments)
        
        records = self.create_deep_hierarchy_records(deep_departments)
        summaries = aggregator.aggregate_by_department(
            records, date(2024, 1, 1), date(2024, 1, 31)
        )
        
        # 最深部門から最上位部門まで集計可能
        for level in range(10):
            level_summaries = aggregator.aggregate_by_hierarchy(summaries, level)
            assert len(level_summaries) > 0
    
    def test_extreme_work_hours(self):
        # 極端な勤務時間データのテスト
        extreme_records = [
            self.create_record("EMP001", "DEPT003", 0),      # 0時間勤務
            self.create_record("EMP002", "DEPT003", 1440),   # 24時間勤務  
            self.create_record("EMP003", "DEPT003", 2880),   # 48時間勤務（異常値）
        ]
        
        aggregator = self.create_test_aggregator()
        summary = aggregator.aggregate_single_department(
            "DEPT003", extreme_records, date(2024, 1, 1), date(2024, 1, 31)
        )
        
        # 異常値が適切に処理されることを確認
        assert summary.total_work_minutes >= 0
        assert summary.average_work_minutes >= 0
```

### TC-203-202: エラーハンドリングテスト
```python
class TestErrorHandling:
    def test_invalid_department_data(self):
        # 無効な部門データ
        invalid_departments = [
            Department("", "空コード", None, 0, True),          # 空部門コード
            Department("DEPT001", "", None, 0, True),            # 空部門名
            Department("DEPT002", "正常", "NONEXISTENT", 1, True), # 存在しない親部門
        ]
        
        with pytest.raises(ValidationError):
            DepartmentAggregator(invalid_departments)
    
    def test_data_inconsistency_handling(self):
        # データ不整合の処理
        aggregator = self.create_test_aggregator()
        
        inconsistent_records = [
            # 存在しない部門に所属する従業員
            self.create_record_with_invalid_dept("EMP999", "NONEXISTENT", 480),
        ]
        
        # エラーが発生しても処理が継続されることを確認
        summaries = aggregator.aggregate_by_department(
            inconsistent_records, date(2024, 1, 1), date(2024, 1, 31)
        )
        
        # 無効なレコードは除外される
        assert len(summaries) == 0
    
    def test_memory_limit_handling(self):
        # メモリ制限テスト
        # 実際の実装では制限を超えた場合の適切な処理を確認
        pass  # TODO: 実装時に追加
```

## パフォーマンステストケース

### TC-203-301: パフォーマンステスト
```python  
class TestPerformance:
    def test_aggregation_performance(self):
        # 集計パフォーマンステスト
        # 100部門 × 100名 × 30日 = 300,000レコード
        large_dataset = self.create_performance_test_data()
        aggregator = self.create_test_aggregator()
        
        start_time = time.time()
        memory_start = self.get_memory_usage()
        
        summaries = aggregator.aggregate_by_department(
            large_dataset, date(2024, 1, 1), date(2024, 1, 31)
        )
        
        elapsed_time = time.time() - start_time
        memory_used = self.get_memory_usage() - memory_start
        
        # パフォーマンス要件確認
        assert elapsed_time < 300      # 5分以内
        assert memory_used < 500 * 1024 * 1024  # 500MB以内
        assert len(summaries) > 0
    
    def test_concurrent_aggregation(self):
        # 並行処理テスト
        import threading
        
        aggregator = self.create_test_aggregator()
        records = self.create_test_records()
        results = []
        
        def aggregate_worker():
            summary = aggregator.aggregate_by_department(
                records, date(2024, 1, 1), date(2024, 1, 31)
            )
            results.append(summary)
        
        # 複数スレッドで同時実行
        threads = [threading.Thread(target=aggregate_worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # 全ての結果が同じであることを確認
        assert len(results) == 5
        assert all(len(r) == len(results[0]) for r in results)
```

## テストユーティリティ

### ヘルパーメソッド
```python
class TestHelper:
    def create_test_departments(self) -> List[Department]:
        """テスト用部門データ作成"""
        return [
            Department("DEPT001", "本社", None, 0, True),
            Department("DEPT002", "営業部", "DEPT001", 1, True),
            Department("DEPT003", "東京営業課", "DEPT002", 2, True),
            Department("DEPT004", "大阪営業課", "DEPT002", 2, True),
            Department("DEPT005", "技術部", "DEPT001", 1, True),
            Department("DEPT006", "開発課", "DEPT005", 2, True),
        ]
    
    def create_attendance_records(self, dept_code: str, 
                                 employee_count: int, day_count: int) -> List[AttendanceRecord]:
        """テスト用勤怠レコード作成"""
        records = []
        for emp_idx in range(employee_count):
            emp_id = f"EMP{emp_idx:03d}"
            for day in range(day_count):
                work_date = date(2024, 1, 1) + timedelta(days=day)
                record = AttendanceRecord(
                    employee_id=emp_id,
                    employee_name=f"従業員{emp_idx:03d}",
                    department_code=dept_code,
                    work_date=work_date,
                    work_status="出勤",
                    start_time=time(9, 0),
                    end_time=time(18, 0),
                    break_minutes=60
                )
                records.append(record)
        return records
    
    def create_test_aggregator(self) -> DepartmentAggregator:
        """テスト用集計器作成"""
        return DepartmentAggregator(self.create_test_departments())
```

## テスト実行順序

### Phase 1: 基本単体テスト
1. Department クラステスト
2. DepartmentAggregator 初期化テスト
3. 単一部門集計テスト

### Phase 2: 機能統合テスト
1. 複数部門集計テスト
2. 階層集計テスト
3. エンドツーエンドテスト

### Phase 3: 品質保証テスト
1. 境界値テスト
2. エラーハンドリングテスト
3. パフォーマンステスト

## 期待される測定値

### コードカバレッジ目標
- 行カバレッジ: 90%以上
- 分岐カバレッジ: 85%以上
- 関数カバレッジ: 100%

### パフォーマンス目標
- 処理時間: 5分以内（標準データセット）
- メモリ使用: 500MB以内
- 同時実行: 劣化率20%以内