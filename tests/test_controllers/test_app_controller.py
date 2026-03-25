# tests/test_controllers/test_app_controller.py
"""
Tests for SchedulerController (app_controller.py).
"""

import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

from models.config_model import ConfigModel

TESTING_CONFIG    = "example.json"
TEST_COPY_CONFIG  = "test_copy.json"


@pytest.fixture
def test_config():
    shutil.copy(TESTING_CONFIG, TEST_COPY_CONFIG)
    yield TEST_COPY_CONFIG
    Path(TEST_COPY_CONFIG).unlink(missing_ok=True)


@pytest.fixture
def config_model(test_config):
    return ConfigModel(test_config)


@pytest.fixture
def controller(test_config):
    """
    Create a SchedulerController with GUIView patched out so NiceGUI
    never tries to start a server during tests.
    """
    with patch('controllers.app_controller.GUIView') as MockView:
        MockView.return_value = MagicMock()
        from controllers.app_controller import SchedulerController
        ctrl = SchedulerController(test_config)
    return ctrl


# ================================================================
# TESTS: Instantiation
# ================================================================

def test_controller_instantiation(controller):
    """SchedulerController should instantiate without error."""
    assert controller is not None


def test_controller_instantiation_no_config():
    """SchedulerController should start in unloaded state when given None."""
    with patch('controllers.app_controller.GUIView'):
        from controllers.app_controller import SchedulerController
        ctrl = SchedulerController(None)
    assert ctrl.config_model is None
    assert ctrl.faculty_controller is None


def test_controller_has_sub_controllers(controller):
    """All sub-controllers should be initialized when a config is loaded."""
    assert controller.faculty_controller  is not None
    assert controller.course_controller   is not None
    assert controller.conflict_controller is not None
    assert controller.lab_controller      is not None
    assert controller.room_controller     is not None
    assert controller.schedule_controller is not None


# ================================================================
# TESTS: save_configuration
# ================================================================

def test_save_configuration_delegates_to_model(controller):
    """save_configuration() should call config_model.safe_save()."""
    controller.config_model.safe_save = MagicMock(return_value=True)

    result = controller.save_configuration()

    assert result is True
    controller.config_model.safe_save.assert_called_once()


def test_save_configuration_returns_false_when_no_config():
    """save_configuration() should return False when no config is loaded."""
    with patch('controllers.app_controller.GUIView'):
        from controllers.app_controller import SchedulerController
        ctrl = SchedulerController(None)
    assert ctrl.save_configuration() is False


# ================================================================
# TESTS: load_config
# ================================================================

def test_load_config_success(controller, test_config):
    """load_config() should return (True, message) on a valid path."""
    success, message = controller.load_config(test_config)
    assert success is True
    assert test_config in message


def test_load_config_bad_path(controller):
    """load_config() should return (False, message) on an invalid path."""
    success, message = controller.load_config("nonexistent_file.json")
    assert success is False
    assert len(message) > 0


# ================================================================
# TESTS: temp_save and save_to_config
# ================================================================

def test_temp_save_delegates_to_model(controller):
    """temp_save() should call config_model.save_feature('temp', feature)."""
    controller.config_model.save_feature = MagicMock(return_value=True)

    result = controller.temp_save('faculty')

    assert result is True
    controller.config_model.save_feature.assert_called_once_with('temp', 'faculty')


def test_save_to_config_delegates_to_model(controller):
    """save_to_config() should call config_model.save_feature('config', feature)."""
    controller.config_model.save_feature = MagicMock(return_value=True)

    result = controller.save_to_config('courses')

    assert result is True
    controller.config_model.save_feature.assert_called_once_with('config', 'courses')


def test_temp_save_returns_false_when_no_config():
    """temp_save() should return False when no config is loaded."""
    with patch('controllers.app_controller.GUIView'):
        from controllers.app_controller import SchedulerController
        ctrl = SchedulerController(None)
    assert ctrl.temp_save() is False


def test_save_to_config_returns_false_when_no_config():
    """save_to_config() should return False when no config is loaded."""
    with patch('controllers.app_controller.GUIView'):
        from controllers.app_controller import SchedulerController
        ctrl = SchedulerController(None)
    assert ctrl.save_to_config() is False


# ================================================================
# TESTS: has_config
# ================================================================

def test_has_config_true_when_loaded(controller):
    assert controller.has_config() is True


def test_has_config_false_when_not_loaded():
    with patch('controllers.app_controller.GUIView'):
        from controllers.app_controller import SchedulerController
        ctrl = SchedulerController(None)
    assert ctrl.has_config() is False


# ================================================================
# TESTS: get_schedule_limit
# ================================================================

def test_get_schedule_limit_returns_int(controller):
    """get_schedule_limit() should return an integer."""
    limit = controller.get_schedule_limit()
    assert isinstance(limit, int)
    assert limit > 0


def test_get_schedule_limit_returns_100_when_no_config():
    """get_schedule_limit() should fall back to 100 when no config loaded."""
    with patch('controllers.app_controller.GUIView'):
        from controllers.app_controller import SchedulerController
        ctrl = SchedulerController(None)
    assert ctrl.get_schedule_limit() == 100