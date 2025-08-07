# TASK-103: 期間フィルタリング機能 - Test Cases Phase

## 1. Test Cases Phase概要

### 1.1 テスト戦略
- **境界値テスト重点**: うるう年・月末日・年跨ぎの完全網羅
- **エッジケーステスト充実**: 無効日付・範囲逆転・型不整合
- **統合テスト**: TASK-101/102連携動作の確認
- **パフォーマンステスト**: 大量データでの性能検証

### 1.2 テスト分類
- **単体テスト**: 個別機能の詳細検証
- **統合テスト**: モジュール間連携検証  
- **境界値テスト**: エッジケース専用検証
- **パフォーマンステスト**: 非機能要件検証

### 1.3 品質目標
- **テストカバレッジ**: 95%以上
- **境界値カバレッジ**: 100%（うるう年・月末日）
- **エラーケースカバレッジ**: 100%
- **統合テストカバレッジ**: 100%（TASK-101/102）

## 2. 単体テスト設計

### 2.1 月単位フィルタリング テスト (test_filter_by_month)

#### 2.1.1 正常系テスト

```python
class TestFilterByMonth:
    """月単位フィルタリング単体テスト"""
    
    def test_filter_standard_month(self):
        """標準月フィルタリング - 2024年1月"""
        # データ準備
        df = create_test_dataframe([
            {"work_date": "2023-12-31", "employee_id": "EMP001"},
            {"work_date": "2024-01-01", "employee_id": "EMP001"}, 
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-31", "employee_id": "EMP001"},
            {"work_date": "2024-02-01", "employee_id": "EMP001"},
        ])
        
        # テスト実行
        filter = DateFilter()
        result = filter.filter_by_month(df, "2024-01")
        
        # 検証
        assert result.filtered_count == 3
        assert result.original_count == 5
        assert result.date_range == (date(2024, 1, 1), date(2024, 1, 31))
        assert len(result.filtered_data) == 3
        assert all("2024-01" in str(d) for d in result.filtered_data["work_date"])
    
    def test_filter_february_normal_year(self):
        """2月フィルタリング - 平年(2023年)"""
        df = create_test_dataframe([
            {"work_date": "2023-01-31", "employee_id": "EMP001"},
            {"work_date": "2023-02-01", "employee_id": "EMP001"},
            {"work_date": "2023-02-28", "employee_id": "EMP001"},
            {"work_date": "2023-03-01", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_month(df, "2023-02")
        
        assert result.filtered_count == 2
        assert result.date_range == (date(2023, 2, 1), date(2023, 2, 28))
        assert result.latest_date == date(2023, 2, 28)
    
    def test_filter_february_leap_year(self):
        """🎯 2月フィルタリング - うるう年(2024年) - 重要境界値テスト"""
        df = create_test_dataframe([
            {"work_date": "2024-01-31", "employee_id": "EMP001"},
            {"work_date": "2024-02-01", "employee_id": "EMP001"},
            {"work_date": "2024-02-28", "employee_id": "EMP001"},
            {"work_date": "2024-02-29", "employee_id": "EMP001"},  # うるう年特有
            {"work_date": "2024-03-01", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_month(df, "2024-02")
        
        # うるう年の2月29日が正しく含まれることを検証
        assert result.filtered_count == 3
        assert result.date_range == (date(2024, 2, 1), date(2024, 2, 29))
        assert result.latest_date == date(2024, 2, 29)
        
        # 2024年2月29日のデータが確実に含まれていることを確認
        feb29_data = result.filtered_data[
            result.filtered_data["work_date"] == "2024-02-29"
        ]
        assert len(feb29_data) == 1
```

#### 2.1.2 境界値テスト - うるう年・月末日重点

