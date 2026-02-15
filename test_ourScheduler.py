#!/usr/bin/env python3
"""
Comprehensive Unit Tests for Scheduler Runner
Tests all functions in the scheduler runner script.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, mock_open, call
from io import StringIO

# Import the module to test
# Assuming the code is in a file called scheduler_runner.py
# If it has a different name, adjust the import accordingly
import ourScheduler


class TestPromptConfigFile:
    """Tests for promptConfigFile function."""
    
    @patch('builtins.input', return_value='config.json')
    def test_prompt_config_file_basic(self, mock_input):
        """Test promptConfigFile with basic input."""
        scheduler_runner.promptConfigFile()
        assert scheduler_runner.configFileName == 'config.json'
        mock_input.assert_called_once()
    
    @patch('builtins.input', return_value='  my_config.json  ')
    def test_prompt_config_file_with_whitespace(self, mock_input):
        """Test promptConfigFile strips whitespace."""
        scheduler_runner.promptConfigFile()
        assert scheduler_runner.configFileName == 'my_config.json'
    
    @patch('builtins.input', return_value='path/to/config.json')
    def test_prompt_config_file_with_path(self, mock_input):
        """Test promptConfigFile with file path."""
        scheduler_runner.promptConfigFile()
        assert scheduler_runner.configFileName == 'path/to/config.json'


class TestSpecifyLimit:
    """Tests for specifyLimit function."""
    
    @patch('builtins.input', return_value='10')
    def test_specify_limit_valid_number(self, mock_input):
        """Test specifyLimit with valid number."""
        scheduler_runner.specifyLimit()
        assert scheduler_runner.scheduleLimit == 10
        mock_input.assert_called_once()
    
    @patch('builtins.input', return_value='1')
    def test_specify_limit_one(self, mock_input):
        """Test specifyLimit with limit of 1."""
        scheduler_runner.specifyLimit()
        assert scheduler_runner.scheduleLimit == 1
    
    @patch('builtins.input', return_value='100')
    def test_specify_limit_large_number(self, mock_input):
        """Test specifyLimit with large number."""
        scheduler_runner.specifyLimit()
        assert scheduler_runner.scheduleLimit == 100
    
    @patch('builtins.input', side_effect=['abc', 'xyz', '5'])
    @patch('builtins.print')
    def test_specify_limit_invalid_then_valid(self, mock_print, mock_input):
        """Test specifyLimit retries on invalid input."""
        scheduler_runner.specifyLimit()
        assert scheduler_runner.scheduleLimit == 5
        assert mock_input.call_count == 3
        # Should print error message twice
        assert mock_print.call_count == 2
        mock_print.assert_called_with("Not a number, try again.")
    
    @patch('builtins.input', side_effect=['', '  ', '7'])
    @patch('builtins.print')
    def test_specify_limit_empty_strings(self, mock_print, mock_input):
        """Test specifyLimit with empty strings then valid."""
        scheduler_runner.specifyLimit()
        assert scheduler_runner.scheduleLimit == 7
        assert mock_input.call_count == 3
    
    @patch('builtins.input', side_effect=['3.14', '5'])
    @patch('builtins.print')
    def test_specify_limit_float_then_valid(self, mock_print, mock_input):
        """Test specifyLimit with float then valid integer."""
        scheduler_runner.specifyLimit()
        assert scheduler_runner.scheduleLimit == 5
        assert mock_input.call_count == 2


class TestPromptFormat:
    """Tests for promptFormat function."""
    
    @patch('builtins.input', return_value='csv')
    def test_prompt_format_csv_lowercase(self, mock_input):
        """Test promptFormat returns True for 'csv'."""
        result = scheduler_runner.promptFormat()
        assert result is True
    
    @patch('builtins.input', return_value='CSV')
    def test_prompt_format_csv_uppercase(self, mock_input):
        """Test promptFormat returns True for 'CSV'."""
        result = scheduler_runner.promptFormat()
        assert result is True
    
    @patch('builtins.input', return_value='CsV')
    def test_prompt_format_csv_mixed_case(self, mock_input):
        """Test promptFormat returns True for mixed case 'CsV'."""
        result = scheduler_runner.promptFormat()
        assert result is True
    
    @patch('builtins.input', return_value='  csv  ')
    def test_prompt_format_csv_with_whitespace(self, mock_input):
        """Test promptFormat strips whitespace."""
        result = scheduler_runner.promptFormat()
        assert result is True
    
    @patch('builtins.input', return_value='json')
    def test_prompt_format_json_lowercase(self, mock_input):
        """Test promptFormat returns False for 'json'."""
        result = scheduler_runner.promptFormat()
        assert result is False
    
    @patch('builtins.input', return_value='JSON')
    def test_prompt_format_json_uppercase(self, mock_input):
        """Test promptFormat returns False for 'JSON'."""
        result = scheduler_runner.promptFormat()
        assert result is False
    
    @patch('builtins.input', return_value='xml')
    def test_prompt_format_other_format(self, mock_input):
        """Test promptFormat returns False for non-csv format."""
        result = scheduler_runner.promptFormat()
        assert result is False
    
    @patch('builtins.input', return_value='')
    def test_prompt_format_empty_string(self, mock_input):
        """Test promptFormat returns False for empty string."""
        result = scheduler_runner.promptFormat()
        assert result is False


class TestPromptOutputFileName:
    """Tests for promptOutputFileName function."""
    
    @patch('scheduler_runner.promptFormat', return_value=True)
    @patch('builtins.input', return_value='schedules')
    def test_prompt_output_csv(self, mock_input, mock_format):
        """Test promptOutputFileName for CSV format."""
        scheduler_runner.promptOutputFileName()
        assert scheduler_runner.outputFile == 'schedules.csv'
        assert scheduler_runner.formatChoice is True
    
    @patch('scheduler_runner.promptFormat', return_value=False)
    @patch('builtins.input', return_value='schedules')
    def test_prompt_output_json(self, mock_input, mock_format):
        """Test promptOutputFileName for JSON format."""
        scheduler_runner.promptOutputFileName()
        assert scheduler_runner.outputFile == 'schedules.json'
        assert scheduler_runner.formatChoice is False
    
    @patch('scheduler_runner.promptFormat', return_value=True)
    @patch('builtins.input', return_value='  output  ')
    def test_prompt_output_with_whitespace(self, mock_input, mock_format):
        """Test promptOutputFileName strips whitespace."""
        scheduler_runner.promptOutputFileName()
        assert scheduler_runner.outputFile == 'output.csv'
    
    @patch('scheduler_runner.promptFormat', return_value=True)
    @patch('builtins.input', return_value='path/to/output')
    def test_prompt_output_with_path(self, mock_input, mock_format):
        """Test promptOutputFileName with path."""
        scheduler_runner.promptOutputFileName()
        assert scheduler_runner.outputFile == 'path/to/output.csv'
    
    @patch('scheduler_runner.promptFormat', return_value=False)
    @patch('builtins.input', return_value='results')
    def test_prompt_output_sets_format_choice(self, mock_input, mock_format):
        """Test promptOutputFileName sets formatChoice global."""
        scheduler_runner.promptOutputFileName()
        assert scheduler_runner.formatChoice is False
        assert scheduler_runner.outputFile == 'results.json'


class TestGenerateSchedule:
    """Tests for generateSchedule function."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock CombinedConfig."""
        config = MagicMock()
        config.limit = 10
        return config
    
    @pytest.fixture
    def mock_course_csv(self):
        """Create a mock course with as_csv method."""
        course = MagicMock()
        course.as_csv.return_value = "CS101,Prof. Smith,Room1,Mon,9:00"
        return course
    
    @pytest.fixture
    def mock_course_json(self):
        """Create a mock course with model_dump_json method."""
        course = MagicMock()
        course.model_dump_json.return_value = '{"course_id": "CS101", "faculty": "Prof. Smith"}'
        return course
    
    @patch('scheduler_runner.scheduler.Scheduler')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_generate_schedule_csv_single(self, mock_print, mock_file, mock_scheduler_class, mock_config, mock_course_csv):
        """Test generateSchedule with CSV format and single schedule."""
        scheduler_runner.formatChoice = True
        
        # Setup mock scheduler
        mock_scheduler = MagicMock()
        mock_scheduler.get_models.return_value = iter([[mock_course_csv]])
        mock_scheduler_class.return_value = mock_scheduler
        
        # Call function
        scheduler_runner.generateSchedule(mock_config, 'output.csv')
        
        # Verify file operations
        mock_file.assert_called_once_with('output.csv', 'w+', encoding='utf-8')
        handle = mock_file()
        
        # Should write course CSV and newline
        expected_calls = [
            call('CS101,Prof. Smith,Room1,Mon,9:00\n'),
            call('\n')
        ]
        handle.write.assert_has_calls(expected_calls)
        
        # Should print course and newline
        assert mock_print.call_count == 2
    
    @patch('scheduler_runner.scheduler.Scheduler')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_generate_schedule_json_single(self, mock_print, mock_file, mock_scheduler_class, mock_config, mock_course_json):
        """Test generateSchedule with JSON format and single schedule."""
        scheduler_runner.formatChoice = False
        
        # Setup mock scheduler
        mock_scheduler = MagicMock()
        mock_scheduler.get_models.return_value = iter([[mock_course_json]])
        mock_scheduler_class.return_value = mock_scheduler
        
        # Call function
        scheduler_runner.generateSchedule(mock_config, 'output.json')
        
        # Verify file operations
        mock_file.assert_called_once_with('output.json', 'w+', encoding='utf-8')
        handle = mock_file()
        
        # Should write course JSON and newline
        expected_calls = [
            call('{"course_id": "CS101", "faculty": "Prof. Smith"}\n'),
            call('\n')
        ]
        handle.write.assert_has_calls(expected_calls)
    
    @patch('scheduler_runner.scheduler.Scheduler')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_generate_schedule_csv_multiple_courses(self, mock_print, mock_file, mock_scheduler_class, mock_config):
        """Test generateSchedule with multiple courses in one schedule."""
        scheduler_runner.formatChoice = True
        
        # Create multiple courses
        course1 = MagicMock()
        course1.as_csv.return_value = "CS101,Prof. Smith,Room1,Mon,9:00"
        course2 = MagicMock()
        course2.as_csv.return_value = "CS102,Prof. Jones,Room2,Tue,10:00"
        
        # Setup mock scheduler
        mock_scheduler = MagicMock()
        mock_scheduler.get_models.return_value = iter([[course1, course2]])
        mock_scheduler_class.return_value = mock_scheduler
        
        # Call function
        scheduler_runner.generateSchedule(mock_config, 'output.csv')
        
        handle = mock_file()
        
        # Should write both courses
        expected_calls = [
            call('CS101,Prof. Smith,Room1,Mon,9:00\n'),
            call('CS102,Prof. Jones,Room2,Tue,10:00\n'),
            call('\n')
        ]
        handle.write.assert_has_calls(expected_calls)
    
    @patch('scheduler_runner.scheduler.Scheduler')
    @patch('builtins.open', new_callable=mock_open)
    @patch('builtins.print')
    def test_generate_schedule_multiple_models(self, mock_print, mock_file, mock_scheduler_class, mock_config):
        """Test generateSchedule with multiple schedules."""
        scheduler_runner.formatChoice = True
        
        # Create courses for different schedules
        course1 = MagicMock()
        course1.as_csv.return_value = "CS101,Prof. Smith,Room1,Mon,9:00"
        course2 = MagicMock()
        course2.as_csv.return_value = "CS102,Prof. Jones,Room2,Tue,10:00"
        
        # Setup mock scheduler with two models
        mock_scheduler = MagicMock()
        mock_scheduler.get_models.return_value = iter([[course1], [course2]])
        mock_scheduler_class.return_value = mock_scheduler
        
        # Call function
        scheduler_runner.generateSchedule(mock_config, 'output.csv')
        
        handle = mock_file()
        
        # Should write both schedules with separating newlines
        expected_calls = [
            call('CS101,Prof. Smith,Room1,Mon,9:00\n'),
            call('\n'),  # End of first schedule
            call('CS102,Prof. Jones,Room2,Tue,10:00\n'),
            call('\n')   # End of second schedule
        ]
        handle.write.assert_has_calls(expected_calls)
    
    @patch('scheduler_runner.scheduler.Scheduler')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_schedule_empty_model(self, mock_file, mock_scheduler_class, mock_config):
        """Test generateSchedule with empty schedule."""
        scheduler_runner.formatChoice = True
        
        # Setup mock scheduler with empty model
        mock_scheduler = MagicMock()
        mock_scheduler.get_models.return_value = iter([[]])
        mock_scheduler_class.return_value = mock_scheduler
        
        # Call function
        scheduler_runner.generateSchedule(mock_config, 'output.csv')
        
        handle = mock_file()
        
        # Should only write the separator newline
        handle.write.assert_called_once_with('\n')
    
    @patch('scheduler_runner.scheduler.Scheduler')
    @patch('builtins.open', new_callable=mock_open)
    def test_generate_schedule_file_encoding(self, mock_file, mock_scheduler_class, mock_config):
        """Test generateSchedule uses UTF-8 encoding."""
        scheduler_runner.formatChoice = True
        
        mock_scheduler = MagicMock()
        mock_scheduler.get_models.return_value = iter([])
        mock_scheduler_class.return_value = mock_scheduler
        
        scheduler_runner.generateSchedule(mock_config, 'output.csv')
        
        # Verify encoding is UTF-8
        mock_file.assert_called_once_with('output.csv', 'w+', encoding='utf-8')


