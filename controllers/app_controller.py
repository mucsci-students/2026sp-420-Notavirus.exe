# controllers/app_controller.py
"""
AppController - Main application controller

This is the main controller that coordinates all feature controllers
and handles the main menu loop for the scheduler application.
"""

from models.config_model import ConfigModel
from models.faculty_model import FacultyModel
from models.course_model import CourseModel
from models.conflict_model import ConflictModel
from models.lab_model import LabModel
from models.room_model import RoomModel
from models.scheduler_model import SchedulerModel

from controllers.faculty_controller import FacultyController
from controllers.course_controller import CourseController
from controllers.conflict_controller import ConflictController
from controllers.lab_controller import LabController
from controllers.room_controller import RoomController
from controllers.schedule_controller import ScheduleController

from views.cli_view import CLIView
from views.gui_view import GUIView
from nicegui import ui


class SchedulerController:
    """
    Main application controller.
    
    Coordinates all sub-controllers and manages the main menu loop.
    
    Attributes:
        config_path (str): Path to configuration file
        config_model (ConfigModel): Central configuration model
        view (CLIView): User interface
        faculty_controller (FacultyController): Faculty operations
        course_controller (CourseController): Course operations
        conflict_controller (ConflictController): Conflict operations
        lab_controller (LabController): Lab operations
        room_controller (RoomController): Room operations
        schedule_controller (ScheduleController): Schedule operations
    """
    
    def __init__(self, config_path: str):
        """
        Initialize SchedulerController.
        
        Sets up all models, view, and sub-controllers.
        
        Parameters:
            config_path (str): Path to configuration JSON file
        
        Returns:
            None
        """
        # Initialize view
        self.view = CLIView()
        
        # Initialize config model
        self.config_path = config_path
        self.config_model = ConfigModel(config_path)
        
        # Initialize all feature models
        self.faculty_model = FacultyModel(self.config_model)
        self.course_model = CourseModel(self.config_model)
        self.conflict_model = ConflictModel(self.config_model)
        self.lab_model = LabModel(self.config_model)
        self.room_model = RoomModel(self.config_model)
        self.scheduler_model = SchedulerModel(self.config_model)
        
        # Initialize all feature controllers
        self.faculty_controller = FacultyController(self.faculty_model, self.view)
        self.course_controller = CourseController(self.course_model, self.view, self.config_model)
        self.conflict_controller = ConflictController(self.conflict_model, self.view)
        self.lab_controller = LabController(self.lab_model, self.view)
        self.room_controller = RoomController(self.room_model, self.view)
        self.schedule_controller = ScheduleController(self.scheduler_model, self.view)
    
    def run(self):
        """
        Main application loop.
        
        Displays the GUI.
        
        Parameters:
            None
        
        Returns:
            None
        """
        from views.gui_view import GUIView
        GUIView.set_controller(self)
        ui.run(title='Scheduler')