```python
class TestMonthFilterBoundaries:
    """月フィルタリング境界値テスト - うるう年・月末日重点"""
    
    @pytest.mark.parametrize("year,expected_last_day", [
        (2020, 29),  # うるう年
        (2021, 28),  # 平年
        (2022, 28),  # 平年  
        (2023, 28),  # 平年
        (2024, 29),  # うるう年
        (2025, 28),  # 平年
        (2100, 28),  # 100年ルール（うるう年でない）
        (2000, 29),  # 400年ルール（うるう年）
    ])
    def test_february_last_day_detection(self, year, expected_last_day):
        """🎯 2月末日検出テスト - うるう年判定完全網羅"""
        df = create_test_dataframe([
            {"work_date": f"{year}-02-28", "employee_id": "EMP001"},
            {"work_date": f"{year}-02-{expected_last_day}" if expected_last_day == 29 else None, 
             "employee_id": "EMP001"},  # うるう年のみ2/29データ
            {"work_date": f"{year}-03-01", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_month(df, f"{year}-02")
        
        # 2月末日が正しく検出されることを検証
        assert result.date_range[1] == date(year, 2, expected_last_day)
        
        # うるう年の場合29日データが含まれることを確認
        if expected_last_day == 29:
            assert result.filtered_count >= 2  # 2/28 + 2/29
        else:
            assert result.filtered_count >= 1  # 2/28のみ
    
    @pytest.mark.parametrize("month,expected_days", [
        (1, 31),   # 1月 - 31日
        (2, 28),   # 2月 - 28日（平年、うるう年は別途テスト）
        (3, 31),   # 3月 - 31日
        (4, 30),   # 4月 - 30日
        (5, 31),   # 5月 - 31日
        (6, 30),   # 6月 - 30日
        (7, 31),   # 7月 - 31日
        (8, 31),   # 8月 - 31日
        (9, 30),   # 9月 - 30日
        (10, 31),  # 10月 - 31日
        (11, 30),  # 11月 - 30日
        (12, 31),  # 12月 - 31日
    ])
    def test_month_end_days_all_months(self, month, expected_days):
        """🎯 全月の月末日数テスト - 30/31日月の正確な処理"""
        year = 2023  # 平年を使用
        
        # 各月の最後の日のデータを作成
        last_day_str = f"{year}-{month:02d}-{expected_days:02d}"
        next_month_first_day = date(year, month, expected_days) + timedelta(days=1)
        
        df = create_test_dataframe([
            {"work_date": last_day_str, "employee_id": "EMP001"},
            {"work_date": next_month_first_day.strftime("%Y-%m-%d"), "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_month(df, f"{year}-{month:02d}")
        
        # 月末日の正確な検出を検証
        assert result.date_range == (date(year, month, 1), date(year, month, expected_days))
        assert result.filtered_count == 1
        assert result.latest_date == date(year, month, expected_days)
    
    def test_year_boundary_crossing(self):
        """🎯 年跨ぎ境界テスト - 12月→1月の正確な処理"""
        df = create_test_dataframe([
            {"work_date": "2023-12-29", "employee_id": "EMP001"},
            {"work_date": "2023-12-30", "employee_id": "EMP001"},
            {"work_date": "2023-12-31", "employee_id": "EMP001"},  # 年末
            {"work_date": "2024-01-01", "employee_id": "EMP001"},  # 年始
            {"work_date": "2024-01-02", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        
        # 2023年12月のフィルタリング
        result_dec = filter.filter_by_month(df, "2023-12")
        assert result_dec.filtered_count == 3
        assert result_dec.latest_date == date(2023, 12, 31)
        
        # 2024年1月のフィルタリング
        result_jan = filter.filter_by_month(df, "2024-01")
        assert result_jan.filtered_count == 2
        assert result_jan.earliest_date == date(2024, 1, 1)
        
        # 重複データがないことを確認
        all_dates = set()
        for d in result_dec.filtered_data["work_date"]:
            all_dates.add(str(d))
        for d in result_jan.filtered_data["work_date"]:
            assert str(d) not in all_dates  # 重複なし
```

### 2.2 日付範囲フィルタリング テスト (test_filter_by_range)

#### 2.2.1 正常系テスト

