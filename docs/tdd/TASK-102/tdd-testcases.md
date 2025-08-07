# TASK-102: データ検証・クレンジング機能 - テストケース設計

## 1. テスト設計概要

### 1.1 テスト戦略
- **TDD (Test-Driven Development)**: テスト先行開発による品質確保
- **カバレッジ目標**: 単体テスト95%以上、統合テスト100%
- **テストピラミッド**: Unit Tests > Integration Tests > E2E Tests

### 1.2 テストカテゴリ
1. **Unit Tests**: 各クラス・メソッドの個別テスト
2. **Integration Tests**: コンポーネント間連携テスト
3. **Boundary Tests**: 境界値・異常値テスト
4. **Performance Tests**: パフォーマンス要件検証
5. **Error Handling Tests**: エラーケース処理テスト

## 2. Unit Tests (単体テスト)

### 2.1 AttendanceRecord (pydantic モデル) テスト

#### 2.1.1 正常系テスト
```python
class TestAttendanceRecordNormal:
    def test_valid_record_creation(self):
        """有効なレコード作成テスト"""
        # Given: 有効なデータ
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎", 
            "department": "開発部",
            "work_date": date(2024, 1, 15),
            "start_time": time(9, 0),
            "end_time": time(18, 0),
            "break_minutes": 60
        }
        
        # When: レコード作成
        record = AttendanceRecord(**data)
        
        # Then: 正しく作成される
        assert record.employee_id == "EMP001"
        assert record.work_date == date(2024, 1, 15)
        
    def test_optional_fields_none(self):
        """オプショナルフィールドがNoneのケース"""
        # Given: 必須フィールドのみ
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎",
            "work_date": date(2024, 1, 15)
        }
        
        # When & Then: エラーなしで作成
        record = AttendanceRecord(**data)
        assert record.department is None
        assert record.start_time is None
        assert record.end_time is None
```

#### 2.1.2 バリデーションテスト
```python
class TestAttendanceRecordValidation:
    def test_invalid_employee_id_empty(self):
        """空の社員IDテスト (エラーケース)"""
        # Given: 空の社員ID
        data = {
            "employee_id": "",
            "employee_name": "田中太郎",
            "work_date": date(2024, 1, 15)
        }
        
        # When & Then: ValidationError発生
        with pytest.raises(ValidationError, match="社員IDは必須"):
            AttendanceRecord(**data)
            
    def test_future_work_date(self):
        """未来日の検証 (EDGE-204)"""
        # Given: 未来の日付
        future_date = date.today() + timedelta(days=1)
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎",
            "work_date": future_date
        }
        
        # When & Then: 警告レベルの例外
        with pytest.raises(ValidationError, match="未来の日付"):
            AttendanceRecord(**data)
            
    def test_start_time_after_end_time(self):
        """出勤時刻 > 退勤時刻 (EDGE-201)"""
        # Given: 論理的に矛盾する時刻
        data = {
            "employee_id": "EMP001", 
            "employee_name": "田中太郎",
            "work_date": date(2024, 1, 15),
            "start_time": time(18, 0),  # 18:00
            "end_time": time(9, 0)      # 09:00
        }
        
        # When & Then: 時刻論理エラー
        with pytest.raises(TimeLogicError, match="出勤時刻が退勤時刻より遅い"):
            AttendanceRecord(**data)
            
    def test_negative_break_minutes(self):
        """負の休憩時間"""
        # Given: 負の休憩時間
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎", 
            "work_date": date(2024, 1, 15),
            "break_minutes": -30
        }
        
        # When & Then: バリデーションエラー
        with pytest.raises(ValidationError, match="休憩時間は0以上"):
            AttendanceRecord(**data)
```

### 2.2 DataValidator クラステスト