class TestRunScheduler:
    """Tests for runScheduler function."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock CombinedConfig."""
        config = MagicMock()
        config.limit = 5
        return config
    
    @patch('scheduler_runner.generateSchedule')
    @patch('scheduler_runner.promptOutputFileName')
    @patch('scheduler_runner.specifyLimit')
    def test_run_scheduler_basic(self, mock_limit, mock_output, mock_generate, mock_config):
        """Test runScheduler calls all required functions."""
        scheduler_runner.scheduleLimit = 10
        scheduler_runner.outputFile = 'test.csv'
        
        scheduler_runner.runScheduler(mock_config)
        
        # Verify function calls
        mock_limit.assert_called_once()
        mock_output.assert_called_once()
        mock_generate.assert_called_once_with(mock_config, 'test.csv')
    
    @patch('scheduler_runner.generateSchedule')
    @patch('scheduler_runner.promptOutputFileName')
    @patch('scheduler_runner.specifyLimit')
    def test_run_scheduler_sets_limit(self, mock_limit, mock_output, mock_generate, mock_config):
        """Test runScheduler sets config limit."""
        scheduler_runner.scheduleLimit = 15
        scheduler_runner.outputFile = 'test.csv'
        
        scheduler_runner.runScheduler(mock_config)
        
        # Verify config limit was set
        assert mock_config.limit == 15
    
    @patch('scheduler_runner.generateSchedule')
    @patch('scheduler_runner.promptOutputFileName')
    @patch('scheduler_runner.specifyLimit')
    def test_run_scheduler_function_order(self, mock_limit, mock_output, mock_generate, mock_config):
        """Test runScheduler calls functions in correct order."""
        scheduler_runner.scheduleLimit = 5
        scheduler_runner.outputFile = 'test.csv'
        
        # Track call order
        call_order = []
        mock_limit.side_effect = lambda: call_order.append('limit')
        mock_output.side_effect = lambda: call_order.append('output')
        mock_generate.side_effect = lambda c, o: call_order.append('generate')
        
        scheduler_runner.runScheduler(mock_config)
        
        # Verify order
        assert call_order == ['limit', 'output', 'generate']