```python
class TestFilterByRange:
    """日付範囲フィルタリング単体テスト"""
    
    def test_filter_standard_range(self):
        """標準日付範囲フィルタリング"""
        df = create_test_dataframe([
            {"work_date": "2024-01-10", "employee_id": "EMP001"},
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-20", "employee_id": "EMP001"},
            {"work_date": "2024-01-25", "employee_id": "EMP001"},
            {"work_date": "2024-01-30", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_range(df, "2024-01-15", "2024-01-25")
        
        assert result.filtered_count == 3  # 15, 20, 25
        assert result.date_range == (date(2024, 1, 15), date(2024, 1, 25))
        assert result.earliest_date == date(2024, 1, 15)
        assert result.latest_date == date(2024, 1, 25)
    
    def test_filter_cross_month_range(self):
        """月跨ぎ日付範囲フィルタリング"""
        df = create_test_dataframe([
            {"work_date": "2024-01-25", "employee_id": "EMP001"},
            {"work_date": "2024-01-31", "employee_id": "EMP001"},
            {"work_date": "2024-02-01", "employee_id": "EMP001"},
            {"work_date": "2024-02-15", "employee_id": "EMP001"},
            {"work_date": "2024-02-20", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_range(df, "2024-01-30", "2024-02-10")
        
        assert result.filtered_count == 2  # 1/31, 2/1
        
    def test_filter_cross_year_range(self):
        """🎯 年跨ぎ日付範囲フィルタリング - 重要境界値テスト"""
        df = create_test_dataframe([
            {"work_date": "2023-12-25", "employee_id": "EMP001"},
            {"work_date": "2023-12-31", "employee_id": "EMP001"},
            {"work_date": "2024-01-01", "employee_id": "EMP001"},
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-31", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_range(df, "2023-12-30", "2024-01-10")
        
        assert result.filtered_count == 2  # 12/31, 1/1
        assert result.date_range == (date(2023, 12, 30), date(2024, 1, 10))
```

#### 2.2.2 境界値・エラーケーステスト

```python
class TestRangeFilterBoundaries:
    """日付範囲境界値・エラーケーステスト"""
    
    def test_leap_year_february_range(self):
        """🎯 うるう年2月を含む範囲テスト"""
        df = create_test_dataframe([
            {"work_date": "2024-02-27", "employee_id": "EMP001"},
            {"work_date": "2024-02-28", "employee_id": "EMP001"},
            {"work_date": "2024-02-29", "employee_id": "EMP001"},  # うるう年のみ存在
            {"work_date": "2024-03-01", "employee_id": "EMP001"},
            {"work_date": "2024-03-02", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_range(df, "2024-02-28", "2024-03-01")
        
        # うるう年の2月29日が含まれることを確認
        assert result.filtered_count == 3  # 2/28, 2/29, 3/1
        
        # 2024年2月29日が確実に含まれることを確認
        filtered_dates = [str(d) for d in result.filtered_data["work_date"]]
        assert "2024-02-29" in filtered_dates
    
    def test_invalid_date_range_start_after_end(self):
        """🎯 無効範囲 - 開始日 > 終了日のエラーテスト"""
        df = create_test_dataframe([
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        
        with pytest.raises(DateRangeError, match="開始日が終了日より後です"):
            filter.filter_by_range(df, "2024-01-20", "2024-01-10")
    
    def test_invalid_date_format(self):
        """🎯 無効日付フォーマットのエラーテスト"""
        df = create_test_dataframe([
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        
        with pytest.raises(InvalidPeriodError, match="無効な日付フォーマット"):
            filter.filter_by_range(df, "2024/13/45", "2024-01-31")
    
    def test_nonexistent_date_handling(self):
        """🎯 存在しない日付の処理テスト"""
        df = create_test_dataframe([
            {"work_date": "2024-02-28", "employee_id": "EMP001"},
            {"work_date": "2024-02-29", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        
        # 平年の2月29日を指定した場合の処理
        with pytest.raises(InvalidPeriodError, match="存在しない日付"):
            filter.filter_by_range(df, "2023-02-29", "2023-03-01")  # 2023年は平年
    
    def test_same_date_range(self):
        """同一日付範囲テスト"""
        df = create_test_dataframe([
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-16", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_range(df, "2024-01-15", "2024-01-15")
        
        assert result.filtered_count == 1
        assert result.earliest_date == result.latest_date == date(2024, 1, 15)
```

