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
from controllers.chatbot_controller import ChatbotController

from views.gui_view import GUIView
from views.lab_gui_view import LabGUIView
from views.room_gui_view import RoomGUIView
from views.chatbot_gui_view import ChatbotGUIView
from views.faculty_gui_view import FacultyGUIView
from views.course_gui_view import CourseGUIView
from views.conflict_gui_view import ConflictGUIView
from views.schedule_gui_view import ScheduleGUIView
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
            self.config_path = None
            self.config_model = None
            self.faculty_model = None
            self.course_model = None
            self.conflict_model = None
            self.lab_model = None
            self.room_model = None
            self.scheduler_model = None
            self.faculty_controller = None
            self.course_controller = None
            self.conflict_controller = None
            self.lab_controller = None
            self.room_controller = None
            self.schedule_controller = None
            self.chatbot_controller = None
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
        self.config_model = ConfigModel(config_path)
        self.faculty_model = FacultyModel(self.config_model)
        self.course_model = CourseModel(self.config_model)
        self.conflict_model = ConflictModel(self.config_model)
        self.lab_model = LabModel(self.config_model)
        self.room_model = RoomModel(self.config_model)
        self.scheduler_model = SchedulerModel(self.config_model)

        # Sub-controllers
        self.faculty_controller = FacultyController(self.faculty_model, self.view)
        self.course_controller = CourseController(self.course_model, self.config_model)
        self.conflict_controller = ConflictController(self.conflict_model, self.view)
        self.lab_controller = LabController(self.lab_model, self.view)
        self.room_controller = RoomController(self.room_model, self.view)
        self.schedule_controller = ScheduleController(self.scheduler_model, self.view)
        self.chatbot_controller = ChatbotController(
            self.lab_model,
            self.room_model,
            self.course_model,
            self.faculty_model,
            self.conflict_model,
        )

        LabGUIView._lab_controller = self.lab_controller

        from views.faculty_gui_view import FacultyGUIView
        from views.course_gui_view import CourseGUIView
        from views.conflict_gui_view import ConflictGUIView
        from views.schedule_gui_view import ScheduleGUIView
        from views.schedule_gui_view import _state as _schedule_state

        FacultyGUIView.faculty_model = self.faculty_model
        FacultyGUIView.faculty_controller = self.faculty_controller

        CourseGUIView.course_model = self.course_model
        CourseGUIView.course_controller = self.course_controller

        ConflictGUIView.conflict_model = self.conflict_model
        ConflictGUIView.conflict_controller = self.conflict_controller

        LabGUIView.lab_model = self.lab_model
        LabGUIView.lab_controller = self.lab_controller
        LabGUIView._lab_controller = self.lab_controller

        RoomGUIView.room_model = self.room_model
        RoomGUIView.room_controller = self.room_controller

        if _schedule_state is not None:
            _schedule_state._scheduler_model = self.scheduler_model
        ScheduleGUIView.schedule_controller = self.schedule_controller

        ChatbotGUIView._chatbot_controller = self.chatbot_controller

        GUIView.controller = self

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

    def load_config(self, config_path: str) -> tuple[bool, str]:
        """
        Loads a new configuration file and re-initializes all models and
        sub-controllers.

        Called by the View when the user uploads a config file via the Load
        Configuration dialog.

        Parameters:
            config_path (str): Absolute path to the JSON config file.
        Returns:
            tuple[bool, str]: (True, '') on success, (False, error message) on failure.
        """
        try:
            self._initialize_from_path(config_path)
            return True, ""
        except Exception as e:
            return False, str(e)

    def temp_save(self, feature: str = "all") -> bool:
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
        return self.config_model.save_feature("temp", feature)

    def save_to_config(self, feature: str = "all") -> bool:
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
        return self.config_model.save_feature("config", feature)

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

            with open(self.config_model.config_path, "r") as f:
                raw = json.load(f)
            return raw.get("limit", getattr(self.config_model.config, "limit", 100))
        except Exception:
            return getattr(self.config_model.config, "limit", 100)

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
        print("\n" + "=" * 60)
        print("  🚀 GUI SERVER STARTING")
        print("=" * 60)
        print("  🌐 Open your browser to: http://localhost:8080")
        print("  🛑 Stop server: Press Ctrl+C in this terminal")
        print("=" * 60 + "\n")
        ui.run(title="Scheduler", reload=False, storage_secret="scheduler_secret_key")