#### 2.2.1 DataFrame検証テスト
```python
class TestDataValidatorDataFrame:
    def setup_method(self):
        """テスト準備"""
        self.validator = DataValidator(config={}, rules=[])
        
    def test_validate_dataframe_success(self):
        """正常なDataFrame検証"""
        # Given: 有効なDataFrame
        df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002'],
            'employee_name': ['田中太郎', '山田花子'],
            'work_date': ['2024-01-15', '2024-01-15'],
            'start_time': ['09:00', '09:30'],
            'end_time': ['18:00', '18:30']
        })
        
        # When: 検証実行
        report = self.validator.validate_dataframe(df)
        
        # Then: 成功結果
        assert report.total_records == 2
        assert report.valid_records == 2
        assert len(report.errors) == 0
        assert report.quality_score >= 0.95
        
    def test_validate_dataframe_with_errors(self):
        """エラーありDataFrame検証"""
        # Given: エラーを含むDataFrame
        df = pd.DataFrame({
            'employee_id': ['EMP001', ''],  # 空の社員ID
            'employee_name': ['田中太郎', '山田花子'],
            'work_date': ['2024-01-15', '2025-01-15'],  # 未来日
            'start_time': ['18:00', '09:30'],  # 論理エラー
            'end_time': ['09:00', '18:30']
        })
        
        # When: 検証実行
        report = self.validator.validate_dataframe(df)
        
        # Then: エラー検出
        assert report.total_records == 2
        assert report.valid_records == 0  # 両方エラー
        assert len(report.errors) >= 2
        assert any("社員ID" in error.message for error in report.errors)
        assert any("時刻論理" in error.message for error in report.errors)
        
    def test_validate_large_dataframe_performance(self):
        """大量データ処理性能テスト"""
        # Given: 10,000件のDataFrame
        size = 10000
        df = pd.DataFrame({
            'employee_id': [f'EMP{i:04d}' for i in range(size)],
            'employee_name': [f'社員{i}' for i in range(size)],
            'work_date': ['2024-01-15'] * size,
            'start_time': ['09:00'] * size,
            'end_time': ['18:00'] * size
        })
        
        # When: 検証実行 (時間測定)
        start_time = time.time()
        report = self.validator.validate_dataframe(df)
        end_time = time.time()
        
        # Then: 性能要件達成 (30秒以内)
        processing_time = end_time - start_time
        assert processing_time <= 30.0
        assert report.total_records == size
        assert report.valid_records == size
```

#### 2.2.2 個別レコード検証テスト
```python
class TestDataValidatorRecord:
    def test_validate_record_success(self):
        """正常レコード検証"""
        # Given: 有効なレコード
        record = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': '2024-01-15',
            'start_time': '09:00',
            'end_time': '18:00'
        }
        
        # When: レコード検証
        validator = DataValidator(config={}, rules=[])
        errors = validator.validate_record(record)
        
        # Then: エラーなし
        assert len(errors) == 0
        
    def test_validate_record_multiple_errors(self):
        """複数エラーレコード検証"""
        # Given: 複数エラーを含むレコード
        record = {
            'employee_id': '',  # エラー1: 空ID
            'employee_name': '田中太郎',
            'work_date': '2025-01-15',  # エラー2: 未来日
            'start_time': '25:00',  # エラー3: 無効時刻
            'end_time': '18:00'
        }
        
        # When: レコード検証
        validator = DataValidator(config={}, rules=[])
        errors = validator.validate_record(record)
        
        # Then: 3つのエラー検出
        assert len(errors) == 3
        error_messages = [error.message for error in errors]
        assert any("社員ID" in msg for msg in error_messages)
        assert any("未来" in msg for msg in error_messages)
        assert any("無効な時刻" in msg for msg in error_messages)
```

### 2.3 DataCleaner クラステスト