class TestMain:
    """Tests for main function."""
    
    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration."""
        return {
            "config": {
                "rooms": ["Room1"],
                "labs": [],
                "courses": [],
                "faculty": []
            },
            "time_slot_config": {
                "times": {},
                "classes": [],
                "max_time_gap": 30,
                "min_time_overlap": 45
            },
            "limit": 10,
            "optimizer_flags": []
        }
    
    @pytest.fixture
    def temp_config_file(self, sample_config):
        """Create a temporary config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_config, f)
            temp_path = f.name
        
        yield temp_path
        
        # Cleanup
        Path(temp_path).unlink(missing_ok=True)
    
    @patch('scheduler_runner.runScheduler')
    @patch('scheduler_runner.scheduler.load_config_from_file')
    @patch('scheduler_runner.promptConfigFile')
    @patch('builtins.print')
    def test_main_valid_file(self, mock_print, mock_prompt, mock_load, mock_run, temp_config_file):
        """Test main with valid config file."""
        scheduler_runner.configFileName = temp_config_file
        mock_config = MagicMock()
        mock_load.return_value = mock_config
        
        scheduler_runner.main()
        
        # Verify functions were called
        mock_prompt.assert_called_once()
        mock_load.assert_called_once()
        mock_run.assert_called_once_with(mock_config)
        
        # Verify success message was printed
        assert any('Using config file' in str(call) for call in mock_print.call_args_list)
    
    @patch('scheduler_runner.runScheduler')
    @patch('scheduler_runner.promptConfigFile')
    @patch('builtins.print')
    def test_main_file_not_found(self, mock_print, mock_prompt, mock_run):
        """Test main with non-existent file."""
        scheduler_runner.configFileName = 'nonexistent_file.json'
        
        scheduler_runner.main()
        
        # Should not call runScheduler
        mock_run.assert_not_called()
        
        # Should print error message
        mock_print.assert_called_once()
        assert 'Error' in str(mock_print.call_args)
        assert 'does not exist' in str(mock_print.call_args)
    
    @patch('scheduler_runner.runScheduler')
    @patch('scheduler_runner.scheduler.load_config_from_file')
    @patch('scheduler_runner.promptConfigFile')
    @patch('os.path.isfile', return_value=True)
    def test_main_checks_file_existence(self, mock_isfile, mock_prompt, mock_load, mock_run):
        """Test main checks if file exists."""
        scheduler_runner.configFileName = 'config.json'
        mock_config = MagicMock()
        mock_load.return_value = mock_config
        
        scheduler_runner.main()
        
        # Verify file existence was checked
        mock_isfile.assert_called_once_with('config.json')


