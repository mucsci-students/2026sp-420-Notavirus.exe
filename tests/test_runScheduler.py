import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the module to test
import ourScheduler as main


class TestPromptConfigFile:
    """Tests for promptConfigFile function"""
    def test_valid_config_file(self, monkeypatch):
        """Test with valid config file that exists"""
        monkeypatch.setattr('builtins.input', lambda _: 'config.json')
        monkeypatch.setattr('os.path.exists', lambda _: True)
        
        main.promptConfigFile()
        assert main.configFileName == 'config.json'
    
    def test_empty_filename_then_valid(self, monkeypatch):
        """Test empty filename followed by valid filename"""
        inputs = iter(['', 'config.json'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        monkeypatch.setattr('os.path.exists', lambda _: True)
        
        main.promptConfigFile()
        assert main.configFileName == 'config.json'
    
    def test_nonexistent_file_decline_retry(self, monkeypatch):
        """Test nonexistent file and user declines to retry"""
        inputs = iter(['nonexistent.json', 'no'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        monkeypatch.setattr('os.path.exists', lambda _: False)
        
        with pytest.raises(FileNotFoundError):
            main.promptConfigFile()


class TestSpecifyLimit:
    """Tests for specifyLimit function"""
    
    def test_valid_positive_number(self, monkeypatch):
        """Test with valid positive number"""
        monkeypatch.setattr('builtins.input', lambda _: '5')
        
        main.specifyLimit()
        assert main.scheduleLimit == 5
    
    def test_invalid_then_valid(self, monkeypatch):
        """Test invalid input followed by valid number"""
        inputs = iter(['abc', '10'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        
        main.specifyLimit()
        assert main.scheduleLimit == 10


class TestPromptSaveToFile:
    """Tests for promptSaveToFile function"""
    
    def test_save_yes(self, monkeypatch):
        """Test user chooses to save to file"""
        monkeypatch.setattr('builtins.input', lambda _: 'yes')
        
        main.promptSaveToFile()
        assert main.saveToFile is True
    
    def test_no_save_no(self, monkeypatch):
        """Test user chooses not to save"""
        monkeypatch.setattr('builtins.input', lambda _: 'no')
        
        main.promptSaveToFile()
        assert main.saveToFile is False


class TestPromptFormat:
    """Tests for promptFormat function"""
    
    def test_csv_format(self, monkeypatch):
        """Test choosing CSV format"""
        monkeypatch.setattr('builtins.input', lambda _: 'csv')
        
        result = main.promptFormat()
        assert result is True
    
    def test_json_format(self, monkeypatch):
        """Test choosing JSON format"""
        monkeypatch.setattr('builtins.input', lambda _: 'json')
        
        result = main.promptFormat()
        assert result is False


class TestPromptOutputFileName:
    """Tests for promptOutputFileName function"""
    
    def test_valid_filename_csv(self, monkeypatch):
        """Test valid filename with CSV format"""
        inputs = iter(['schedule', 'csv'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        monkeypatch.setattr('os.path.exists', lambda _: False)
        
        main.promptOutputFileName()
        assert main.outputFile == 'schedule.csv'
        assert main.formatChoice is True
    
    def test_valid_filename_json(self, monkeypatch):
        """Test valid filename with JSON format"""
        inputs = iter(['output', 'json'])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        monkeypatch.setattr('os.path.exists', lambda _: False)
        
        main.promptOutputFileName()
        assert main.outputFile == 'output.json'
        assert main.formatChoice is False