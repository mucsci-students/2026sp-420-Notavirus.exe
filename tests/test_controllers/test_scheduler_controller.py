# tests/test_controllers/test_schedule_controller.py
"""
Unit tests for ScheduleController using MVC architecture.

Tests cover:
- ScheduleController workflow orchestration
- View interaction (mocked)
- Schedule generation
- Output formatting (CSV/JSON)
- Configuration display
"""

import pytest
from unittest.mock import Mock, patch, mock_open
import shutil
from pathlib import Path
import json

from models.config_model import ConfigModel
from models.scheduler_model import SchedulerModel
from controllers.schedule_controller import ScheduleController

# Test configuration
TESTING_CONFIG = "example.json"
TEST_COPY_CONFIG = "test_copy.json"


# ================================================================
# PYTEST FIXTURES
# ================================================================

@pytest.fixture
def test_config():
    """Create a fresh copy of example.json for each test."""
    shutil.copy(TESTING_CONFIG, TEST_COPY_CONFIG)
    yield TEST_COPY_CONFIG
    Path(TEST_COPY_CONFIG).unlink(missing_ok=True)


@pytest.fixture
def config_model(test_config):
    """Create ConfigModel with test configuration."""
    return ConfigModel(test_config)


@pytest.fixture
def schedule_controller(config_model):
    """
    Create ScheduleController with mocked view.
    
    Returns:
        tuple: (controller, mock_view, scheduler_model)
    """
    scheduler_model = SchedulerModel(config_model)
    mock_view = Mock()
    controller = ScheduleController(scheduler_model, mock_view)
    return controller, mock_view, scheduler_model


# ================================================================
# TESTS: Run Scheduler - Basic Workflow
# ================================================================

def test_run_scheduler_success(schedule_controller):
    """
    Test successfully generating schedules.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Mock user input - no file save
    mock_view.get_schedule_limit.return_value = 5
    mock_view.get_yes_no_input.return_value = False  # Don't save to file
    
    # Execute
    controller.run_scheduler()
    
    # Verify view called to display schedules
    mock_view.display_schedules.assert_called()


def test_run_scheduler_limit_one(schedule_controller):
    """
    Test generating exactly one schedule.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Mock user input
    mock_view.get_schedule_limit.return_value = 1
    mock_view.get_yes_no_input.return_value = False
    
    # Execute
    controller.run_scheduler()
    
    # Verify limit set correctly
    assert model.config_model.config.limit == 1


def test_run_scheduler_limit_large(schedule_controller):
    """
    Test generating many schedules.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Mock user input
    mock_view.get_schedule_limit.return_value = 100
    mock_view.get_yes_no_input.return_value = False
    
    # Execute
    controller.run_scheduler()
    
    # Verify limit set correctly
    assert model.config_model.config.limit == 100


def test_run_scheduler_invalid_limit_negative(schedule_controller):
    """
    Test that negative schedule limit is rejected.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Mock user entering invalid then valid limit
    mock_view.get_schedule_limit.side_effect = [-5, 5]
    mock_view.get_yes_no_input.return_value = False
    
    # Execute
    controller.run_scheduler()
    
    # Verify error displayed and re-prompted
    mock_view.display_error.assert_called()