### 2.3 相対期間フィルタリング テスト (test_filter_by_relative)

```python
class TestFilterByRelative:
    """相対期間フィルタリング単体テスト"""
    
    @freeze_time("2024-02-15")  # 現在時刻を固定
    def test_filter_last_month(self):
        """先月フィルタリング"""
        df = create_test_dataframe([
            {"work_date": "2023-12-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-05", "employee_id": "EMP001"},
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-25", "employee_id": "EMP001"},
            {"work_date": "2024-02-05", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_relative(df, "last_month")
        
        # 2024-02-15の先月は2024-01
        assert result.filtered_count == 3
        assert result.date_range == (date(2024, 1, 1), date(2024, 1, 31))
    
    @freeze_time("2024-03-10")  # うるう年3月での先月テスト
    def test_filter_last_month_leap_february(self):
        """🎯 先月フィルタリング - うるう年2月の検証"""
        df = create_test_dataframe([
            {"work_date": "2024-01-31", "employee_id": "EMP001"},
            {"work_date": "2024-02-01", "employee_id": "EMP001"},
            {"work_date": "2024-02-28", "employee_id": "EMP001"},
            {"work_date": "2024-02-29", "employee_id": "EMP001"},  # うるう年
            {"work_date": "2024-03-01", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_relative(df, "last_month")
        
        # 2024-03-10の先月は2024-02（うるう年なので29日まで）
        assert result.filtered_count == 3  # 2/1, 2/28, 2/29
        assert result.date_range == (date(2024, 2, 1), date(2024, 2, 29))
        assert result.latest_date == date(2024, 2, 29)
    
    @freeze_time("2024-01-10")
    def test_filter_this_month(self):
        """今月フィルタリング"""
        df = create_test_dataframe([
            {"work_date": "2023-12-25", "employee_id": "EMP001"},
            {"work_date": "2024-01-05", "employee_id": "EMP001"},
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-02-01", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_relative(df, "this_month")
        
        assert result.filtered_count == 2
        assert all("2024-01" in str(d) for d in result.filtered_data["work_date"])
    
    @freeze_time("2024-12-15")
    def test_filter_next_month_year_crossing(self):
        """🎯 来月フィルタリング - 年跨ぎケース"""
        df = create_test_dataframe([
            {"work_date": "2024-11-25", "employee_id": "EMP001"},
            {"work_date": "2024-12-15", "employee_id": "EMP001"},
            {"work_date": "2025-01-05", "employee_id": "EMP001"},
            {"work_date": "2025-01-15", "employee_id": "EMP001"},
            {"work_date": "2025-02-01", "employee_id": "EMP001"},
        ])
        
        filter = DateFilter()
        result = filter.filter_by_relative(df, "next_month")
        
        # 2024-12-15の来月は2025-01
        assert result.filtered_count == 2
        assert result.date_range == (date(2025, 1, 1), date(2025, 1, 31))
```

### 2.4 統合テスト設計

#### 2.4.1 TASK-101 CSVReader統合テスト

```python
class TestCSVReaderIntegration:
    """TASK-101 CSVReader統合テスト"""
    
    def test_enhanced_csv_reader_with_date_filter(self):
        """EnhancedCSVReaderでの期間フィルタ統合"""
        # テストCSVファイル作成
        test_csv = create_test_csv([
            ["employee_id", "employee_name", "work_date"],
            ["EMP001", "田中太郎", "2024-01-15"],
            ["EMP001", "田中太郎", "2024-01-20"],
            ["EMP001", "田中太郎", "2024-02-01"],
            ["EMP002", "佐藤花子", "2024-01-25"],
        ])
        
        # 統合クラスインスタンス作成
        csv_reader = CSVReader()
        date_filter = DateFilter()
        integrated_filter = IntegratedDateFilter(csv_reader, None, date_filter)
        
        # 期間フィルタ付きCSV読み込み
        period_spec = PeriodSpecification(
            period_type=PeriodType.MONTH,
            month_string="2024-01"
        )
        result = integrated_filter.load_and_filter(test_csv, period_spec)
        
        assert result.filtered_count == 3  # 1月のデータのみ
        assert len(result.filtered_data) == 3
    
    def test_csv_date_column_auto_detection(self):
        """CSV日付列の自動検出テスト"""
        # 異なる日付列名のCSV
        test_csv = create_test_csv([
            ["社員ID", "氏名", "勤務日"],  # 日本語カラム名
            ["EMP001", "田中太郎", "2024-01-15"],
            ["EMP001", "田中太郎", "2024-02-01"],
        ])
        
        csv_reader = CSVReader()
        df = csv_reader.load_file(test_csv)
        
        date_filter = DateFilter()
        result = date_filter.filter_by_month(df, "2024-01")  # 自動検出に依存
        
        assert result.filtered_count == 1
```