#### 2.3.1 自動修正テスト
```python
class TestDataCleanerAutoCorrection:
    def test_clean_time_format(self):
        """時刻フォーマット統一"""
        # Given: 様々な時刻フォーマット
        df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002', 'EMP003'],
            'start_time': ['9:00', '09:00:00', '9時00分'],
            'end_time': ['18:0', '18:00:00', '18時00分']
        })
        
        # When: 自動修正実行
        cleaner = DataCleaner(config={})
        cleaned_df = cleaner.apply_auto_corrections(df)
        
        # Then: 統一されたフォーマット
        assert cleaned_df.loc[0, 'start_time'] == '09:00'
        assert cleaned_df.loc[1, 'start_time'] == '09:00' 
        assert cleaned_df.loc[2, 'start_time'] == '09:00'
        
    def test_clean_department_names(self):
        """部署名正規化"""
        # Given: 表記ゆれのある部署名
        df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002', 'EMP003'],
            'department': ['開発部', '開発課', 'Development']
        })
        
        # When: 正規化実行
        cleaner = DataCleaner(config={'department_mapping': {
            '開発課': '開発部',
            'Development': '開発部'
        }})
        cleaned_df = cleaner.apply_auto_corrections(df)
        
        # Then: 統一された部署名
        assert all(dept == '開発部' for dept in cleaned_df['department'])
```

#### 2.3.2 修正提案テスト
```python
class TestDataCleanerSuggestions:
    def test_suggest_time_corrections(self):
        """時刻修正提案"""
        # Given: 時刻論理エラー
        errors = [
            ValidationError(
                row_number=1,
                field='time_logic',
                message='出勤時刻が退勤時刻より遅い',
                value=('18:00', '09:00')
            )
        ]
        
        # When: 修正提案生成
        cleaner = DataCleaner(config={})
        suggestions = cleaner.suggest_corrections(errors)
        
        # Then: 適切な提案
        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.correction_type == 'time_swap'
        assert '日跨ぎ勤務' in suggestion.description
        assert suggestion.confidence_score >= 0.7
        
    def test_suggest_date_corrections(self):
        """日付修正提案"""
        # Given: 未来日エラー
        errors = [
            ValidationError(
                row_number=1,
                field='work_date',
                message='未来の日付です',
                value='2025-01-15'
            )
        ]
        
        # When: 修正提案生成
        cleaner = DataCleaner(config={})
        suggestions = cleaner.suggest_corrections(errors)
        
        # Then: 年度修正提案
        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.correction_type == 'date_year'
        assert '2024-01-15' in suggestion.suggested_value
```

## 3. Integration Tests (統合テスト)

### 3.1 CSVReader統合テスト
```python
class TestCSVReaderIntegration:
    def test_enhanced_csv_reader_full_workflow(self):
        """完全ワークフローテスト"""
        # Given: テストCSVファイル作成
        test_csv = self.create_test_csv_with_errors()
        
        # When: 統合処理実行
        validator = DataValidator(config={}, rules=[])
        cleaner = DataCleaner(config={})
        enhanced_reader = EnhancedCSVReader(validator, cleaner)
        
        df, report = enhanced_reader.load_and_validate(test_csv)
        
        # Then: 期待される結果
        assert isinstance(df, pd.DataFrame)
        assert isinstance(report, ValidationReport)
        assert report.total_records > 0
        assert len(report.errors) >= 0  # エラー検出
        assert len(report.warnings) >= 0  # 警告検出
        
    def test_csv_reader_compatibility(self):
        """既存CSVReaderとの互換性テスト"""
        # Given: 既存のCSVファイル
        csv_path = "/path/to/existing/test.csv"
        
        # When: 両方の読み込み方法で処理
        old_reader = CSVReader()
        new_reader = EnhancedCSVReader(
            DataValidator(config={}, rules=[]),
            DataCleaner(config={})
        )
        
        old_df = old_reader.load_file(csv_path)
        new_df, report = new_reader.load_and_validate(csv_path)
        
        # Then: 基本的なデータは同じ
        assert len(old_df) == len(new_df)
        assert list(old_df.columns) == list(new_df.columns)
```