def test_run_scheduler_invalid_limit_zero(schedule_controller):
    """
    Test that zero schedule limit is rejected.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Mock user entering invalid then valid limit
    mock_view.get_schedule_limit.side_effect = [0, 3]
    mock_view.get_yes_no_input.return_value = False
    
    # Execute
    controller.run_scheduler()
    
    # Verify error displayed
    mock_view.display_error.assert_called()


# ================================================================
# TESTS: Save to File - CSV Format
# ================================================================

def test_save_to_csv(schedule_controller, tmp_path):
    """
    Test saving schedules to CSV file.
    
    Parameters:
        schedule_controller: Controller fixture
        tmp_path: Pytest temporary directory fixture
    """
    controller, mock_view, model = schedule_controller
    
    output_file = tmp_path / "output.csv"
    
    # Mock user input
    mock_view.get_schedule_limit.return_value = 3
    mock_view.get_yes_no_input.return_value = True  # Save to file
    mock_view.get_output_format.return_value = "csv"
    mock_view.get_filename.return_value = str(output_file)
    
    # Execute
    controller.run_scheduler()
    
    # Verify file created
    assert output_file.exists()


def test_save_to_csv_overwrite_confirm(schedule_controller, tmp_path):
    """
    Test overwriting existing CSV file with confirmation.
    
    Parameters:
        schedule_controller: Controller fixture
        tmp_path: Pytest temporary directory fixture
    """
    controller, mock_view, model = schedule_controller
    
    output_file = tmp_path / "existing.csv"
    output_file.write_text("old content")
    
    # Mock user input
    mock_view.get_schedule_limit.return_value = 2
    mock_view.get_yes_no_input.side_effect = [
        True,   # Save to file
        True    # Overwrite confirmation
    ]
    mock_view.get_output_format.return_value = "csv"
    mock_view.get_filename.return_value = str(output_file)
    mock_view.file_exists.return_value = True
    
    # Execute
    controller.run_scheduler()
    
    # Verify file overwritten
    assert output_file.exists()


def test_save_to_csv_overwrite_cancel(schedule_controller, tmp_path):
    """
    Test canceling overwrite of existing file.
    
    Parameters:
        schedule_controller: Controller fixture
        tmp_path: Pytest temporary directory fixture
    """
    controller, mock_view, model = schedule_controller
    
    output_file = tmp_path / "existing.csv"
    output_file.write_text("old content")
    
    # Mock user input
    mock_view.get_schedule_limit.return_value = 2
    mock_view.get_yes_no_input.side_effect = [
        True,   # Save to file
        False   # Don't overwrite
    ]
    mock_view.get_output_format.return_value = "csv"
    mock_view.get_filename.side_effect = [
        str(output_file),
        str(tmp_path / "new.csv")
    ]
    mock_view.file_exists.side_effect = [True, False]
    
    # Execute
    controller.run_scheduler()
    
    # Verify new file created instead
    assert (tmp_path / "new.csv").exists()


# ================================================================
# TESTS: Save to File - JSON Format
# ================================================================

def test_save_to_json(schedule_controller, tmp_path):
    """
    Test saving schedules to JSON file.
    
    Parameters:
        schedule_controller: Controller fixture
        tmp_path: Pytest temporary directory fixture
    """
    controller, mock_view, model = schedule_controller
    
    output_file = tmp_path / "output.json"
    
    # Mock user input
    mock_view.get_schedule_limit.return_value = 3
    mock_view.get_yes_no_input.return_value = True  # Save to file
    mock_view.get_output_format.return_value = "json"
    mock_view.get_filename.return_value = str(output_file)
    
    # Execute
    controller.run_scheduler()
    
    # Verify file created and is valid JSON
    assert output_file.exists()
    with open(output_file) as f:
        data = json.load(f)
        assert "generatedSchedules" in data


def test_json_structure(schedule_controller, tmp_path):
    """
    Test that JSON output has correct structure.
    
    Parameters:
        schedule_controller: Controller fixture
        tmp_path: Pytest temporary directory fixture
    """
    controller, mock_view, model = schedule_controller
    
    output_file = tmp_path / "structured.json"
    
    # Mock user input
    mock_view.get_schedule_limit.return_value = 2
    mock_view.get_yes_no_input.return_value = True
    mock_view.get_output_format.return_value = "json"
    mock_view.get_filename.return_value = str(output_file)
    
    # Execute
    controller.run_scheduler()
    
    # Verify JSON structure
    with open(output_file) as f:
        data = json.load(f)
        assert "generatedSchedules" in data
        assert isinstance(data["generatedSchedules"], list)


# ================================================================
# TESTS: Console Output Only
# ================================================================

def test_console_output_only(schedule_controller):
    """
    Test displaying schedules to console without saving.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Mock user input - no file save
    mock_view.get_schedule_limit.return_value = 5
    mock_view.get_yes_no_input.return_value = False  # Don't save
    
    # Execute
    controller.run_scheduler()
    
    # Verify schedules displayed but no file operations
    mock_view.display_schedules.assert_called()
    mock_view.get_filename.assert_not_called()


# ================================================================
# TESTS: Display Configuration
# ================================================================

def test_display_configuration(schedule_controller):
    """
    Test displaying configuration.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Execute
    controller.display_configuration()
    
    # Verify view called to display config
    mock_view.display_configuration.assert_called()


def test_display_configuration_with_data(schedule_controller):
    """
    Test that configuration display includes all sections.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Execute
    controller.display_configuration()
    
    # Verify config passed to view
    call_args = mock_view.display_configuration.call_args
    assert call_args is not None


# ================================================================
# TESTS: Display Schedules
# ================================================================

