"""
Red Phase Tests for AdaptiveChunking - TASK-501
These tests are designed to FAIL until the AdaptiveChunking class is implemented.
"""

import pytest
import pandas as pd
from datetime import datetime, date
from unittest.mock import MagicMock, patch, Mock
from typing import Iterator, List
import psutil
import time
import gc

# These imports will fail because the classes don't exist yet
from attendance_tool.performance.chunk_processor import (
    AdaptiveChunking, 
    OptimizedCSVProcessor, 
    ProcessingChunk, 
    ChunkProcessingResult
)
from attendance_tool.models import AttendanceRecord


class TestAdaptiveChunking:
    """Test cases for AdaptiveChunking class - Red Phase (failing tests)"""
    
    @pytest.fixture
    def large_dataset(self) -> pd.DataFrame:
        """大容量テストデータセットを生成"""
        data = []
        for i in range(50000):  # 50,000レコード
            employee_id = f"EMP_{i % 1000:04d}"
            work_date = date(2024, 1, (i % 31) + 1)
            
            data.append({
                'employee_id': employee_id,
                'date': work_date,
                'start_time': datetime(2024, 1, 1, 9, 0),
                'end_time': datetime(2024, 1, 1, 18, 0),
                'break_minutes': 60,
                'total_hours': 8.0,
                'overtime_hours': max(0, (i % 10) - 8) * 0.5
            })
        
        return pd.DataFrame(data)
    
    def test_optimal_chunk_size_calculation(self, large_dataset):
        """最適チャンクサイズ算出テスト"""
        # 期待結果: データサイズとメモリに基づく最適サイズ
        # 性能目標: メモリ効率と処理速度の最適バランス
        
        chunker = AdaptiveChunking(
            initial_chunk_size=10000,
            memory_limit=512 * 1024 * 1024  # 512MB
        )
        
        # 利用可能メモリ量の異なるシナリオをテスト
        memory_scenarios = [
            (1024, 100000),  # 1GB利用可能 -> 大きなチャンク
            (512, 50000),    # 512MB利用可能 -> 中程度のチャンク  
            (256, 25000),    # 256MB利用可能 -> 小さなチャンク
            (128, 10000)     # 128MB利用可能 -> 最小チャンク
        ]
        
        for available_memory_mb, expected_min_chunk in memory_scenarios:
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.available = available_memory_mb * 1024 * 1024
                
                optimal_size = chunker.calculate_optimal_chunk_size(
                    data_size=len(large_dataset),
                    memory_usage=chunker.get_current_memory_usage()
                )
                
                # 最適サイズがメモリ制約に応じて調整されることを確認
                assert optimal_size >= expected_min_chunk, f"Chunk size {optimal_size} below minimum {expected_min_chunk}"
                assert optimal_size <= chunker.max_chunk_size, f"Chunk size {optimal_size} exceeds maximum"
                
                # チャンクサイズが妥当な範囲内にあることを確認
                assert 1000 <= optimal_size <= 100000, f"Chunk size {optimal_size} outside reasonable range"
    
    def test_memory_based_adaptation(self, large_dataset):
        """メモリベース適応テスト"""
        # 期待結果: 利用可能メモリに応じたサイズ調整
        # 性能目標: メモリ制限違反率0%
        
        chunker = AdaptiveChunking(
            memory_limit=256 * 1024 * 1024,  # 256MB制限
            adaptive_sizing=True
        )
        
        memory_violations = 0
        processed_chunks = 0
        memory_readings = []
        
        # メモリ監視付きチャンク処理
        for chunk in chunker.process_with_adaptive_chunking(large_dataset):
            processed_chunks += 1
            current_memory = chunker.get_memory_usage_mb()
            memory_readings.append(current_memory)
            
            # メモリ制限違反チェック
            if current_memory > 256:
                memory_violations += 1
            
            # チャンクサイズの適応性確認
            assert hasattr(chunk, 'adaptive_size')
            assert chunk.adaptive_size <= chunker.get_current_max_chunk_size()
        
        # メモリ制限違反率0%の確認
        violation_rate = memory_violations / processed_chunks if processed_chunks > 0 else 0
        assert violation_rate == 0, f"Memory violation rate {violation_rate:.2%} exceeds 0%"
        
        # 処理完了の確認
        assert processed_chunks > 0, "No chunks were processed"
        
        # メモリ使用パターンの確認
        max_memory = max(memory_readings)
        assert max_memory <= 256, f"Peak memory {max_memory}MB exceeded 256MB limit"
    
    def test_chunk_dependency_management(self):
        """チャンク依存関係管理テスト"""
        # 期待結果: 依存関係を持つデータの適切な分割
        # 性能目標: データ整合性100%維持
        
        # 時系列依存データを生成
        time_series_data = []
        for employee_id in range(100):
            for day in range(31):
                # 前日の残業が翌日の開始時間に影響するような依存関係
                prev_overtime = 0 if day == 0 else time_series_data[-1]['overtime_hours']
                start_delay = min(30, prev_overtime * 10)  # 残業時間に応じた遅刻
                
                time_series_data.append({
                    'employee_id': f'EMP_{employee_id:03d}',
                    'date': date(2024, 1, day + 1),
                    'start_time': datetime(2024, 1, day + 1, 9, int(start_delay)),
                    'end_time': datetime(2024, 1, day + 1, 18, 0),
                    'overtime_hours': max(0, (day + employee_id) % 5 - 2)
                })
        
        df = pd.DataFrame(time_series_data)
        
        chunker = AdaptiveChunking(
            dependency_aware=True,
            dependency_columns=['employee_id', 'date']
        )
        
        dependency_violations = 0
        chunk_boundaries = []
        
        # 依存関係を考慮したチャンク処理
        for chunk in chunker.process_with_adaptive_chunking(df):
            chunk_boundaries.append((chunk.start_index, chunk.end_index))
            
            # 依存関係チェック
            if chunker.has_dependency_violations(chunk):
                dependency_violations += 1
            
            # チャンク境界が適切に設定されていることを確認
            assert chunk.respects_dependencies, "Chunk violates data dependencies"
        
        # データ整合性100%維持の確認
        violation_rate = dependency_violations / len(chunk_boundaries) if chunk_boundaries else 0
        assert violation_rate == 0, f"Dependency violation rate {violation_rate:.2%} exceeds 0%"
        
        # チャンク境界の妥当性確認
        for i, (start, end) in enumerate(chunk_boundaries):
            if i > 0:
                prev_end = chunk_boundaries[i-1][1]
                assert start == prev_end, f"Gap detected between chunks: {prev_end} -> {start}"
    
    def test_dynamic_size_adjustment(self, large_dataset):
        """動的サイズ調整テスト"""
        # 期待結果: 処理中のリアルタイムサイズ調整
        # 性能目標: 処理効率10%向上
        
        chunker = AdaptiveChunking(
            initial_chunk_size=5000,
            dynamic_adjustment=True,
            adjustment_threshold=0.1  # 10%の効率変化で調整
        )
        
        processing_times = []
        chunk_sizes = []
        adjustments_made = 0
        
        start_time = time.time()
        
        for i, chunk in enumerate(chunker.process_with_adaptive_chunking(large_dataset)):
            chunk_start_time = time.time()
            
            # チャンク処理のシミュレート
            time.sleep(0.01)  # 処理時間のシミュレート
            
            chunk_end_time = time.time()
            processing_time = chunk_end_time - chunk_start_time
            processing_times.append(processing_time)
            chunk_sizes.append(chunk.size)
            
            # 動的調整の記録
            if i > 0 and chunk_sizes[i] != chunk_sizes[i-1]:
                adjustments_made += 1
            
            # 処理効率のモニタリング
            if i > 2:  # 最初の3チャンク後から効率測定
                recent_efficiency = chunker.calculate_processing_efficiency(processing_times[-3:])
                assert hasattr(chunker, 'efficiency_history')
        
        total_time = time.time() - start_time
        
        # 動的調整が発生していることを確認
        assert adjustments_made > 0, "No dynamic adjustments were made"
        
        # 処理効率向上の確認
        if len(processing_times) >= 10:
            early_efficiency = sum(processing_times[:5]) / 5
            late_efficiency = sum(processing_times[-5:]) / 5
            
            efficiency_improvement = (early_efficiency - late_efficiency) / early_efficiency
            assert efficiency_improvement >= 0.1, f"Efficiency improvement {efficiency_improvement:.2%} below 10%"
    
    def test_partial_failure_recovery(self, large_dataset):
        """部分失敗回復テスト"""
        # 期待結果: チャンク単位での失敗からの回復
        # 性能目標: 回復時間 < 10秒
        
        chunker = AdaptiveChunking(
            error_recovery=True,
            retry_failed_chunks=True,
            max_retries=3
        )
        
        # 意図的にエラーを含むデータを作成
        corrupted_dataset = large_dataset.copy()
        # 20%のレコードで意図的なエラーを導入
        error_indices = range(0, len(corrupted_dataset), 5)  # 5レコードごと
        for idx in error_indices:
            corrupted_dataset.at[idx, 'employee_id'] = None  # エラーの原因
        
        failed_chunks = []
        recovered_chunks = []
        recovery_times = []
        
        for chunk_result in chunker.process_with_error_recovery(corrupted_dataset):
            if chunk_result.had_errors:
                if chunk_result.recovery_successful:
                    recovered_chunks.append(chunk_result)
                    recovery_times.append(chunk_result.recovery_time_seconds)
                else:
                    failed_chunks.append(chunk_result)
        
        # 回復成功の確認
        total_chunks = len(recovered_chunks) + len(failed_chunks)
        recovery_rate = len(recovered_chunks) / total_chunks if total_chunks > 0 else 0
        assert recovery_rate >= 0.8, f"Recovery rate {recovery_rate:.2%} below 80%"
        
        # 回復時間の確認
        if recovery_times:
            avg_recovery_time = sum(recovery_times) / len(recovery_times)
            max_recovery_time = max(recovery_times)
            
            assert avg_recovery_time < 10, f"Average recovery time {avg_recovery_time:.2f}s exceeds 10s"
            assert max_recovery_time < 15, f"Max recovery time {max_recovery_time:.2f}s exceeds 15s"
    
    def test_memory_pressure_adaptation(self):
        """メモリ圧迫適応テスト"""
        # 期待結果: メモリ不足時の適応的サイズ縮小
        
        chunker = AdaptiveChunking(
            initial_chunk_size=20000,
            memory_pressure_threshold=0.85
        )
        
        # メモリ圧迫シミュレーション
        memory_scenarios = [
            (0.5, 20000),  # 50%使用率 -> 通常サイズ
            (0.7, 15000),  # 70%使用率 -> やや縮小
            (0.85, 10000), # 85%使用率 -> 大幅縮小
            (0.95, 5000)   # 95%使用率 -> 最小サイズ
        ]
        
        for memory_usage_percent, expected_max_size in memory_scenarios:
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.percent = memory_usage_percent * 100
                
                adjusted_size = chunker.adapt_to_memory_pressure()
                
                assert adjusted_size <= expected_max_size, f"Size {adjusted_size} not adapted for {memory_usage_percent:.0%} memory usage"
                assert adjusted_size >= chunker.min_chunk_size, "Size below minimum threshold"
    
    def test_chunk_processing_benchmark(self, large_dataset):
        """チャンク処理性能ベンチマーク"""
        # 期待結果: 基準性能の達成
        
        chunker = AdaptiveChunking()
        
        start_time = time.time()
        chunks_processed = 0
        total_records = 0
        
        for chunk in chunker.process_with_adaptive_chunking(large_dataset):
            chunks_processed += 1
            total_records += len(chunk.data)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 性能指標の確認
        records_per_second = total_records / processing_time
        assert records_per_second >= 5000, f"Processing speed {records_per_second:.1f} records/sec below 5000 threshold"
        
        chunks_per_second = chunks_processed / processing_time
        assert chunks_per_second >= 10, f"Chunk processing speed {chunks_per_second:.1f} chunks/sec below 10 threshold"
        
        # メモリ効率の確認
        peak_memory_mb = chunker.get_peak_memory_usage_mb()
        memory_per_record = peak_memory_mb / total_records
        assert memory_per_record < 0.01, f"Memory per record {memory_per_record:.4f}MB too high"