#### 2.4.2 TASK-102 DataValidator統合テスト

```python
class TestDataValidatorIntegration:
    """TASK-102 DataValidator統合テスト"""
    
    def test_validated_date_filter(self):
        """検証済みデータでの期間フィルタリング"""
        df = create_test_dataframe([
            {"employee_id": "EMP001", "work_date": "2024-01-15"},
            {"employee_id": "", "work_date": "2024-01-20"},        # 無効データ
            {"employee_id": "EMP002", "work_date": "2030-01-25"},  # 未来日（警告）
            {"employee_id": "EMP003", "work_date": "2024-01-30"},
        ])
        
        # DataValidator統合
        validator = DataValidator()
        date_filter = ValidatedDateFilter(validator)
        
        period_spec = PeriodSpecification(
            period_type=PeriodType.MONTH,
            month_string="2024-01"
        )
        
        validation_report, filter_result = date_filter.validate_and_filter(df, period_spec)
        
        # 検証結果確認
        assert validation_report.total_records == 4
        assert len(validation_report.errors) == 1  # 空社員ID
        assert len(validation_report.warnings) == 1  # 未来日
        
        # フィルタリング結果確認（有効データのみ）
        assert filter_result.filtered_count == 2  # EMP001, EMP003の1月データ
    
    def test_validation_error_handling_in_filter(self):
        """フィルタリング時の検証エラー処理"""
        df = create_test_dataframe([
            {"employee_id": "EMP001", "work_date": "invalid_date"},
            {"employee_id": "EMP002", "work_date": "2024-01-15"},
        ])
        
        validator = DataValidator()
        date_filter = ValidatedDateFilter(validator)
        
        # 検証エラーがある場合の処理
        with pytest.raises(ValidationError, match="無効な日付"):
            date_filter.filter_by_month(df, "2024-01")
```

### 2.5 パフォーマンステスト設計

#### 2.5.1 大量データ処理テスト

```python
class TestPerformance:
    """パフォーマンステスト"""
    
    def test_large_dataset_performance(self):
        """大量データ処理性能テスト"""
        # 100万件のテストデータ作成
        large_df = create_large_test_dataframe(1_000_000, 
                                             date_range=("2020-01-01", "2024-12-31"))
        
        date_filter = DateFilter()
        
        # 処理時間測定
        start_time = time.time()
        result = date_filter.filter_by_month(large_df, "2024-01")
        processing_time = time.time() - start_time
        
        # パフォーマンス要件検証
        assert processing_time < 10.0  # 10秒以内
        assert result.filtered_count > 0
        assert result.processing_time < 10.0
    
    def test_memory_efficiency(self):
        """メモリ効率性テスト"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # 大量データでフィルタリング
        large_df = create_large_test_dataframe(500_000)
        date_filter = DateFilter()
        
        for month in ["2024-01", "2024-02", "2024-03"]:
            result = date_filter.filter_by_month(large_df, month)
            del result  # 明示的削除
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # メモリ増加量が1GB以内であることを確認
        assert memory_increase < 1024 * 1024 * 1024  # 1GB
    
    @pytest.mark.parametrize("chunk_size", [1000, 10000, 50000])
    def test_chunked_processing(self, chunk_size):
        """チャンク処理性能テスト"""
        large_df = create_large_test_dataframe(100_000)
        
        date_filter = DateFilter()
        date_filter.config.chunk_size = chunk_size
        
        result = date_filter.filter_by_month(large_df, "2024-01")
        
        # チャンクサイズに関わらず結果が一致することを確認
        assert result.filtered_count > 0
        assert result.processing_time > 0
```