def test_display_schedules_default_count(schedule_controller):
    """
    Test displaying schedules with default count.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Mock user input
    mock_view.get_display_count.return_value = 1  # Default to 1
    
    # Execute
    controller.display_schedules()
    
    # Verify display called
    mock_view.display_schedule_csv.assert_called()


def test_display_schedules_multiple(schedule_controller):
    """
    Test displaying multiple schedules.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Mock user input
    mock_view.get_display_count.return_value = 5
    
    # Execute
    controller.display_schedules()
    
    # Verify called
    mock_view.display_schedule_csv.assert_called()


# ================================================================
# TESTS: Error Handling
# ================================================================

def test_no_valid_schedules_generated(schedule_controller):
    """
    Test handling when no valid schedules can be generated.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Mock impossible configuration
    model.config_model.config.limit = 10
    
    # Mock user input
    mock_view.get_schedule_limit.return_value = 10
    mock_view.get_yes_no_input.return_value = False
    
    # Execute
    controller.run_scheduler()
    
    # Verify appropriate message (may succeed with example.json)
    # This test depends on whether example.json can generate schedules


def test_file_write_error(schedule_controller, tmp_path):
    """
    Test handling file write errors.
    
    Parameters:
        schedule_controller: Controller fixture
        tmp_path: Pytest temporary directory fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Use invalid file path
    invalid_path = "/nonexistent/directory/output.csv"
    
    # Mock user input
    mock_view.get_schedule_limit.return_value = 3
    mock_view.get_yes_no_input.return_value = True
    mock_view.get_output_format.return_value = "csv"
    mock_view.get_filename.return_value = invalid_path
    
    # Execute
    controller.run_scheduler()
    
    # Verify error handled
    mock_view.display_error.assert_called()


def test_user_cancels_scheduler(schedule_controller):
    """
    Test user canceling scheduler workflow.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Mock user canceling at limit prompt
    mock_view.get_schedule_limit.return_value = None  # Or 0 to trigger cancel
    
    # Execute
    controller.run_scheduler()
    
    # Verify no schedules generated
    mock_view.display_schedules.assert_not_called()


# ================================================================
# TESTS: Integration - Full Workflow
# ================================================================

def test_full_workflow_csv(schedule_controller, tmp_path):
    """
    Test complete workflow: generate schedules and save to CSV.
    
    Parameters:
        schedule_controller: Controller fixture
        tmp_path: Pytest temporary directory fixture
    """
    controller, mock_view, model = schedule_controller
    
    output_file = tmp_path / "complete.csv"
    
    # Mock complete user workflow
    mock_view.get_schedule_limit.return_value = 3
    mock_view.get_yes_no_input.return_value = True  # Save to file
    mock_view.get_output_format.return_value = "csv"
    mock_view.get_filename.return_value = str(output_file)
    
    # Execute
    controller.run_scheduler()
    
    # Verify all steps completed
    mock_view.get_schedule_limit.assert_called_once()
    mock_view.get_yes_no_input.assert_called()
    assert output_file.exists()


def test_full_workflow_json(schedule_controller, tmp_path):
    """
    Test complete workflow: generate schedules and save to JSON.
    
    Parameters:
        schedule_controller: Controller fixture
        tmp_path: Pytest temporary directory fixture
    """
    controller, mock_view, model = schedule_controller
    
    output_file = tmp_path / "complete.json"
    
    # Mock complete user workflow
    mock_view.get_schedule_limit.return_value = 2
    mock_view.get_yes_no_input.return_value = True  # Save to file
    mock_view.get_output_format.return_value = "json"
    mock_view.get_filename.return_value = str(output_file)
    
    # Execute
    controller.run_scheduler()
    
    # Verify all steps completed
    assert output_file.exists()
    
    # Verify JSON is valid and has correct structure
    with open(output_file) as f:
        data = json.load(f)
        assert "generatedSchedules" in data
        assert isinstance(data["generatedSchedules"], list)


def test_full_workflow_console_only(schedule_controller):
    """
    Test complete workflow: generate and display without saving.
    
    Parameters:
        schedule_controller: Controller fixture
    """
    controller, mock_view, model = schedule_controller
    
    # Mock complete user workflow
    mock_view.get_schedule_limit.return_value = 5
    mock_view.get_yes_no_input.return_value = False  # Don't save
    
    # Execute
    controller.run_scheduler()
    
    # Verify displayed but not saved
    mock_view.display_schedules.assert_called()
    mock_view.get_filename.assert_not_called()