class TestGlobalVariables:
    """Tests for global variable initialization."""
    
    def test_format_choice_default(self):
        """Test formatChoice initial value."""
        assert hasattr(scheduler_runner, 'formatChoice')
        assert isinstance(scheduler_runner.formatChoice, bool)
    
    def test_output_file_default(self):
        """Test outputFile initial value."""
        assert hasattr(scheduler_runner, 'outputFile')
        assert isinstance(scheduler_runner.outputFile, str)
    
    def test_schedule_limit_default(self):
        """Test scheduleLimit initial value."""
        assert hasattr(scheduler_runner, 'scheduleLimit')
        assert isinstance(scheduler_runner.scheduleLimit, int)
    
    def test_config_file_name_default(self):
        """Test configFileName initial value."""
        assert hasattr(scheduler_runner, 'configFileName')
        assert isinstance(scheduler_runner.configFileName, str)


class TestIntegration:
    """Integration tests for complete workflow."""
    
    @pytest.fixture
    def sample_config(self):
        """Create a sample configuration."""
        return {
            "config": {
                "rooms": ["Room1"],
                "labs": [],
                "courses": [],
                "faculty": []
            },
            "time_slot_config": {
                "times": {},
                "classes": [],
                "max_time_gap": 30,
                "min_time_overlap": 45
            },
            "limit": 10,
            "optimizer_flags": []
        }
    
    @patch('scheduler_runner.scheduler.Scheduler')
    @patch('scheduler_runner.scheduler.load_config_from_file')
    @patch('builtins.input')
    @patch('builtins.print')
    def test_full_workflow_csv(self, mock_print, mock_input, mock_load, mock_scheduler_class, sample_config, tmp_path):
        """Test complete workflow from start to finish with CSV output."""
        # Setup config file
        config_file = tmp_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(sample_config, f)
        
        output_file = tmp_path / "output.csv"
        
        # Setup input sequence
        mock_input.side_effect = [
            str(config_file),  # Config file name
            '3',               # Schedule limit
            'output',          # Output file name
            'csv'              # Format choice
        ]
        
        # Setup mock config
        mock_config = MagicMock()
        mock_config.limit = 10
        mock_load.return_value = mock_config
        
        # Setup mock scheduler
        mock_course = MagicMock()
        mock_course.as_csv.return_value = "CS101,Prof. Smith,Room1,Mon,9:00"
        mock_scheduler = MagicMock()
        mock_scheduler.get_models.return_value = iter([[mock_course]])
        mock_scheduler_class.return_value = mock_scheduler
        
        # Temporarily change outputFile to use tmp_path
        scheduler_runner.outputFile = str(output_file)
        scheduler_runner.formatChoice = True
        
        # Run main
        scheduler_runner.main()
        
        # Verify config was loaded
        assert mock_config.limit == 3
        
        # Verify scheduler was created
        mock_scheduler_class.assert_called_once_with(mock_config)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
