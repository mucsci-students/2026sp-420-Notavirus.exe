# controllers/course_controller.py
"""
CourseController - Coordinates course-related workflows

✅ MVC rules followed here:
    - All write operations (add, modify, delete) temp-save after success.
      Previously the View was responsible for calling config_model.save_feature()
      after each operation — that now happens here.
    - Input validation lives here, not in the View.
"""

from scheduler import CourseConfig


class CourseController:
    """
    Controller for course operations.

    Coordinates between CourseModel (data) and GUI layer
    to implement complete course workflows.

    Attributes:
        model:        CourseModel instance
        config_model: ConfigModel instance (for rooms/labs/faculty lookups and saves)
    """

    def __init__(self, course_model, config_model):
        self.model        = course_model
        self.config_model = config_model

    # ------------------------------------------------------------------
    # Query methods (read-only — safe for View to call)
    # ------------------------------------------------------------------

    def get_all_courses(self) -> list:
        """Return all course objects."""
        return self.model.get_all_courses()

    def get_courses_with_sections(self) -> list:
        """Return list of (section_label, index, course_object)."""
        return self.model.get_courses_with_sections()

    def get_available_resources(self) -> dict:
        """
        Return available rooms, labs, and faculty for GUI dropdowns.

        Returns:
            dict: {'rooms': [...], 'labs': [...], 'faculty': [...]}
        """
        return {
            "rooms":   self.config_model.get_all_rooms(),
            "labs":    self.config_model.get_all_labs(),
            "faculty": [f.name for f in self.config_model.get_all_faculty()],
        }

    # ------------------------------------------------------------------
    # GUI command methods — all return (bool, str) and temp-save
    # ------------------------------------------------------------------

    def add_course(self, data: dict) -> tuple[bool, str]:
        """
        Validate input, add a course, and temp-save.

        ✅ Validation lives here, not in the View.
           Temp-save happens here — the View no longer calls
           config_model.save_feature() after this method.

        Parameters:
            data (dict): Course data from the GUI (course_id, credits, room,
                         lab, faculty, conflicts).
        Returns:
            tuple[bool, str]: (success, message)
        """
        # --- Validation ---
        course_id = (data.get('course_id') or '').strip()
        if not course_id:
            return False, "Course ID is required."

        try:
            credits = int(data.get('credits', 0))
        except (ValueError, TypeError):
            return False, "Credits must be a valid number."

        if credits < 0:
            return False, "Credits cannot be negative."

        # --- Build and add ---
        try:
            data['course_id'] = course_id
            data['credits']   = credits
            course_config     = self._build_course_config(data)
            success           = self.model.add_course(course_config)
            if success:
                # ✅ Temp-save happens here — View never touches config_model.
                self.config_model.save_feature('temp', 'courses')
                return True, f"Course '{course_id}' added successfully."
            return False, f"Course '{course_id}' already exists."
        except Exception as e:
            return False, f"Failed to add course: {e}"

    def modify_course(
        self,
        course_id: str,
        section_index: int,
        modifications: dict,
    ) -> tuple[bool, str]:
        """
        Validate, apply modifications to a course section, and temp-save.

        ✅ Temp-save happens here — the View no longer calls
           config_model.save_feature() after this method.

        Parameters:
            course_id     (str):  Course ID.
            section_index (int):  Section index to modify.
            modifications (dict): Fields to update.
        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            course = self.model.get_course_by_id(course_id)
            if not course:
                return False, f"No course '{course_id}' found."

            updates, error_msg = self._parse_modifications(modifications, course)
            if updates is None:
                return False, error_msg

            success = self.model.modify_course(course_id, section_index=section_index, **updates)
            if success:
                # ✅ Temp-save happens here — View never touches config_model.
                self.config_model.save_feature('temp', 'all')
                return True, f"Course '{course_id}' updated successfully."
            return False, f"Failed to update course '{course_id}'."
        except Exception as e:
            return False, f"Failed to modify course: {e}"

    def delete_course(self, course_id: str, section_index: int) -> tuple[bool, str]:
        """
        Delete a course section and temp-save.

        ✅ Temp-save happens here — the View no longer calls
           config_model.save_feature() after this method.

        Parameters:
            course_id     (str): Course ID.
            section_index (int): Section index to delete.
        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            success = self.model.delete_course(course_id, section_index)
            if success:
                # ✅ Temp-save happens here — View never touches config_model.
                self.config_model.save_feature('temp', 'all')
                return True, "Course section deleted successfully."
            return False, "Failed to delete course section."
        except Exception as e:
            return False, f"Failed to delete course: {e}"

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_course_config(self, data: dict) -> CourseConfig:
        return CourseConfig(
            course_id=data['course_id'],
            credits=data['credits'],
            room=data['room'],
            lab=data['lab'],
            faculty=data['faculty'],
            conflicts=data['conflicts'],
        )

    def _parse_modifications(
        self,
        modifications: dict,
        current_course,
    ) -> tuple[dict | None, str]:
        """
        Parse and validate modification inputs.

        Returns (updates_dict, '') on success, or (None, error_message) on failure.
        """
        updates = {}

        if 'credits' in modifications and modifications['credits'] is not None:
            try:
                credits_int = int(modifications['credits'])
                if credits_int < 0:
                    return None, "Credits must be a positive integer."
                updates['credits'] = credits_int
            except (ValueError, TypeError):
                return None, "Credits must be a valid number."

        def _to_list(val):
            if isinstance(val, list):
                return val
            if isinstance(val, str):
                return [x.strip() for x in val.split(",") if x.strip()]
            return []

        if 'room' in modifications and modifications['room'] is not None:
            rooms       = _to_list(modifications['room'])
            valid_rooms = self.config_model.get_all_rooms()
            for r in rooms:
                if r not in valid_rooms:
                    return None, f"Invalid room '{r}'. Room does not exist in configuration."
            updates['room'] = rooms

        if 'lab' in modifications and modifications['lab'] is not None:
            labs       = _to_list(modifications['lab'])
            valid_labs = self.config_model.get_all_labs()
            for lab in labs:
                if lab not in valid_labs:
                    return None, f"Invalid lab '{lab}'. Lab does not exist in configuration."
            updates['lab'] = labs

        if 'faculty' in modifications and modifications['faculty'] is not None:
            faculties      = _to_list(modifications['faculty'])
            valid_faculty  = [f.name for f in self.config_model.get_all_faculty()]
            for f in faculties:
                if f not in valid_faculty:
                    return None, f"Invalid faculty '{f}'. Faculty does not exist."
            updates['faculty'] = faculties

        return updates, ""