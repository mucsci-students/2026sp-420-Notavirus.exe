import pytest
from unittest.mock import patch, MagicMock
from views.gui_view import GUIView

def test_export_configuration_success():
    """
    Test that export_configuration triggers download and positive notification on success.
    """
    # Mock the controller and its save_configuration method
    mock_controller = MagicMock()
    mock_controller.save_configuration.return_value = True
    mock_controller.config_path = "test_path.json"
    
    # Set the static controller attribute
    GUIView.controller = mock_controller
    
    # Mock ui.download and ui.notify
    with patch('views.gui_view.ui.download') as mock_download, \
         patch('views.gui_view.ui.notify') as mock_notify:
        
        # Execute
        GUIView.export_configuration()
        
        # Assert
        mock_controller.save_configuration.assert_called_once()
        mock_download.assert_called_once_with("test_path.json", 'scheduler_configuration.json')
        mock_notify.assert_called_once_with('Configuration exported successfully!', type='positive')

def test_export_configuration_failure():
    """
    Test that export_configuration triggers negative notification on failure.
    """
    # Mock the controller and its save_configuration method to fail
    mock_controller = MagicMock()
    mock_controller.save_configuration.return_value = False
    
    GUIView.controller = mock_controller
    
    with patch('views.gui_view.ui.download') as mock_download, \
         patch('views.gui_view.ui.notify') as mock_notify:
        
        # Execute
        GUIView.export_configuration()
        
        # Assert
        mock_controller.save_configuration.assert_called_once()
        mock_download.assert_not_called()
        mock_notify.assert_called_once_with('Error saving configuration.', type='negative')

def test_export_configuration_exception():
    """
    Test that export_configuration handles exceptions properly.
    """
    mock_controller = MagicMock()
    mock_controller.save_configuration.side_effect = Exception("Test Exception")
    
    GUIView.controller = mock_controller
    
    with patch('views.gui_view.ui.download') as mock_download, \
         patch('views.gui_view.ui.notify') as mock_notify:
        
        # Execute
        GUIView.export_configuration()
        
        # Assert
        mock_controller.save_configuration.assert_called_once()
        mock_download.assert_not_called()
        mock_notify.assert_called_once_with('Failed to export configuration: Test Exception', type='negative')
