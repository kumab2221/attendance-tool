"""設定管理のテストモジュール"""

import os
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
import yaml

from attendance_tool.utils.config import ConfigManager, ConfigError, get_config


class TestConfigManager:
    """ConfigManagerクラスのテスト"""
    
    @pytest.fixture
    def temp_config_dir(self):
        """一時的な設定ディレクトリを作成"""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)
    
    @pytest.fixture
    def sample_work_rules(self):
        """サンプルの就業規則設定"""
        return {
            'working_hours': {
                'standard_daily_minutes': 480,
                'standard_start_time': '09:00'
            },
            'overtime': {
                'rates': {
                    'weekday_overtime': 1.25
                }
            }
        }
    
    @pytest.fixture
    def config_manager(self, temp_config_dir):
        """ConfigManagerインスタンス"""
        return ConfigManager(temp_config_dir)
    
    def test_init_with_default_config_dir(self):
        """デフォルトの設定ディレクトリでの初期化"""
        manager = ConfigManager()
        assert manager.config_dir.name == "config"
        assert manager.config_dir.exists()
    
    def test_init_with_custom_config_dir(self, temp_config_dir):
        """カスタム設定ディレクトリでの初期化"""
        manager = ConfigManager(temp_config_dir)
        assert manager.config_dir == temp_config_dir
    
    def test_load_config_success(self, config_manager, temp_config_dir, sample_work_rules):
        """設定ファイル読み込み成功"""
        # テスト用の設定ファイルを作成
        config_file = temp_config_dir / "work_rules.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_work_rules, f)
        
        # 設定を読み込み
        config = config_manager.load_config('work_rules')
        
        # 検証
        assert config == sample_work_rules
        assert 'work_rules' in config_manager._configs
    
    def test_load_config_file_not_found(self, config_manager):
        """存在しない設定ファイルの読み込み"""
        with pytest.raises(ConfigError, match="設定ファイルが見つかりません"):
            config_manager.load_config('nonexistent')
    
    def test_load_config_invalid_yaml(self, config_manager, temp_config_dir):
        """不正なYAMLファイルの読み込み"""
        # 不正なYAMLファイルを作成
        config_file = temp_config_dir / "invalid.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: content: [")
        
        with pytest.raises(ConfigError, match="YAML形式エラー"):
            config_manager.load_config('invalid')
    
    def test_load_config_empty_file(self, config_manager, temp_config_dir):
        """空の設定ファイルの読み込み"""
        # 空のファイルを作成
        config_file = temp_config_dir / "empty.yaml"
        config_file.touch()
        
        config = config_manager.load_config('empty')
        assert config == {}
    
    def test_load_config_caching(self, config_manager, temp_config_dir, sample_work_rules):
        """設定のキャッシュ機能"""
        # テスト用の設定ファイルを作成
        config_file = temp_config_dir / "cached.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_work_rules, f)
        
        # 最初の読み込み
        config1 = config_manager.load_config('cached')
        
        # ファイルを変更
        modified_config = sample_work_rules.copy()
        modified_config['working_hours']['standard_daily_minutes'] = 450
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(modified_config, f)
        
        # キャッシュから読み込み（変更されていないはず）
        config2 = config_manager.load_config('cached')
        assert config1 == config2
        assert config2['working_hours']['standard_daily_minutes'] == 480
        
        # 強制再読み込み
        config3 = config_manager.load_config('cached', reload=True)
        assert config3['working_hours']['standard_daily_minutes'] == 450
    
    @patch.dict(os.environ, {
        'ATTENDANCE_TOOL_WORK_RULES_WORKING_HOURS_STANDARD_DAILY_MINUTES': '450',
        'ATTENDANCE_TOOL_WORK_RULES_WORKING_HOURS_STANDARD_START_TIME': '08:30',
        'ATTENDANCE_TOOL_WORK_RULES_OVERTIME_RATES_WEEKDAY_OVERTIME': '1.30'
    })
    def test_env_override(self, config_manager, temp_config_dir, sample_work_rules):
        """環境変数による設定オーバーライド"""
        # テスト用の設定ファイルを作成
        config_file = temp_config_dir / "work_rules.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_work_rules, f)
        
        # 設定を読み込み
        config = config_manager.load_config('work_rules')
        
        # 環境変数による上書きを検証
        assert config['working_hours']['standard_daily_minutes'] == 450
        assert config['working_hours']['standard_start_time'] == '08:30'
        assert config['overtime']['rates']['weekday_overtime'] == 1.30
    
    def test_convert_env_value_bool(self, config_manager):
        """環境変数のbool値変換"""
        assert config_manager._convert_env_value('true') is True
        assert config_manager._convert_env_value('True') is True
        assert config_manager._convert_env_value('YES') is True
        assert config_manager._convert_env_value('1') is True
        assert config_manager._convert_env_value('on') is True
        
        assert config_manager._convert_env_value('false') is False
        assert config_manager._convert_env_value('False') is False
        assert config_manager._convert_env_value('NO') is False
        assert config_manager._convert_env_value('0') is False
        assert config_manager._convert_env_value('off') is False
    
    def test_convert_env_value_numeric(self, config_manager):
        """環境変数の数値変換"""
        assert config_manager._convert_env_value('123') == 123
        assert config_manager._convert_env_value('123.45') == 123.45
        assert config_manager._convert_env_value('-10') == -10
        assert config_manager._convert_env_value('0') == 0
    
    def test_convert_env_value_string(self, config_manager):
        """環境変数の文字列変換"""
        assert config_manager._convert_env_value('hello') == 'hello'
        assert config_manager._convert_env_value('09:00') == '09:00'
        assert config_manager._convert_env_value('') == ''
    
    def test_set_nested_value(self, config_manager):
        """ネストした値の設定"""
        config = {}
        
        # 新しいネストしたパスを設定
        config_manager._set_nested_value(config, ['a', 'b', 'c'], 'value1')
        assert config == {'a': {'b': {'c': 'value1'}}}
        
        # 既存のパスに追加
        config_manager._set_nested_value(config, ['a', 'b', 'd'], 'value2')
        assert config == {'a': {'b': {'c': 'value1', 'd': 'value2'}}}
        
        # 既存の値を上書き
        config_manager._set_nested_value(config, ['a', 'b', 'c'], 'new_value')
        assert config == {'a': {'b': {'c': 'new_value', 'd': 'value2'}}}
    
    def test_get_work_rules(self, config_manager, temp_config_dir, sample_work_rules):
        """就業規則設定の取得"""
        # テスト用の設定ファイルを作成
        config_file = temp_config_dir / "work_rules.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(sample_work_rules, f)
        
        work_rules = config_manager.get_work_rules()
        assert work_rules == sample_work_rules
    
    def test_get_environment_default(self, config_manager):
        """デフォルト実行環境の取得"""
        with patch.dict(os.environ, {}, clear=True):
            assert config_manager.get_environment() == 'development'
    
    @patch.dict(os.environ, {'ATTENDANCE_TOOL_ENV': 'production'})
    def test_get_environment_custom(self, config_manager):
        """カスタム実行環境の取得"""
        assert config_manager.get_environment() == 'production'


class TestConvenienceFunctions:
    """便利関数のテスト"""
    
    @patch('attendance_tool.utils.config.config_manager')
    def test_get_config(self, mock_config_manager):
        """get_config関数のテスト"""
        mock_config_manager.load_config.return_value = {'test': 'value'}
        
        result = get_config('test_config')
        
        mock_config_manager.load_config.assert_called_once_with('test_config')
        assert result == {'test': 'value'}