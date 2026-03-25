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
from nicegui import ui


class SchedulerController:
    """
    Main application controller.

    Coordinates all sub-controllers and manages the main menu loop.

    The Controller owns all Models and sub-Controllers. Views never receive
    direct references to Models — they communicate exclusively through
    Controller methods.

    Attributes:
        config_path (str): Path to configuration file
        config_model (ConfigModel): Central configuration model
        view (GUIView): User interface
        faculty_controller (FacultyController): Faculty operations
        course_controller (CourseController): Course operations
        conflict_controller (ConflictController): Conflict operations
        lab_controller (LabController): Lab operations
        room_controller (RoomController): Room operations
        schedule_controller (ScheduleController): Schedule operations
    """

    def __init__(self, config_path: str | None):
        """
        Initialize SchedulerController.

        If config_path is None the controller starts in an unloaded state —
        all models and sub-controllers are set to None. The GUI will still
        launch and the user can load a configuration via the Load Configuration
        dialog, which calls load_config() to re-initialize everything.

        Parameters:
            config_path (str | None): Path to configuration JSON file, or None
                to launch without a config.
        Returns:
            None
        """
        self.view = GUIView()

        GUIView.controller = self

        if config_path is None:
            self.config_path         = None
            self.config_model        = None
            self.faculty_model       = None
            self.course_model        = None
            self.conflict_model      = None
            self.lab_model           = None
            self.room_model          = None
            self.scheduler_model     = None
            self.faculty_controller  = None
            self.course_controller   = None
            self.conflict_controller = None
            self.lab_controller      = None
            self.room_controller     = None
            self.schedule_controller = None
            return

        self._initialize_from_path(config_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _initialize_from_path(self, config_path: str) -> None:
        """
        Builds (or rebuilds) all models and sub-controllers from a config file.

        Called by __init__ on first load and by load_config() whenever the
        user uploads a new configuration file.

        Parameters:
            config_path (str): Absolute or relative path to the JSON config.
        Returns:
            None
        """
        self.config_path = config_path

        # Models
        self.config_model    = ConfigModel(config_path)
        self.faculty_model   = FacultyModel(self.config_model)
        self.course_model    = CourseModel(self.config_model)
        self.conflict_model  = ConflictModel(self.config_model)
        self.lab_model       = LabModel(self.config_model)
        self.room_model      = RoomModel(self.config_model)
        self.scheduler_model = SchedulerModel(self.config_model)

        # Sub-controllers
        self.faculty_controller  = FacultyController(self.faculty_model, self.view)
        self.course_controller   = CourseController(self.course_model, self.config_model)
        self.conflict_controller = ConflictController(self.conflict_model, self.view)
        self.lab_controller      = LabController(self.lab_model, self.view)
        self.room_controller     = RoomController(self.room_model, self.view)
        self.schedule_controller = ScheduleController(self.scheduler_model, self.view)


    # ------------------------------------------------------------------
    # Public API used by Views
    # ------------------------------------------------------------------

    def load_config(self, file_path: str) -> tuple[bool, str]:
        """
        Load (or reload) a configuration from disk.

        This is the single entry-point the View calls when the user uploads
        a configuration file. The View is responsible only for writing the
        raw bytes to disk and passing the path here; this method handles all
        model and sub-controller construction.

        Parameters:
            file_path (str): Absolute path to the JSON configuration file.
        Returns:
            tuple[bool, str]: (True, success message) or (False, error message)
        """
        try:
            self._initialize_from_path(file_path)
            return True, f'Loaded: {file_path}'
        except Exception as e:
            return False, f'Error loading configuration: {e}'

    def save_configuration(self) -> bool:
        """
        Saves the current configuration via the model.

        Parameters:
            None
        Returns:
            bool: True if save successful, False otherwise
        """
        if self.config_model is None:
            return False
        return self.config_model.safe_save()

    def temp_save(self, feature: str = 'all') -> bool:
        """
        Writes the current in-memory state to the temp store.

        Called by the View after an in-memory change (add / modify / delete)
        so that the state is not lost between page navigations, but before the
        user has explicitly chosen to persist to the real config file.

        Parameters:
            feature (str): Which feature section to save (e.g. 'courses',
                'faculty', 'all'). Defaults to 'all'.
        Returns:
            bool: True if successful, False otherwise
        """
        if self.config_model is None:
            return False
        return self.config_model.save_feature('temp', feature)

    def save_to_config(self, feature: str = 'all') -> bool:
        """
        Persists the current in-memory state to the real configuration file.

        Called by the View when the user clicks "Save to Config".

        Parameters:
            feature (str): Which feature section to save (e.g. 'courses',
                'faculty', 'all'). Defaults to 'all'.
        Returns:
            bool: True if successful, False otherwise
        """
        if self.config_model is None:
            return False
        return self.config_model.save_feature('config', feature)

    def has_config(self) -> bool:
        """
        Returns True if a configuration is currently loaded.

        Parameters:
            None
        Returns:
            bool
        """
        return self.config_model is not None

    def get_schedule_limit(self) -> int:
        """
        Returns the schedule generation limit from the loaded config.

        Reads the raw JSON so the View always sees the value that is
        actually on disk, not a potentially stale in-memory value.
        Falls back to 100 if the config is missing or the key is absent.

        Parameters:
            None
        Returns:
            int: The schedule limit.
        """
        if self.config_model is None:
            return 100
        try:
            import json
            with open(self.config_model.config_path, 'r') as f:
                raw = json.load(f)
            return raw.get('limit', getattr(self.config_model.config, 'limit', 100))
        except Exception:
            return getattr(self.config_model.config, 'limit', 100)

    def validate_schedule_config(self) -> str:
        """
        Validates the current configuration for schedule generation.

        Parameters:
            None
        Returns:
            str: An error message if invalid, or an empty string if valid.
        """
        if self.scheduler_model is None:
            return "No scheduler model loaded."
        errors = getattr(self.scheduler_model, "validate_config", lambda: "")()
        return errors or ""

    def generate_schedules(self, limit: int) -> list:
        """
        Generates schedules via the scheduler model and returns them.

        Parameters:
            limit (int): Maximum number of schedules to generate.
        Returns:
            list: Generated schedules (may be empty).
        """
        if self.scheduler_model is None:
            return []
        return list(self.scheduler_model.generate_schedules(limit=limit))

    # ------------------------------------------------------------------
    # Application entry-point
    # ------------------------------------------------------------------

    def run(self):
        """
        Main application loop. Starts the NiceGUI server.

        Parameters:
            None
        Returns:
            None
        """
        print("\n" + "="*60)
        print("  🚀 GUI SERVER STARTING")
        print("="*60)
        print("  🌐 Open your browser to: http://localhost:8080")
        print("  🛑 Stop server: Press Ctrl+C in this terminal")
        print("="*60 + "\n")
        ui.run(title='Scheduler', reload=False, storage_secret='scheduler_secret_key')