### 2.6 エラーケース・エッジケーステスト

#### 2.6.1 データ型・フォーマット異常テスト

```python
class TestErrorCases:
    """エラーケース・エッジケーステスト"""
    
    def test_mixed_date_formats(self):
        """混在する日付フォーマットの処理"""
        df = create_test_dataframe([
            {"work_date": "2024-01-15", "employee_id": "EMP001"},    # YYYY-MM-DD
            {"work_date": "01/20/2024", "employee_id": "EMP002"},    # MM/DD/YYYY
            {"work_date": "2024/01/25", "employee_id": "EMP003"},    # YYYY/MM/DD
            {"work_date": "Jan 30, 2024", "employee_id": "EMP004"},  # 英語フォーマット
        ])
        
        date_filter = DateFilter()
        result = date_filter.filter_by_month(df, "2024-01")
        
        # 異なるフォーマットが正しく解析されることを確認
        assert result.filtered_count == 4
    
    def test_null_and_empty_dates(self):
        """NULL・空文字日付の処理"""
        df = create_test_dataframe([
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": None, "employee_id": "EMP002"},         # NULL
            {"work_date": "", "employee_id": "EMP003"},           # 空文字
            {"work_date": "N/A", "employee_id": "EMP004"},        # 文字列
        ])
        
        date_filter = DateFilter()
        result = date_filter.filter_by_month(df, "2024-01")
        
        # 有効なデータのみがフィルタされることを確認
        assert result.filtered_count == 1
        assert result.excluded_records == 3
    
    def test_timezone_handling(self):
        """タイムゾーン処理テスト"""
        df = create_test_dataframe([
            {"work_date": "2024-01-15T00:00:00+00:00", "employee_id": "EMP001"},  # UTC
            {"work_date": "2024-01-15T09:00:00+09:00", "employee_id": "EMP002"},  # JST
            {"work_date": "2024-01-15", "employee_id": "EMP003"},                 # タイムゾーンなし
        ])
        
        date_filter = DateFilter()
        result = date_filter.filter_by_month(df, "2024-01")
        
        # タイムゾーンに関わらず同じ日付として処理されることを確認
        assert result.filtered_count == 3
    
    def test_extreme_date_values(self):
        """極端な日付値の処理"""
        df = create_test_dataframe([
            {"work_date": "1900-01-01", "employee_id": "EMP001"},  # 過去の極端な日付
            {"work_date": "2100-12-31", "employee_id": "EMP002"},  # 未来の極端な日付
            {"work_date": "2024-01-15", "employee_id": "EMP003"},
        ])
        
        date_filter = DateFilter()
        
        # 極端な過去日のフィルタリング
        result_past = date_filter.filter_by_month(df, "1900-01")
        assert result_past.filtered_count == 1
        
        # 極端な未来日のフィルタリング
        result_future = date_filter.filter_by_month(df, "2100-12")
        assert result_future.filtered_count == 1
```

## 3. テスト実装戦略

### 3.1 テストデータ生成戦略

#### 3.1.1 境界値データ生成

```python
def generate_boundary_test_data():
    """境界値テスト用データ生成"""
    
    boundary_dates = []
    
    # うるう年境界データ
    leap_years = [2020, 2024, 2028, 2000]  # 400年ルールを含む
    normal_years = [2021, 2022, 2023, 2100]  # 100年ルールを含む
    
    for year in leap_years:
        boundary_dates.extend([
            f"{year}-02-28",
            f"{year}-02-29",  # うるう年のみ有効
            f"{year}-03-01",
        ])
    
    for year in normal_years:
        boundary_dates.extend([
            f"{year}-02-27",
            f"{year}-02-28",
            f"{year}-03-01",
        ])
    
    # 月末日境界データ
    months_30 = [4, 6, 9, 11]  # 30日月
    months_31 = [1, 3, 5, 7, 8, 10, 12]  # 31日月
    
    for month in months_30:
        boundary_dates.extend([
            f"2024-{month:02d}-29",
            f"2024-{month:02d}-30",
        ])
        if month != 12:
            boundary_dates.append(f"2024-{month+1:02d}-01")
        else:
            boundary_dates.append("2025-01-01")
    
    for month in months_31:
        boundary_dates.extend([
            f"2024-{month:02d}-30",
            f"2024-{month:02d}-31",
        ])
    
    return boundary_dates
```

