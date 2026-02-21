# models/scheduler_model.py
"""
SchedulerModel - Handles schedule generation operations

This model class manages schedule generation using the Scheduler class.
"""

import scheduler
from scheduler import Scheduler


class SchedulerModel:
    """
    Model class for schedule generation operations.
    
    Attributes:
        config_model: Reference to ConfigModel for configuration access
    """
    
    def __init__(self, config_model):
        """
        Initialize SchedulerModel.
        
        Parameters:
            config_model (ConfigModel): Central configuration model
        
        Returns:
            None
        """
        self.config_model = config_model
    
    def generate_schedules(self, limit: int = None):
        """
        Generate schedules using the Scheduler.
        
        Parameters:
            limit (int | None): Maximum number of schedules to generate
        
        Returns:
            generator: Generator yielding schedule models
        """
        # Set limit if provided
        if limit is not None:
            self.config_model.config.limit = limit
        
        # Create scheduler and generate
        scheduler_gen = Scheduler(self.config_model.config)
        return scheduler_gen.get_models()
    
    def count_possible_schedules(self, max_check: int = 100) -> int:
        """
        Count how many schedules can be generated (up to max_check).
        
        Parameters:
            max_check (int): Maximum schedules to check
        
        Returns:
            int: Number of schedules found (up to max_check)
        """
        count = 0
        try:
            for _ in self.generate_schedules(limit=max_check):
                count += 1
        except Exception:
            pass
        
        return count