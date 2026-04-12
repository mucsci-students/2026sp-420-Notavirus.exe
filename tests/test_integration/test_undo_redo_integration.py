# tests/test_integration/test_undo_redo_integration.py
import pytest
import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch


TESTING_CONFIG = "example.json"
TEST_COPY_CONFIG = "test_undo_redo.json"


@pytest.fixture
def test_config():
    shutil.copy(TESTING_CONFIG, TEST_COPY_CONFIG)
    yield TEST_COPY_CONFIG
    Path(TEST_COPY_CONFIG).unlink(missing_ok=True)
    Path(TEST_COPY_CONFIG + ".temp").unlink(missing_ok=True)
    Path(TEST_COPY_CONFIG + ".undo").unlink(missing_ok=True)


@pytest.fixture
def app_controller(test_config):
    with patch("views.schedule_gui_view._state"), \
         patch("controllers.app_controller.ui"), \
         patch("nicegui.app"):
        
        from nicegui import app
        app.storage = MagicMock()
        app.storage.user = {}
        
        # Ensure we don't mock GUIView so that views.gui_view.GUIView.controller gets correctly assigned and config_model uses the real one.
        from controllers.app_controller import SchedulerController
        ctrl = SchedulerController(test_config)
        yield ctrl


def test_manual_add_undo_redo(app_controller):
    """Test that adding an item manually allows undo and redo."""
    lab_name = "UndoRedoTestLab"
    assert lab_name not in app_controller.lab_controller.get_all_labs()
    
    # 1. Manually add lab
    success, msg = app_controller.lab_controller.add_lab(lab_name)
    assert success is True
    
    # Now temp_save should have been called and undo state recorded
    assert app_controller.undo_redo_controller.can_undo() is True
    assert app_controller.undo_redo_controller.can_redo() is False
    assert lab_name in app_controller.lab_controller.get_all_labs()
    
    # 2. Perform Undo
    app_controller.perform_undo()
    assert app_controller.undo_redo_controller.can_undo() is False
    assert app_controller.undo_redo_controller.can_redo() is True
    assert lab_name not in app_controller.lab_controller.get_all_labs()
    
    # 3. Perform Redo
    app_controller.perform_redo()
    assert app_controller.undo_redo_controller.can_undo() is True
    assert app_controller.undo_redo_controller.can_redo() is False
    assert lab_name in app_controller.lab_controller.get_all_labs()


def test_ai_add_undo_redo(app_controller):
    """Test that adding an item via AI (ChatbotController) allows undo and redo."""
    lab_name = "AITestLab"
    assert lab_name not in app_controller.lab_controller.get_all_labs()
    
    # AI controller method logic
    result = app_controller.chatbot_controller._add_lab(lab_name)
    assert "added" in result
    
    # Adding via AI triggers _trigger_save which calls GUIView.controller.temp_save()
    assert app_controller.undo_redo_controller.can_undo() is True
    assert app_controller.undo_redo_controller.can_redo() is False
    
    assert lab_name in app_controller.lab_controller.get_all_labs()
    
    # 2. Perform Undo
    app_controller.perform_undo()
    assert app_controller.undo_redo_controller.can_undo() is False
    assert app_controller.undo_redo_controller.can_redo() is True
    assert lab_name not in app_controller.lab_controller.get_all_labs()
    
    # 3. Perform Redo
    app_controller.perform_redo()
    assert app_controller.undo_redo_controller.can_undo() is True
    assert app_controller.undo_redo_controller.can_redo() is False
    assert lab_name in app_controller.lab_controller.get_all_labs()


def test_multiple_undo_redo(app_controller):
    """Test that multiple undos and redos in a row work correctly."""
    labs = ["MultiLab1", "MultiLab2", "MultiLab3"]
    
    # 1. Add three labs sequentially
    for lab in labs:
        success, msg = app_controller.lab_controller.add_lab(lab)
        assert success is True
    
    all_labs = app_controller.lab_controller.get_all_labs()
    assert all(lab in all_labs for lab in labs)
    assert len(app_controller.undo_redo_controller.undo_stack) >= 3
    
    # 2. Undo twice
    app_controller.perform_undo()
    app_controller.perform_undo()
    
    all_labs_after_undo = app_controller.lab_controller.get_all_labs()
    assert labs[0] in all_labs_after_undo
    assert labs[1] not in all_labs_after_undo
    assert labs[2] not in all_labs_after_undo
    
    # 3. Redo once
    app_controller.perform_redo()
    
    all_labs_after_redo_1 = app_controller.lab_controller.get_all_labs()
    assert labs[0] in all_labs_after_redo_1
    assert labs[1] in all_labs_after_redo_1
    assert labs[2] not in all_labs_after_redo_1
    
    # 4. Undo twice (back to empty/original state)
    app_controller.perform_undo()
    app_controller.perform_undo()
    
    all_labs_after_undo_all = app_controller.lab_controller.get_all_labs()
    assert labs[0] not in all_labs_after_undo_all
    assert labs[1] not in all_labs_after_undo_all
    assert labs[2] not in all_labs_after_undo_all
    
    # 5. Redo all the way back
    app_controller.perform_redo()
    app_controller.perform_redo()
    app_controller.perform_redo()
    
    final_labs = app_controller.lab_controller.get_all_labs()
    assert all(lab in final_labs for lab in labs)
    assert app_controller.undo_redo_controller.can_redo() is False