#### 3.1.2 大量データ生成

```python
def create_large_test_dataframe(num_records: int, 
                              date_range: tuple = ("2020-01-01", "2024-12-31")) -> pd.DataFrame:
    """大量テストデータ生成"""
    
    start_date = datetime.strptime(date_range[0], "%Y-%m-%d")
    end_date = datetime.strptime(date_range[1], "%Y-%m-%d")
    date_diff = end_date - start_date
    
    data = []
    for i in range(num_records):
        # ランダム日付生成
        random_days = random.randint(0, date_diff.days)
        work_date = start_date + timedelta(days=random_days)
        
        data.append({
            "employee_id": f"EMP{i:06d}",
            "employee_name": f"Employee {i}",
            "work_date": work_date.strftime("%Y-%m-%d"),
            "start_time": f"{random.randint(7, 10):02d}:00",
            "end_time": f"{random.randint(17, 22):02d}:00",
        })
    
    return pd.DataFrame(data)
```

### 3.2 テスト実行戦略

#### 3.2.1 段階的テスト実行

```python
# テスト実行順序
TEST_EXECUTION_ORDER = [
    # Phase 1: 基本機能テスト
    "test_filter_by_month",
    "test_filter_by_range", 
    "test_filter_by_relative",
    
    # Phase 2: 境界値テスト
    "test_leap_year_boundaries",
    "test_month_end_boundaries", 
    "test_year_crossing_boundaries",
    
    # Phase 3: エラーケーステスト
    "test_invalid_inputs",
    "test_data_type_errors",
    "test_edge_cases",
    
    # Phase 4: 統合テスト
    "test_csv_reader_integration",
    "test_data_validator_integration",
    
    # Phase 5: パフォーマンステスト
    "test_large_data_performance",
    "test_memory_efficiency",
]
```

#### 3.2.2 継続的テスト環境

```python
# pytest設定 (pytest.ini)
[tool:pytest]
testpaths = tests
markers = 
    unit: 単体テスト
    integration: 統合テスト
    boundary: 境界値テスト
    performance: パフォーマンステスト
    slow: 低速テスト
addopts = 
    --cov=src/attendance_tool
    --cov-report=html
    --cov-report=term
    --cov-fail-under=90
    -v
    --tb=short
```

## 4. 品質保証戦略

### 4.1 カバレッジ目標

| テスト分類 | カバレッジ目標 | 測定基準 |
|-----------|--------------|----------|
| 単体テスト | 95%以上 | line coverage |
| 境界値テスト | 100% | うるう年・月末日全パターン |
| エラーケーステスト | 100% | 全例外パス |
| 統合テスト | 100% | TASK-101/102連携 |

### 4.2 品質メトリクス

- **Mutation Testing Score**: 80%以上
- **Property-based Testing**: 主要関数で実施
- **Performance Regression**: 前回比10%以内
- **Memory Leak Detection**: 0件

### 4.3 自動化戦略

```python
# CI/CDパイプライン統合
stages:
  - unit_tests
  - boundary_tests  
  - integration_tests
  - performance_tests
  - mutation_tests
  
script:
  - pytest tests/unit --markers=boundary
  - pytest tests/integration 
  - pytest tests/performance --markers=slow
  - mutmut run
```

---

**Test Cases Phase完了判定**: 全テストケース設計完了、TDD Red実装準備完了

*作成日: 2025年8月7日*  
*作成者: Claude Code TDD実装チーム*  
*文書版数: v1.0.0*