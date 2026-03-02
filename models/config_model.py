# models/config_model.py
"""
ConfigModel - Central configuration management

This model class manages loading, saving, and accessing the scheduler configuration.
All other models use ConfigModel to interact with the configuration file.
"""

from scheduler import load_config_from_file, CombinedConfig
from safe_save import safe_save


class ConfigModel:
    """
    Central configuration model for scheduler data.
    
    Attributes:
        config_path (str): Path to configuration JSON file
        config (CombinedConfig): Loaded configuration object
    """
    
    def __init__(self, config_path: str):
        """
        Initialize ConfigModel.
        
        Parameters:
            config_path (str): Path to configuration JSON file
        
        Returns:
            None
        """
        self.config_path = config_path
        self.config = load_config_from_file(CombinedConfig, config_path)
    
    def safe_save(self) -> bool:
        """
        Save configuration using safe_save function.
        
        Wrapper around the safe_save function that handles
        backup, validation, and atomic file writes.
        
        Parameters:
            None
        
        Returns:
            bool: True if save successful, False otherwise
        """
        return safe_save(self.config, self.config_path)
    
    def reload(self):
        """
        Reload configuration from file.
        
        Use this after saving to ensure in-memory config matches file.
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            self.config = load_config_from_file(CombinedConfig, self.config_path)
        except Exception as e:
            print(f"WARNING: reload skipped due to validation error: {e}")
        
    def get_all_courses(self):
        """
        Get all courses from configuration.
        
        Parameters:
            None
        
        Returns:
            list: List of CourseConfig objects
        """
        return self.config.config.courses
    
    def get_all_faculty(self):
        """
        Get all faculty from configuration.
        
        Parameters:
            None
        
        Returns:
            list: List of FacultyConfig objects
        """
        return self.config.config.faculty
    
    def get_all_rooms(self):
        """
        Get all rooms from configuration.
        
        Parameters:
            None
        
        Returns:
            list: List of room name strings
        """
        return self.config.config.rooms
    
    def get_all_labs(self):
        """
        Get all labs from configuration.
        
        Parameters:
            None
        
        Returns:
            list: List of lab name strings
        """
        return self.config.config.labs