class TestOptimizedCSVProcessor:
    """Test cases for OptimizedCSVProcessor class - Red Phase (failing tests)"""
    
    @pytest.fixture
    def large_csv_file(self, tmp_path):
        """大容量CSVファイルを生成"""
        csv_file = tmp_path / "large_test_data.csv"
        
        # 100MB相当のCSVファイルを作成
        with open(csv_file, 'w', encoding='utf-8') as f:
            f.write("employee_id,date,start_time,end_time,break_minutes,total_hours\n")
            
            for i in range(100000):  # 約100MBのファイル
                employee_id = f"EMP_{i % 1000:04d}"
                work_date = f"2024-01-{(i % 31) + 1:02d}"
                f.write(f"{employee_id},{work_date},09:00:00,18:00:00,60,8.0\n")
        
        return str(csv_file)
    
    def test_large_csv_chunked_reading(self, large_csv_file):
        """大容量CSVチャンク読み込みテスト"""
        # 期待結果: 1GB以上CSVファイルの安全な読み込み
        # 性能目標: メモリ使用量一定（< 200MB）
        
        processor = OptimizedCSVProcessor(
            chunk_size=10000
        )
        
        memory_readings = []
        chunks_read = 0
        total_rows = 0
        
        # チャンク単位での読み込み
        for chunk_df in processor.read_csv_in_chunks(large_csv_file):
            chunks_read += 1
            total_rows += len(chunk_df)
            
            # メモリ使用量監視
            current_memory = processor.get_memory_usage_mb()
            memory_readings.append(current_memory)
            
            # チャンクの妥当性確認
            assert isinstance(chunk_df, pd.DataFrame)
            assert len(chunk_df) <= 10000
            assert len(chunk_df.columns) == 6
        
        # メモリ使用量一定の確認
        max_memory = max(memory_readings)
        assert max_memory <= 200, f"Peak memory {max_memory}MB exceeded 200MB limit"
        
        # メモリ変動の確認（50MB以下の変動）
        memory_variance = max(memory_readings) - min(memory_readings)
        assert memory_variance <= 50, f"Memory variance {memory_variance}MB too high"
        
        # 読み込み完了の確認
        assert total_rows == 100000, f"Expected 100000 rows, got {total_rows}"
        assert chunks_read > 0, "No chunks were read"
    
    def test_parallel_csv_processing(self, tmp_path):
        """並列CSV処理テスト"""
        # 期待結果: 複数CSVファイルの並列処理
        # 性能目標: 単一ファイル処理比3倍高速
        
        # 複数のCSVファイルを作成
        csv_files = []
        for i in range(4):
            csv_file = tmp_path / f"test_data_{i}.csv"
            with open(csv_file, 'w', encoding='utf-8') as f:
                f.write("employee_id,date,hours\n")
                for j in range(10000):
                    f.write(f"EMP_{j + i*10000:05d},2024-01-01,8.0\n")
            csv_files.append(str(csv_file))
        
        processor = OptimizedCSVProcessor(max_workers=4)
        
        # 単一ファイル処理時間測定
        start_time = time.time()
        single_result = processor.process_single_csv(csv_files[0])
        single_time = time.time() - start_time
        
        # 並列処理時間測定
        start_time = time.time()
        parallel_results = processor.parallel_csv_processing(csv_files)
        parallel_time = time.time() - start_time
        
        # 高速化率の確認
        expected_parallel_time = single_time * 4 / 4  # 理想的な並列化
        actual_speedup = (single_time * 4) / parallel_time
        assert actual_speedup >= 3.0, f"Parallel speedup {actual_speedup:.2f}x below 3.0x target"
        
        # 結果の妥当性確認
        assert len(parallel_results.combined_data) == 40000  # 4ファイル × 10000行
        assert parallel_results.processing_stats['files_processed'] == 4
        assert parallel_results.processing_stats['total_time'] == parallel_time
    
    def test_memory_mapped_file_processing(self, large_csv_file):
        """メモリマップドファイル処理テスト"""
        # 期待結果: 巨大ファイルの効率的アクセス
        # 性能目標: 従来読み込み比5倍高速
        
        processor = OptimizedCSVProcessor()
        
        # 通常読み込み時間測定
        start_time = time.time()
        normal_df = pd.read_csv(large_csv_file)
        normal_time = time.time() - start_time
        
        # メモリマップド処理時間測定
        start_time = time.time()
        mmap_result = processor.memory_mapped_processing(large_csv_file)
        mmap_time = time.time() - start_time
        
        # 5倍高速化の確認
        speedup = normal_time / mmap_time
        assert speedup >= 5.0, f"Memory mapped speedup {speedup:.2f}x below 5.0x target"
        
        # 結果の一致性確認
        assert len(mmap_result.data) == len(normal_df)
        assert mmap_result.data.columns.tolist() == normal_df.columns.tolist()
        
        # メモリ効率の確認
        mmap_memory_mb = mmap_result.peak_memory_usage_mb
        normal_memory_mb = processor.estimate_dataframe_memory_mb(normal_df)
        memory_efficiency = normal_memory_mb / mmap_memory_mb
        assert memory_efficiency >= 2.0, f"Memory efficiency {memory_efficiency:.2f}x below 2.0x target"
    
    def test_streaming_csv_validation(self, large_csv_file):
        """ストリーミングCSV検証テスト"""
        # 期待結果: チャンク処理中のデータ検証
        # 性能目標: 検証による速度低下 < 20%
        
        processor = OptimizedCSVProcessor(
            validation_enabled=True,
            validation_rules={
                'employee_id': {'pattern': r'^EMP_\d{4}$', 'required': True},
                'date': {'format': '%Y-%m-%d', 'required': True},
                'total_hours': {'min': 0, 'max': 24, 'type': float}
            }
        )
        
        # 検証なしの処理時間測定
        processor_no_validation = OptimizedCSVProcessor(validation_enabled=False)
        start_time = time.time()
        no_validation_chunks = list(processor_no_validation.read_csv_in_chunks(large_csv_file))
        no_validation_time = time.time() - start_time
        
        # 検証ありの処理時間測定
        start_time = time.time()
        validation_results = []
        validation_errors = []
        
        for chunk_result in processor.read_csv_in_chunks_with_validation(large_csv_file):
            validation_results.append(chunk_result.data)
            if chunk_result.validation_errors:
                validation_errors.extend(chunk_result.validation_errors)
        
        validation_time = time.time() - start_time
        
        # 速度低下20%以下の確認
        slowdown = (validation_time - no_validation_time) / no_validation_time
        assert slowdown <= 0.2, f"Validation slowdown {slowdown:.1%} exceeds 20%"
        
        # 検証結果の妥当性確認
        assert len(validation_results) == len(no_validation_chunks)
        
        # データ品質の確認
        total_rows = sum(len(chunk) for chunk in validation_results)
        if validation_errors:
            error_rate = len(validation_errors) / total_rows
            assert error_rate <= 0.05, f"Validation error rate {error_rate:.1%} exceeds 5%"
    
    def test_encoding_detection_optimization(self, tmp_path):
        """エンコーディング検出最適化テスト"""
        # 期待結果: 高速な文字エンコーディング検出
        # 性能目標: 検出時間 < 1秒/GB
        
        # 異なるエンコーディングのファイルを作成
        encodings = ['utf-8', 'shift_jis', 'euc-jp']
        test_files = []
        
        for encoding in encodings:
            csv_file = tmp_path / f"test_{encoding}.csv"
            with open(csv_file, 'w', encoding=encoding) as f:
                f.write("名前,部署,給与\n")  # 日本語ヘッダー
                for i in range(50000):
                    f.write(f"社員_{i:05d},営業部,300000\n")
            test_files.append((str(csv_file), encoding))
        
        processor = OptimizedCSVProcessor(
            auto_detect_encoding=True,
            encoding_cache=True
        )
        
        # エンコーディング検出時間の測定
        detection_times = []
        detection_results = []
        
        for file_path, expected_encoding in test_files:
            start_time = time.time()
            detected_encoding = processor.detect_file_encoding(file_path)
            detection_time = time.time() - start_time
            
            detection_times.append(detection_time)
            detection_results.append({
                'file': file_path,
                'expected': expected_encoding,
                'detected': detected_encoding,
                'time': detection_time
            })
            
            # 検出精度の確認
            assert detected_encoding == expected_encoding, f"Encoding detection failed: expected {expected_encoding}, got {detected_encoding}"
        
        # 検出速度の確認
        avg_detection_time = sum(detection_times) / len(detection_times)
        
        # ファイルサイズを確認してGB当たりの時間を計算
        file_size_gb = sum(os.path.getsize(f[0]) for f in test_files) / (1024**3)
        time_per_gb = sum(detection_times) / file_size_gb if file_size_gb > 0 else 0
        
        assert time_per_gb < 1.0, f"Encoding detection time {time_per_gb:.2f}s/GB exceeds 1 second/GB"
        
        # キャッシュ効果の確認
        if processor.encoding_cache_enabled:
            # 2回目の検出は高速であるべき
            start_time = time.time()
            cached_encoding = processor.detect_file_encoding(test_files[0][0])
            cached_time = time.time() - start_time
            
            cache_speedup = detection_results[0]['time'] / cached_time
            assert cache_speedup >= 10, f"Cache speedup {cache_speedup:.1f}x below 10x target"