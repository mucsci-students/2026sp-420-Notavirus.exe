# controllers/faculty_controller.py
"""
FacultyController - Coordinates faculty-related workflows

   MVC rules followed here:
    - All GUI-facing methods return (bool, str) tuples.
    - Temp-save after every in-memory write happens here, not in the View.
    - CLI methods are preserved unchanged for backward compatibility.
"""

from scheduler import FacultyConfig, TimeRange

# Constants
FULL_TIME_MAX_CREDITS        = 12
ADJUNCT_MAX_CREDITS          = 4
MIN_CREDITS                  = 0
MAX_DAYS                     = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT   = 1


class FacultyController:
    """
    Controller for faculty operations.

    Coordinates between FacultyModel (data) and the view layer to
    implement complete faculty workflows.

    Attributes:
        model: FacultyModel instance
        view:  View instance (GUIView or CLIView)
    """

    def __init__(self, faculty_model, view):
        self.model = faculty_model
        self.view  = view

    # ------------------------------------------------------------------
    # Query methods (read-only — safe for View to call)
    # ------------------------------------------------------------------

    def get_all_faculty(self) -> list:
        """Return all faculty objects."""
        return self.model.get_all_faculty()

    def get_faculty_by_name(self, name: str):
        """Return a single faculty object by name, or None."""
        return self.model.get_faculty_by_name(name)

    def get_available_courses(self) -> list[str]:
        """Return sorted list of unique course IDs from the config."""
        courses = self.model.config_model.get_all_courses()
        return sorted(set(c.course_id for c in courses))

    def get_available_labs(self) -> list[str]:
        """Return sorted list of lab names from the config."""
        return sorted(set(self.model.config_model.get_all_labs()))

    def get_available_rooms(self) -> list[str]:
        """Return sorted list of room names from the config."""
        return sorted(set(self.model.config_model.get_all_rooms()))

    def get_existing_faculty_names(self) -> list[str]:
        """Return list of all faculty names."""
        return [f.name for f in self.model.get_all_faculty()]

    # ------------------------------------------------------------------
    # GUI command methods — all return (bool, str) and temp-save
    # ------------------------------------------------------------------

    def add_faculty(self, faculty_data: dict) -> tuple[bool, str]:
        """
        Add a new faculty member and temp-save.

          Returns (bool, str) for the View to display.
           Temp-save happens here, not in the View.

        Parameters:
            faculty_data (dict): Faculty data collected by the View.
        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            faculty_config = self._build_faculty_config(faculty_data)
            success        = self.model.add_faculty(faculty_config)
            if success:
                self.model.config_model.save_feature('temp', 'faculty')
                return True, f"Faculty '{faculty_data['name']}' saved to memory."
            return False, f"Failed to add faculty — '{faculty_data['name']}' may already exist."
        except Exception as e:
            return False, f"Error adding faculty: {e}"

    def add_faculty_if_not_exists(self, faculty_data: dict) -> tuple[bool, str]:
        """
        Add faculty only if not already present. Used by save-to-config flow.

        Parameters:
            faculty_data (dict): Faculty data collected by the View.
        Returns:
            tuple[bool, str]: (success, message)
        """
        existing = [f.name for f in self.model.get_all_faculty()]
        if faculty_data['name'] in existing:
            return True, "Faculty already exists — skipping add."
        return self.add_faculty(faculty_data)

    def delete_faculty(self, name: str) -> tuple[bool, str]:
        """
        Delete a faculty member by name and temp-save.

           Returns (bool, str) for the View to display.
           Temp-save happens here, not in the View.

        Parameters:
            name (str): Name of the faculty member to delete.
        Returns:
            tuple[bool, str]: (success, message)
        """
        ok = self.model.delete_faculty(name)
        if ok:
            self.model.config_model.save_feature('temp', 'faculty')
            return True, f"✓ '{name}' deleted from memory."
        return False, f"⚠ Could not delete '{name}'."

    def modify_faculty_field(self, name: str, field: str, value) -> tuple[bool, str]:
        """
        Modify a single field on a faculty member and temp-save.

           Replaces the old pattern of calling controller.model.modify_faculty()
           directly from the View.

        Parameters:
            name  (str): Faculty name.
            field (str): Field to modify (e.g. 'minimum_credits', 'times').
            value:       New value.
        Returns:
            tuple[bool, str]: (success, message)
        """
        success = self.model.modify_faculty(name, field, value)
        if success:
            self.model.config_model.save_feature('temp', 'all')
            return True, "Updated in memory."
        return False, "Update failed."

    def set_position(self, name: str, is_full_time: bool) -> tuple[bool, str]:
        """
        Set a faculty member's position type (full-time / adjunct) and temp-save.

        Parameters:
            name         (str):  Faculty name.
            is_full_time (bool): True for full-time, False for adjunct.
        Returns:
            tuple[bool, str]: (success, message)
        """
        ok = self.gui_set_position(name, is_full_time)
        if ok:
            self.model.config_model.save_feature('temp', 'all')
            label = 'Full-time' if is_full_time else 'Adjunct'
            return True, f"Position set to {label}."
        return False, "Failed to update position."

    def set_maximum_credits(self, name: str, credits: int) -> tuple[bool, str]:
        """
        Set a faculty member's maximum credits and temp-save.

        Parameters:
            name    (str): Faculty name.
            credits (int): New maximum credits value.
        Returns:
            tuple[bool, str]: (success, message)
        """
        ok = self.gui_set_maximum_credits(name, credits)
        if ok:
            self.model.config_model.save_feature('temp', 'all')
            return True, "Maximum credits updated."
        return False, "Failed to update maximum credits."

    # ------------------------------------------------------------------
    # Existing GUI helpers (kept, used internally by set_position etc.)
    # ------------------------------------------------------------------

    def gui_set_position(self, faculty_name: str, is_fulltime: bool) -> bool:
        """
        Set faculty position type and update credits / course limit accordingly.

        Parameters:
            faculty_name (str):  Name of faculty to modify.
            is_fulltime  (bool): True for full-time, False for adjunct.
        Returns:
            bool: True if successful.
        """
        faculty = self.model.get_faculty_by_name(faculty_name)
        if not faculty:
            return False
        if is_fulltime:
            self.model.modify_faculty(faculty_name, 'unique_course_limit', 2)
            if faculty.maximum_credits <= 4:
                self.model.modify_faculty(faculty_name, 'maximum_credits', 12)
        else:
            self.model.modify_faculty(faculty_name, 'unique_course_limit', 1)
            if faculty.maximum_credits > 4:
                if faculty.minimum_credits > 4:
                    self.model.modify_faculty(faculty_name, 'minimum_credits', 4)
                self.model.modify_faculty(faculty_name, 'maximum_credits', 4)
        return True

    def gui_set_maximum_credits(self, faculty_name: str, new_max: int) -> bool:
        """
        Set max credits and sync unique_course_limit and minimum_credits.

        Parameters:
            faculty_name (str): Name of faculty to modify.
            new_max      (int): New maximum credits value.
        Returns:
            bool: True if successful.
        """
        faculty = self.model.get_faculty_by_name(faculty_name)
        if not faculty:
            return False
        if faculty.minimum_credits > new_max:
            self.model.modify_faculty(faculty_name, 'minimum_credits', new_max)
        self.model.modify_faculty(faculty_name, 'maximum_credits', new_max)
        if new_max <= 4:
            self.model.modify_faculty(faculty_name, 'unique_course_limit', 1)
        else:
            if faculty.unique_course_limit < 2:
                self.model.modify_faculty(faculty_name, 'unique_course_limit', 2)
        return True


    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_faculty_config(self, data: dict) -> FacultyConfig:
        """Build a FacultyConfig from GUI or CLI input data."""
        if data['is_full_time']:
            max_credits         = FULL_TIME_MAX_CREDITS
            unique_course_limit = FULL_TIME_UNIQUE_COURSE_LIMIT
        else:
            max_credits         = ADJUNCT_MAX_CREDITS
            unique_course_limit = ADJUNCT_UNIQUE_COURSE_LIMIT

        day_map = {
            'M': 'MON', 'T': 'TUE', 'W': 'WED', 'R': 'THU', 'F': 'FRI',
            'Monday': 'MON', 'Tuesday': 'TUE', 'Wednesday': 'WED',
            'Thursday': 'THU', 'Friday': 'FRI',
        }
        times = {}
        if 'times' in data:
            for day, day_times in data['times'].items():
                key = day_map.get(day, day)
                times[key] = [TimeRange(start=t['start'], end=t['end']) for t in day_times]
        else:
            for day in data.get('days', []):
                key = day_map.get(day, day)
                times[key] = [TimeRange(start='09:00', end='17:00')]

        return FacultyConfig(
            name=data['name'],
            maximum_credits=max_credits,
            minimum_credits=MIN_CREDITS,
            unique_course_limit=unique_course_limit,
            course_preferences=data.get('course_preferences', {}),
            maximum_days=MAX_DAYS,
            times=times,
            room_preferences={},
            lab_preferences=data.get('lab_preferences', {}),
        )

    def _handle_modification(self, faculty_name: str, choice: str, faculty) -> bool:
        """Handle CLI modification menu choice."""
        if choice == '1':
            is_full_time = self.view.get_position_input()
            if is_full_time:
                self.model.modify_faculty(faculty_name, 'maximum_credits', FULL_TIME_MAX_CREDITS)
                self.model.modify_faculty(faculty_name, 'unique_course_limit', FULL_TIME_UNIQUE_COURSE_LIMIT)
                if faculty.minimum_credits > FULL_TIME_MAX_CREDITS:
                    self.model.modify_faculty(faculty_name, 'minimum_credits', FULL_TIME_MAX_CREDITS)
            else:
                self.model.modify_faculty(faculty_name, 'maximum_credits', ADJUNCT_MAX_CREDITS)
                self.model.modify_faculty(faculty_name, 'unique_course_limit', ADJUNCT_UNIQUE_COURSE_LIMIT)
                if faculty.minimum_credits > ADJUNCT_MAX_CREDITS:
                    self.model.modify_faculty(faculty_name, 'minimum_credits', ADJUNCT_MAX_CREDITS)
            return True
        elif choice == '2':
            new_max = self.view.get_integer_input("Enter new maximum credits: ", min_val=faculty.minimum_credits)
            return self.model.modify_faculty(faculty_name, 'maximum_credits', new_max)
        elif choice == '3':
            new_min = self.view.get_integer_input("Enter new minimum credits: ", min_val=0, max_val=faculty.maximum_credits)
            return self.model.modify_faculty(faculty_name, 'minimum_credits', new_min)
        elif choice == '4':
            new_limit = self.view.get_integer_input("Enter new unique course limit: ", min_val=1)
            return self.model.modify_faculty(faculty_name, 'unique_course_limit', new_limit)
        elif choice == '5':
            new_max_days = self.view.get_integer_input("Enter new maximum days (0-5): ", min_val=0, max_val=5)
            return self.model.modify_faculty(faculty_name, 'maximum_days', new_max_days)
        elif choice == '6':
            self.view.display_message("Availability time modification not yet implemented in MVC.")
            return False
        elif choice == '7':
            course_prefs = self.view.get_course_preferences_input()
            return self.model.modify_faculty(faculty_name, 'course_preferences', course_prefs)
        elif choice == '8':
            room_prefs = self.view.get_room_preferences_input()
            return self.model.modify_faculty(faculty_name, 'room_preferences', room_prefs)
        elif choice == '9':
            lab_prefs = self.view.get_lab_preferences_input()
            return self.model.modify_faculty(faculty_name, 'lab_preferences', lab_prefs)
        return False