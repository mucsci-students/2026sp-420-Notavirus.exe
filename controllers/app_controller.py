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

from views.gui_view import GUIView
from views.lab_gui_view import LabGUIView   
from views.room_gui_view import RoomGUIView
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
        self.view = GUIView()
        GUIView.config_path = config_path
        GUIView.controller = self
        
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
        self.course_controller = CourseController(self.course_model, self.config_model)
        self.conflict_controller = ConflictController(self.conflict_model, self.view)
        self.lab_controller = LabController(self.lab_model, self.view)
        self.room_controller = RoomController(self.room_model, self.view)
        self.schedule_controller = ScheduleController(self.scheduler_model, self.view)

        LabGUIView._lab_controller = self.lab_controller

        from views.faculty_gui_view  import FacultyGUIView
        from views.course_gui_view   import CourseGUIView
        from views.conflict_gui_view import ConflictGUIView
        from views.room_gui_view     import RoomGUIView
        from views.schedule_gui_view import ScheduleGUIView
        from views.schedule_gui_view import _state as _schedule_state

        FacultyGUIView.faculty_model        = self.faculty_model
        FacultyGUIView.faculty_controller   = self.faculty_controller

        CourseGUIView.course_model          = self.course_model
        CourseGUIView.course_controller     = self.course_controller

        ConflictGUIView.conflict_model      = self.conflict_model
        ConflictGUIView.conflict_controller = self.conflict_controller

        LabGUIView.lab_model                = self.lab_model
        LabGUIView.lab_controller           = self.lab_controller
        LabGUIView._lab_controller          = self.lab_controller

        RoomGUIView.room_model              = self.room_model
        RoomGUIView.room_controller         = self.room_controller

        _schedule_state._scheduler_model    = self.scheduler_model
        ScheduleGUIView.schedule_controller = self.schedule_controller

        GUIView.controller = self
    
    def save_configuration(self) -> bool:
        """
        Saves the current configuration via the model.
        
        Returns:
            bool: True if save successful, False otherwise
        """
        return self.config_model.safe_save()

    def run(self):
        """
        Main application loop.
        
        Displays the GUI.
        
        Parameters:
            None
        
        Returns:
            None
        """
        print("\n" + "="*60)
        print("  🚀 GUI SERVER STARTING")
        print("="*60)
        print("  🌐 Open your browser to: http://localhost:8080")
        print("  🛑 Stop server: Press Ctrl+C in this terminal (may receive asyncio errors)")
        print("="*60 + "\n")
        ui.run(title='Scheduler', reload=False, storage_secret='scheduler_secret_key')