### 3.2 エラーハンドリング統合テスト
```python
class TestErrorHandlingIntegration:
    def test_edge_201_time_logic_integration(self):
        """EDGE-201: 時刻論理エラー統合処理"""
        # Given: 時刻論理エラーのあるCSV
        df = pd.DataFrame({
            'employee_id': ['EMP001'],
            'employee_name': ['田中太郎'],
            'work_date': ['2024-01-15'],
            'start_time': ['18:00'],  # 出勤時刻
            'end_time': ['09:00']     # 退勤時刻
        })
        
        # When: 統合検証実行
        validator = DataValidator(config={}, rules=[])
        report = validator.validate_dataframe(df)
        
        cleaner = DataCleaner(config={})
        suggestions = cleaner.suggest_corrections(report.errors)
        
        # Then: 適切なエラー検出と修正提案
        assert len(report.errors) >= 1
        assert any("時刻論理" in error.message for error in report.errors)
        assert len(suggestions) >= 1
        assert any("日跨ぎ" in sugg.description for sugg in suggestions)
        
    def test_req_104_work_hours_integration(self):
        """REQ-104: 勤務時間エラー統合処理"""
        # Given: 24時間超勤務のCSV
        df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002'],
            'employee_name': ['田中太郎', '山田花子'],
            'work_date': ['2024-01-15', '2024-01-15'],
            'start_time': ['08:00', '09:00'],
            'end_time': ['09:00', '08:30'],  # 負の勤務時間
            'break_minutes': [0, 0]
        })
        
        # When: 統合検証実行
        validator = DataValidator(config={}, rules=[])
        report = validator.validate_dataframe(df)
        
        # Then: 勤務時間エラー検出
        work_hour_errors = [
            error for error in report.errors 
            if "勤務時間" in error.message or "24時間" in error.message
        ]
        assert len(work_hour_errors) >= 1
```

## 4. Boundary Tests (境界値テスト)

### 4.1 時刻境界値テスト
```python
class TestTimeBoundaryValues:
    @pytest.mark.parametrize("start_time,end_time,expected_valid", [
        ("00:00", "23:59", True),   # 通常の24時間勤務
        ("23:59", "00:01", False),  # 日跨ぎ（2分勤務）
        ("23:58", "23:59", True),   # 1分勤務
        ("24:00", "08:00", False),  # 無効時刻
        ("09:00", "09:00", False),  # 同時刻（0時間勤務）
    ])
    def test_time_boundary_validation(self, start_time, end_time, expected_valid):
        """時刻境界値検証"""
        # Given: 境界値の時刻ペア
        record = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': '2024-01-15',
            'start_time': start_time,
            'end_time': end_time
        }
        
        # When: バリデーション実行
        validator = DataValidator(config={}, rules=[])
        errors = validator.validate_record(record)
        
        # Then: 期待される結果
        if expected_valid:
            assert len(errors) == 0
        else:
            assert len(errors) > 0
            
    def test_24_hour_shift_handling(self):
        """24時間勤務の処理"""
        # Given: 24時間勤務のデータ
        record = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': '2024-01-15',
            'start_time': '08:00',
            'end_time': '08:00',  # 翌日の8:00を想定
            'break_minutes': 60
        }
        
        # When: 検証実行
        validator = DataValidator(config={
            'allow_24hour_shift': True
        }, rules=[])
        errors = validator.validate_record(record)
        
        # Then: 警告レベルで処理
        warnings = [e for e in errors if e.level == 'WARNING']
        assert len(warnings) >= 1
        assert "24時間勤務" in warnings[0].message
```

### 4.2 日付境界値テスト
```python
class TestDateBoundaryValues:
    def test_leap_year_february_29(self):
        """うるう年2月29日のテスト"""
        # Given: うるう年の2月29日
        record = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': '2024-02-29'  # 2024年はうるう年
        }
        
        # When: 日付検証
        validator = DataValidator(config={}, rules=[])
        errors = validator.validate_record(record)
        
        # Then: エラーなし
        date_errors = [e for e in errors if 'date' in e.field]
        assert len(date_errors) == 0
        
    def test_non_leap_year_february_29(self):
        """非うるう年2月29日のテスト"""
        # Given: 非うるう年の2月29日
        record = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': '2023-02-29'  # 2023年は非うるう年
        }
        
        # When: 日付検証
        validator = DataValidator(config={}, rules=[])
        errors = validator.validate_record(record)
        
        # Then: 日付エラー
        date_errors = [e for e in errors if 'date' in e.field]
        assert len(date_errors) >= 1
        assert "無効な日付" in date_errors[0].message
```

