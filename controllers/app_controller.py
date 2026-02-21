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
        
        Displays menu, gets user choice, and routes to appropriate controller.
        Continues until user chooses to exit.
        
        Parameters:
            None
        
        Returns:
            None
        """
        while True:
            # Display menu
            self.view.display_main_menu()
            
            # Get user choice
            choice = self.view.get_menu_choice()
            
            # Route to appropriate controller
            try:
                if choice == '1':
                    self.faculty_controller.add_faculty()
                
                elif choice == '2':
                    self.faculty_controller.modify_faculty()
                
                elif choice == '3':
                    self.faculty_controller.delete_faculty()
                
                elif choice == '4':
                    self.course_controller.add_course()
                
                elif choice == '5':
                    self.course_controller.modify_course()
                
                elif choice == '6':
                    self.course_controller.delete_course()
                
                elif choice == '7':
                    self.conflict_controller.add_conflict()
                
                elif choice == '8':
                    self.conflict_controller.modify_conflict()
                
                elif choice == '9':
                    self.conflict_controller.delete_conflict()
                
                elif choice == '10':
                    self.lab_controller.add_lab()
                
                elif choice == '11':
                    self.lab_controller.modify_lab()
                
                elif choice == '12':
                    self.lab_controller.delete_lab()
                
                elif choice == '13':
                    self.room_controller.add_room()
                
                elif choice == '14':
                    self.room_controller.modify_room()
                
                elif choice == '15':
                    self.room_controller.delete_room()
                
                elif choice == '16':
                    self.schedule_controller.display_configuration()
                
                elif choice == '17':
                    self.schedule_controller.run_scheduler()
                
                elif choice == '18':
                    # Get number of schedules to display
                    max_schedules = self.view.get_integer_input(
                        "How many schedules to display?: ",
                        min_val=1
                    )
                    self.schedule_controller.display_schedules_csv(max_schedules)
                
                elif choice == '19':
                    self.view.display_message("Exiting scheduler. Goodbye!")
                    break
                
                else:
                    self.view.display_error("Invalid option. Please choose a number between 1 and 19.")
            
            except Exception as e:
                self.view.display_error(f"An error occurred: {e}")
                # Optionally, ask if they want to continue
                if not self.view.confirm("Would you like to continue?"):
                    break