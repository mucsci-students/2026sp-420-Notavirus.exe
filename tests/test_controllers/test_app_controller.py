import pytest
from unittest.mock import MagicMock
from controllers.app_controller import SchedulerController

def test_save_configuration(config_model):
    """
    Test that save_configuration correctly delegates to config_model.safe_save().
    """
    # Initialize the controller with our test config
    controller = SchedulerController(config_model.config_path)
    
    # Replace the actual config_model with our mocked one 
    # (or just mock its safe_save method)
    controller.config_model.safe_save = MagicMock(return_value=True)
    
    # Execute
    result = controller.save_configuration()
    
    # Assert
    assert result is True
    controller.config_model.safe_save.assert_called_once()