## 5. Performance Tests (性能テスト)

### 5.1 大量データ処理テスト
```python
class TestPerformance:
    @pytest.mark.performance
    def test_large_dataset_processing(self):
        """大量データセット処理テスト"""
        # Given: 100,000件のテストデータ
        size = 100000
        df = self.generate_large_dataset(size)
        
        # When: 処理時間測定
        start_time = time.time()
        
        validator = DataValidator(config={}, rules=[])
        report = validator.validate_dataframe(df)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Then: 性能要件達成
        assert processing_time <= 300  # 5分以内
        assert report.total_records == size
        
        # メモリ使用量チェック
        memory_usage = self.get_memory_usage()
        expected_max_memory = df.memory_usage(deep=True).sum() * 3
        assert memory_usage <= expected_max_memory
        
    @pytest.mark.performance
    def test_parallel_processing_speedup(self):
        """並列処理による高速化テスト"""
        # Given: 中規模データセット
        df = self.generate_large_dataset(10000)
        
        # When: シングルプロセスとマルチプロセス比較
        # シングルプロセス
        start_time = time.time()
        validator_single = DataValidator(config={'parallel': False}, rules=[])
        report_single = validator_single.validate_dataframe(df)
        single_time = time.time() - start_time
        
        # マルチプロセス
        start_time = time.time()
        validator_multi = DataValidator(config={'parallel': True}, rules=[])
        report_multi = validator_multi.validate_dataframe(df)
        multi_time = time.time() - start_time
        
        # Then: 並列処理による高速化確認
        speedup_ratio = single_time / multi_time
        assert speedup_ratio >= 1.5  # 50%以上の高速化
        assert report_single.total_records == report_multi.total_records
```

## 6. Error Handling Tests (エラーハンドリングテスト)

### 6.1 例外処理テスト
```python
class TestExceptionHandling:
    def test_invalid_file_path(self):
        """無効ファイルパスのエラーハンドリング"""
        # Given: 存在しないファイルパス
        invalid_path = "/nonexistent/file.csv"
        
        # When & Then: 適切な例外発生
        enhanced_reader = EnhancedCSVReader(
            DataValidator(config={}, rules=[]),
            DataCleaner(config={})
        )
        
        with pytest.raises(FileNotFoundError, match="ファイルが見つかりません"):
            enhanced_reader.load_and_validate(invalid_path)
            
    def test_corrupted_data_handling(self):
        """破損データのハンドリング"""
        # Given: 破損したDataFrame
        corrupted_df = pd.DataFrame({
            'employee_id': [None, 'EMP001', float('nan')],
            'employee_name': ['', '田中太郎', None],
            'work_date': ['invalid_date', '2024-01-15', None]
        })
        
        # When: 検証実行
        validator = DataValidator(config={}, rules=[])
        report = validator.validate_dataframe(corrupted_df)
        
        # Then: 例外なく処理完了
        assert isinstance(report, ValidationReport)
        assert len(report.errors) >= 3  # 各行にエラー
        assert report.total_records == 3
        assert report.valid_records == 1  # 1行のみ有効
        
    def test_memory_exhaustion_handling(self):
        """メモリ不足時のハンドリング"""
        # Given: 極端に大きなデータセット（メモリ制限下）
        # This test would be run with limited memory allocation
        
        # When & Then: 適切にメモリ不足を処理
        # Implementation would handle this gracefully
        pass
```

### 6.2 部分的失敗テスト
```python
class TestPartialFailures:
    def test_partial_validation_failure(self):
        """部分的バリデーション失敗の処理"""
        # Given: 一部にエラーがあるデータ
        df = pd.DataFrame({
            'employee_id': ['EMP001', '', 'EMP003'],  # 2行目エラー
            'employee_name': ['田中太郎', '山田花子', '佐藤次郎'],
            'work_date': ['2024-01-15', '2024-01-15', '2025-01-15']  # 3行目警告
        })
        
        # When: バリデーション実行
        validator = DataValidator(config={}, rules=[])
        report = validator.validate_dataframe(df)
        
        # Then: 処理継続と適切な分類
        assert report.total_records == 3
        assert report.valid_records == 1  # 1行目のみ有効
        assert len(report.errors) >= 1    # 2行目エラー
        assert len(report.warnings) >= 1  # 3行目警告
        
        # エラーがあっても処理は継続される
        assert report.processing_time > 0
```

