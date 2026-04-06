# controllers/course_controller.py
"""
CourseController - Coordinates course-related workflows

   MVC rules followed here:
    - All write operations (add, modify, delete) temp-save after success.
      Previously the View was responsible for calling config_model.save_feature()
      after each operation — that now happens here.
    - Input validation lives here, not in the View.
"""


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
        self.model = course_model
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
            "rooms": self.config_model.get_all_rooms(),
            "labs": self.config_model.get_all_labs(),
            "faculty": [f.name for f in self.config_model.get_all_faculty()],
        }

    # ------------------------------------------------------------------
    # GUI command methods — all return (bool, str) and temp-save
    # ------------------------------------------------------------------

    def add_course(self, data: dict) -> tuple[bool, str]:
        """
        Validate input, add a course, and temp-save.

        Parameters:
            data (dict): Course data from the GUI (course_id, credits, room,
                         lab, faculty, conflicts).
        Returns:
            tuple[bool, str]: (success, message)
        """
        # --- Validation ---
        course_id = (data.get("course_id") or "").strip()
        if not course_id:
            return False, "Course ID is required."

        try:
            credits = int(data.get("credits", 0))
        except (ValueError, TypeError):
            return False, "Credits must be a valid number."

        if credits < 0:
            return False, "Credits cannot be negative."

        # --- Build and add ---
        try:
            data["course_id"] = course_id
            data["credits"] = credits
            course_config = self._build_course_config(data)
            success = self.model.add_course(course_config)
            if success:
                self.config_model.save_feature("temp", "courses")
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

            success = self.model.modify_course(
                course_id, section_index=section_index, **updates
            )
            if success:
                self.config_model.save_feature("temp", "all")
                return True, f"Course '{course_id}' updated successfully."
            return False, f"Failed to update course '{course_id}'."
        except Exception as e:
            return False, f"Failed to modify course: {e}"

    def delete_course(
        self, course_id: str, section_index: int | None = None
    ) -> tuple[bool, str]:
        """
        Delete a course section (or all sections) and temp-save.

        Parameters:
            course_id     (str):      Course ID to delete.
            section_index (int|None): Section index to delete, or None for all.
        Returns:
            tuple[bool, str]: (success, message)
        """
        try:
            # Calculate 1-based relative section number before deletion
            display_index = section_index
            if section_index is not None:
                all_courses = self.model.get_all_courses()
                if 0 <= section_index < len(all_courses):
                    display_index = 0
                    for i in range(section_index + 1):
                        if all_courses[i].course_id == course_id:
                            display_index += 1

            success = self.model.delete_course(course_id, section_index)
            if success:
                self.config_model.save_feature("temp", "courses")
                label = (
                    f"'{course_id}' section {display_index}"
                    if section_index is not None
                    else f"'{course_id}'"
                )
                return True, f"Course {label} deleted successfully."
            return False, f"Course '{course_id}' not found."
        except Exception as e:
            return False, f"Failed to delete course: {e}"

    def _build_course_config(self, data: dict):
        return self.model.build_course_config(data)

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

        if "credits" in modifications and modifications["credits"] is not None:
            try:
                credits_int = int(modifications["credits"])
                if credits_int < 0:
                    return None, "Credits must be a positive integer."
                updates["credits"] = credits_int
            except (ValueError, TypeError):
                return None, "Credits must be a valid number."

        def _to_list(val):
            if isinstance(val, list):
                return val
            if isinstance(val, str):
                return [x.strip() for x in val.split(",") if x.strip()]
            return []

        rooms = (
            _to_list(modifications["room"])
            if "room" in modifications and modifications["room"] is not None
            else None
        )
        labs = (
            _to_list(modifications["lab"])
            if "lab" in modifications and modifications["lab"] is not None
            else None
        )
        faculties = (
            _to_list(modifications["faculty"])
            if "faculty" in modifications and modifications["faculty"] is not None
            else None
        )

        valid, error = self.model.validate_resources(
            rooms or [], labs or [], faculties or []
        )
        if not valid:
            return None, error

        if rooms is not None:
            updates["room"] = rooms
        if labs is not None:
            updates["lab"] = labs
        if faculties is not None:
            updates["faculty"] = faculties

        return updates, ""
