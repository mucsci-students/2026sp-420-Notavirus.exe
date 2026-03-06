# controllers/course_controller.py
"""
CourseController - Coordinates course-related workflows

This controller class manages all course workflows including:
- Adding new courses
- Modifying existing courses
- Deleting courses
- Validating course data
"""

# controllers/course_controller.py

from scheduler import CourseConfig


class CourseController:
    """
    Controller for course operations.

    Coordinates between CourseModel (data) and GUI layer
    to implement complete course workflows.

    Attributes:
        model: CourseModel instance
        config_model: ConfigModel instance (for accessing rooms/labs/faculty)
    """

    def __init__(self, course_model, config_model):
        """
        Initialize CourseController.

        Parameters:
            course_model (CourseModel): Model for course data operations
            config_model (ConfigModel): Config model for accessing rooms/labs/faculty

        Returns:
            None
        """
        self.model = course_model
        self.config_model = config_model

    def get_all_courses(self):
        """
        Get all courses in the configuration.

        Parameters:
            None

        Returns:
            list: List of course objects
        """
        return self.model.get_all_courses()

    def get_courses_with_sections(self):
        """
        Get courses including generated section labels.

        Parameters:
            None

        Returns:
            list: List of tuples (section_label, index, course_object)
        """
        return self.model.get_courses_with_sections()

    def get_available_resources(self):
        """
        Get available rooms, labs, and faculty for GUI dropdowns.

        Parameters:
            None

        Returns:
            dict: Dictionary containing:
                - rooms (list)
                - labs (list)
                - faculty (list)
        """
        return {
            "rooms": self.config_model.get_all_rooms(),
            "labs": self.config_model.get_all_labs(),
            "faculty": [f.name for f in self.config_model.get_all_faculty()],
        }


    def add_course(self, data: dict) -> tuple[bool, str]:
        """
        Complete workflow for adding a new course (GUI version).

        Steps:
        1. Build CourseConfig object
        2. Add via Model
        3. Return success status and message

        Parameters:
            data (dict): Dictionary containing course data from GUI input

        Returns:
            tuple[bool, str]:
                - success (True if added successfully)
                - message (Result message for GUI display)
        """
        try:
            course_config = self._build_course_config(data)
            success = self.model.add_course(course_config)

            if success:
                return True, f"Course '{data['course_id']}' added successfully."
            return False, f"Course '{data['course_id']}' already exists."

        except Exception as e:
            return False, f"Failed to add course: {e}"


    def delete_course(self, course_id: str, section_index: int) -> tuple[bool, str]:
        """
        Complete workflow for deleting a course section (GUI version).

        Steps:
        1. Validate section exists
        2. Delete via Model
        3. Return success status and message

        Parameters:
            course_id (str): Base course ID
            section_index (int): Index of the section to delete

        Returns:
            tuple[bool, str]:
                - success (True if deleted successfully)
                - message (Result message for GUI display)
        """
        try:
            success = self.model.delete_course(course_id, section_index)

            if success:
                return True, "Course section deleted successfully."
            return False, "Failed to delete course section."

        except Exception as e:
            return False, f"Failed to delete course: {e}"


    def modify_course(self, course_id: str, section_index: int, modifications: dict) -> tuple[bool, str]:
        """
        Complete workflow for modifying a course (GUI version).

        Steps:
        1. Validate course exists
        2. Parse modification inputs
        3. Apply updates via Model
        4. Return success status and message

        Parameters:
            course_id (str): ID of the course to modify
            section_index (int): Index of the section to modify
            modifications (dict): Raw modification inputs from GUI

        Returns:
            tuple[bool, str]:
                - success (True if updated successfully)
                - message (Result message for GUI display)
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
                return True, f"Course '{course_id}' updated successfully."
            return False, f"Failed to update course '{course_id}'."

        except Exception as e:
            return False, f"Failed to modify course: {e}"

    def _build_course_config(self, data: dict) -> CourseConfig:
        """
        Build a CourseConfig object from GUI input data.

        Parameters:
            data (dict): Dictionary containing course input data

        Returns:
            CourseConfig: Configured course object
        """
        return CourseConfig(
            course_id=data['course_id'],
            credits=data['credits'],
            room=data['room'],
            lab=data['lab'],
            faculty=data['faculty'],
            conflicts=data['conflicts']
        )

    def _parse_modifications(self, modifications: dict, current_course) -> tuple[dict | None, str]:
        """
        Parse modification inputs into update dictionary.

        Handles special cases like:
        - Converting comma-separated lists
        - Adding/removing faculty members (prefix with -)
        - Validating credit values
        - Validating existence of rooms, labs, and faculty

        Parameters:
            modifications (dict): Raw modification inputs from GUI
            current_course: Current course object for reference

        Returns:
            tuple[dict | None, str]:
                - Dictionary of updates if valid, error message string
                - None if validation fails, error message string
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

        # Handle lists and comma-separated strings for backwards compatibility
        def _to_list(val):
            if isinstance(val, list):
                return val
            if isinstance(val, str):
                return [x.strip() for x in val.split(",") if x.strip()]
            return []

        if 'room' in modifications and modifications['room'] is not None:
            rooms = _to_list(modifications['room'])
            valid_rooms = self.config_model.get_all_rooms()
            for r in rooms:
                if r not in valid_rooms:
                    return None, f"Invalid room '{r}'. Room does not exist in configuration."
            updates['room'] = rooms

        if 'lab' in modifications and modifications['lab'] is not None:
            labs = _to_list(modifications['lab'])
            valid_labs = self.config_model.get_all_labs()
            for l in labs:
                if l not in valid_labs:
                    return None, f"Invalid lab '{l}'. Lab does not exist in configuration."
            updates['lab'] = labs

        if 'faculty' in modifications and modifications['faculty'] is not None:
            faculties = _to_list(modifications['faculty'])
            valid_faculty = [f.name for f in self.config_model.get_all_faculty()]
            for f in faculties:
                if f not in valid_faculty:
                    return None, f"Invalid faculty '{f}'. Faculty does not exist."
            updates['faculty'] = faculties

        return updates, ""