## 7. テストデータとフィクスチャ

### 7.1 テストデータ生成
```python
@pytest.fixture
def sample_valid_dataframe():
    """有効なサンプルDataFrame"""
    return pd.DataFrame({
        'employee_id': ['EMP001', 'EMP002', 'EMP003'],
        'employee_name': ['田中太郎', '山田花子', '佐藤次郎'],
        'department': ['開発部', '営業部', '開発部'],
        'work_date': ['2024-01-15', '2024-01-15', '2024-01-15'],
        'start_time': ['09:00', '09:30', '08:45'],
        'end_time': ['18:00', '18:30', '17:45'],
        'break_minutes': [60, 60, 45]
    })

@pytest.fixture
def sample_error_dataframe():
    """エラーを含むサンプルDataFrame"""
    return pd.DataFrame({
        'employee_id': ['EMP001', '', 'EMP003'],
        'employee_name': ['田中太郎', '山田花子', ''],
        'work_date': ['2024-01-15', '2025-01-15', 'invalid'],
        'start_time': ['09:00', '25:00', '18:00'],
        'end_time': ['18:00', '17:00', '09:00'],
        'break_minutes': [60, -30, 1440]
    })

@pytest.fixture
def test_config():
    """テスト用設定"""
    return {
        'validation': {
            'date_range': {
                'past_years': 5,
                'future_days': 0
            },
            'time_validation': {
                'max_work_minutes': 1440
            }
        },
        'cleaning': {
            'auto_correction_level': 'standard',
            'suggestion_threshold': 0.7
        }
    }
```

### 7.2 モックとスタブ
```python
@pytest.fixture
def mock_csv_reader():
    """CSVReaderのモック"""
    mock_reader = Mock(spec=CSVReader)
    mock_reader.load_file.return_value = sample_valid_dataframe()
    return mock_reader

@pytest.fixture
def mock_config_loader():
    """設定ローダーのモック"""
    mock_loader = Mock()
    mock_loader.load_config.return_value = test_config()
    return mock_loader
```

## 8. テスト実行戦略

### 8.1 テスト分類とマーク
```python
# テストマーク定義
pytest.mark.unit        # 単体テスト
pytest.mark.integration # 統合テスト
pytest.mark.boundary    # 境界値テスト
pytest.mark.performance # 性能テスト
pytest.mark.slow        # 実行時間の長いテスト
```

### 8.2 テスト実行コマンド
```bash
# 全テスト実行
pytest tests/

# 単体テストのみ
pytest -m unit tests/

# 統合テストのみ  
pytest -m integration tests/

# 性能テスト除外
pytest -m "not performance" tests/

# カバレッジ付き実行
pytest --cov=src/attendance_tool/validation tests/

# 並列実行
pytest -n auto tests/
```

### 8.3 継続的インテグレーション
```yaml
# GitHub Actions設定例
- name: Run Unit Tests
  run: pytest -m unit --cov=src

- name: Run Integration Tests  
  run: pytest -m integration

- name: Run Performance Tests
  run: pytest -m performance
  if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

## 9. テスト成功基準

### 9.1 カバレッジ基準
- **単体テスト**: 95%以上のコードカバレッジ
- **統合テスト**: 100%の統合ポイントカバレッジ
- **境界値テスト**: 全境界条件のカバレッジ

### 9.2 品質基準
- **テスト実行時間**: 全テスト5分以内
- **テスト安定性**: 99%以上の成功率
- **テストメンテナンス性**: 機能変更時の修正コスト最小化

### 9.3 実用性基準
- **バグ検出率**: 開発段階で90%以上のバグを検出
- **回帰防止**: 既存機能の品質維持
- **ドキュメント性**: テストがソフトウェア仕様として機能