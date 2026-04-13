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
from controllers.undoRedo_controller import UndoRedoController

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
            self.undo_redo_controller = UndoRedoController()
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

        if (
            not hasattr(self, "undo_redo_controller")
            or self.undo_redo_controller is None
        ):
            self.undo_redo_controller = UndoRedoController()

        import os

        temp_path = config_path + ".temp"
        initial_state = ""
        if os.path.exists(temp_path):
            with open(temp_path, "r") as f:
                initial_state = f.read()
        elif os.path.exists(config_path):
            with open(config_path, "r") as f:
                initial_state = f.read()

        if self.undo_redo_controller.last_known_state is None and initial_state:
            self.undo_redo_controller.set_initial_state(initial_state)

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

        success = self.config_model.save_feature("temp", feature)
        if (
            success
            and hasattr(self, "undo_redo_controller")
            and self.undo_redo_controller is not None
        ):
            import os

            temp_path = ""
            if getattr(self.config_model, "config_path", None):
                temp_path = self.config_model.config_path + ".temp"
            elif self.config_path:
                temp_path = self.config_path + ".temp"

            if temp_path and os.path.exists(temp_path):
                with open(temp_path, "r") as f:
                    current_state = f.read()
                    self.undo_redo_controller.record_state(current_state)

        return success

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

    def _get_action_description(self, state1_str: str, state2_str: str) -> str:
        if not state1_str or not state2_str:
            return "Configuration"
        try:
            from scheduler import CombinedConfig

            s1_cfg = CombinedConfig.model_validate_json(state1_str)
            s2_cfg = CombinedConfig.model_validate_json(state2_str)
            s1 = s1_cfg.model_dump()
            s2 = s2_cfg.model_dump()

            c1 = s1.get("config", {})
            c2 = s2.get("config", {})

            categories = [
                ("faculty", "Faculty", "Faculty"),
                ("courses", "Course", "Course"),
                ("rooms", "Room", "Room"),
                ("labs", "Lab", "Lab"),
            ]

            # Pass 1: Additions and Deletions take priority
            for key, single_name, plural_name in categories:
                l1 = c1.get(key, [])
                l2 = c2.get(key, [])
                if len(l1) < len(l2):
                    return f"Add {single_name}"
                if len(l1) > len(l2):
                    return f"Delete {single_name}"

            # Pass 2: Modifications check
            for key, single_name, plural_name in categories:
                l1 = c1.get(key, [])
                l2 = c2.get(key, [])
                if l1 != l2:
                    if key == "courses":
                        for i in range(min(len(l1), len(l2))):
                            if l1[i] != l2[i]:
                                old_no_conf = {
                                    k: v for k, v in l1[i].items() if k != "conflicts"
                                }
                                new_no_conf = {
                                    k: v for k, v in l2[i].items() if k != "conflicts"
                                }
                                if old_no_conf == new_no_conf and l1[i].get(
                                    "conflicts", []
                                ) != l2[i].get("conflicts", []):
                                    return "Modify Conflict"
                    return f"Modify {single_name}"

            if s1.get("time_slot_config") != s2.get("time_slot_config"):
                return "Modify Time Slots"
            if s1.get("limit") != s2.get("limit"):
                return "Modify Schedule Limit"
            if s1.get("optimizer_flags") != s2.get("optimizer_flags"):
                return "Modify Optimizer Flags"
        except Exception:
            pass
        return "Configuration"

    def perform_undo(self):
        if self.config_model is None or not self.undo_redo_controller.can_undo():
            return

        import os

        temp_path = self.config_model.config_path + ".temp"
        current_state = ""
        if os.path.exists(temp_path):
            with open(temp_path, "r") as f:
                current_state = f.read()
        elif os.path.exists(self.config_model.config_path):
            with open(self.config_model.config_path, "r") as f:
                current_state = f.read()

        previous_state = self.undo_redo_controller.undo(current_state)
        if previous_state:
            action = self._get_action_description(previous_state, current_state)
            from nicegui import app

            app.storage.user["flash_message"] = f"Undid: {action}"
            self._apply_state(previous_state)

    def perform_redo(self):
        if self.config_model is None or not self.undo_redo_controller.can_redo():
            return

        import os

        temp_path = self.config_model.config_path + ".temp"
        current_state = ""
        if os.path.exists(temp_path):
            with open(temp_path, "r") as f:
                current_state = f.read()
        elif os.path.exists(self.config_model.config_path):
            with open(self.config_model.config_path, "r") as f:
                current_state = f.read()

        next_state = self.undo_redo_controller.redo(current_state)
        if next_state:
            action = self._get_action_description(current_state, next_state)
            from nicegui import app

            app.storage.user["flash_message"] = f"Redid: {action}"
            self._apply_state(next_state)

    def _apply_state(self, state_json: str):
        if not self.config_path:
            return
        import os

        # 1. Overwrite the .temp file so save_configuration sees it
        temp_path = self.config_path + ".temp"
        with open(temp_path, "w") as f:
            f.write(state_json)

        # 2. Write to a dummy config to initialize models from
        dummy_path = self.config_path + ".undo"
        with open(dummy_path, "w") as f:
            f.write(state_json)

        # 3. Reload models pointing to dummy_path
        original = self.config_path
        self._initialize_from_path(dummy_path)

        # 4. Restore the config paths
        self.config_path = original
        if self.config_model:
            self.config_model.config_path = original
        GUIView.config_path = original

        # 5. Clean up dummy file
        if os.path.exists(dummy_path):
            os.remove(dummy_path)

        # 6. Reload page
        ui.run_javascript("window.location.reload()")

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

    def diagnose_schedule_failure(self) -> str:
        """
        Returns a human-readable explanation of why schedule generation
        produced no results. Checks three common causes in priority order:
        1. A course has no eligible faculty at all.
        2. A faculty member assigned to a course has no availability.
        3. Generic fallback message.

        Parameters:
            None
        Returns:
            str: A diagnostic message, or empty string if no issues found.
        """
        if self.config_model is None:
            return ""

        config = self.config_model.config.config
        faculty_names_with_times = {f.name for f in config.faculty if f.times}

        for course in config.courses:
            if not course.faculty:
                return (
                    f"Oh no! No schedules can be generated because "
                    f"{course.course_id} has no faculty assigned. "
                    f"Faculty must be explicitly listed on a course for it to be taught. "
                    f"Add faculty to this course under Course > Modify."
                )
            for name in course.faculty:
                if name not in faculty_names_with_times:
                    return (
                        f"Oh no! No schedules can be generated because "
                        f"{name} is assigned to teach {course.course_id} "
                        f"but has no availability set. "
                        f"Add availability under Faculty > Modify."
                    )

        return (
            "Oh no! No schedules could be generated. "
            "Check that faculty availability windows cover the required time slots."
        )

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
        print("\n" + "=" * 70)
        print("  🚀 GUI SERVER STARTING")
        print("=" * 70)
        print("  🌐 Open your browser to: http://localhost:8080")
        print("  🛑 Stop server: Press Ctrl+C in this terminal")
        print(
            "  ⚠️  Ctrl+C during generation stops generating — press again to kill server"
        )
        print("=" * 70 + "\n")
        ui.run(title="Scheduler", reload=False, storage_secret="scheduler_secret_key")
