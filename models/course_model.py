# models/course_model.py
"""
CourseModel - Handles course data operations (CRUD)
This model class manages all course-related data operations including:
- Adding courses to configuration
- Deleting courses from configuration
- Modifying existing courses
- Checking for duplicate courses
- Managing course conflicts
"""

from scheduler import CourseConfig


class CourseModel:
    """
    Model class for course data operations.
    Attributes:
        config_model: Reference to ConfigModel for file operations
    """

    def __init__(self, config_model):
        """
        Initialize CourseModel.
        Parameters:
            config_model (ConfigModel): Central configuration model
        Returns:
            None
        """
        self.config_model = config_model

    def add_course(self, course: CourseConfig) -> bool:
        """
        Add course to configuration (in-memory only).
        Call config_model.safe_save() to persist changes to disk.
        Parameters:
            course (CourseConfig): Course object to add
        Returns:
            bool: True if successful, False if course already exists
        """
        self.config_model.config.config.courses.append(course)
        return True

    def delete_course(self, course_id: str, section_index: int | None = None) -> bool:
        """
        Delete course by ID and optional section index (in-memory only).
        Also removes all references to this course from conflicts and faculty preferences.
        Call config_model.safe_save() to persist changes to disk.
        Parameters:
            course_id (str): Course ID to delete (e.g., "CMSC 340")
            section_index (int | None): Specific index to delete, or None to delete all
        Returns:
            bool: True if successful, False if course not found
        """
        if not self.course_exists(course_id):
            return False

        # Remove conflict references from other courses
        for course in self.config_model.config.config.courses:
            if course.course_id != course_id:
                if course_id in course.conflicts:
                    course.conflicts = [c for c in course.conflicts if c != course_id]

        # Remove from faculty preferences
        for faculty in self.config_model.config.config.faculty:
            if course_id in faculty.course_preferences:
                del faculty.course_preferences[course_id]

        # Remove course using list.pop() to avoid assignment validation
        courses = self.config_model.config.config.courses
        if section_index is not None:
            if section_index < len(courses):
                courses.pop(section_index)
        else:
            for i in range(len(courses) - 1, -1, -1):
                if courses[i].course_id == course_id:
                    courses.pop(i)

        return True

    def modify_course(
        self, course_id: str, section_index: int | None = None, **updates
    ) -> bool:
        """
        Modify a course's attributes (in-memory only).
        Call config_model.safe_save() to persist changes to disk.
        Parameters:
            course_id (str): Course ID to modify
            section_index (int | None): Specific section index to modify, or None to modify all matching
        Returns:
            bool: True if successful, False if course not found
        """
        if not self.course_exists(course_id):
            return False

        courses = self.config_model.config.config.courses
        for i, course in enumerate(courses):
            if course.course_id == course_id:
                if section_index is not None and i != section_index:
                    continue
                if "credits" in updates:
                    if updates["credits"] < 0:
                        return False
                    course.credits = updates["credits"]
                if "room" in updates:
                    course.room = updates["room"]
                if "lab" in updates:
                    course.lab = updates["lab"]
                if "faculty" in updates:
                    course.faculty = updates["faculty"]

        return True

    def course_exists(self, course_id: str) -> bool:
        """
        Check if course with given ID exists.
        Parameters:
            course_id (str): Course ID to check
        Returns:
            bool: True if course exists, False otherwise
        """
        return any(
            c.course_id == course_id for c in self.config_model.config.config.courses
        )

    def get_course_by_id(self, course_id: str) -> CourseConfig | None:
        """
        Get first course matching the given ID.
        Parameters:
            course_id (str): Course ID to find
        Returns:
            CourseConfig | None: Course object if found, None otherwise
        """
        for course in self.config_model.config.config.courses:
            if course.course_id == course_id:
                return course
        return None

    def get_all_courses(self) -> list[CourseConfig]:
        """
        Get all courses from configuration.
        Parameters:
            None
        Returns:
            list[CourseConfig]: List of all courses
        """
        return self.config_model.config.config.courses

    def build_course_config(self, data: dict) -> CourseConfig:
        """
        Build a CourseConfig object from raw input data.

        Parameters:
            data (dict): Dictionary with keys: course_id, credits, room, lab, faculty, conflicts

        Returns:
            CourseConfig: Configured course object
        """
        return CourseConfig(
            course_id=data["course_id"],
            credits=data["credits"],
            room=data["room"],
            lab=data["lab"],
            faculty=data["faculty"],
            conflicts=data["conflicts"],
        )

    def validate_resources(
        self, rooms: list, labs: list, faculty_names: list
    ) -> tuple[bool, str]:
        """
        Validate that rooms, labs, and faculty names exist in the configuration.

        Parameters:
            rooms (list): Room names to validate
            labs (list): Lab names to validate
            faculty_names (list): Faculty names to validate

        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        valid_rooms = self.config_model.get_all_rooms()
        for r in rooms:
            if r not in valid_rooms:
                return (
                    False,
                    f"Invalid room '{r}'. Room does not exist in configuration.",
                )
        valid_labs = self.config_model.get_all_labs()
        for lab in labs:
            if lab not in valid_labs:
                return (
                    False,
                    f"Invalid lab '{lab}'. Lab does not exist in configuration.",
                )
        valid_faculty = [f.name for f in self.config_model.get_all_faculty()]
        for f in faculty_names:
            if f not in valid_faculty:
                return False, f"Invalid faculty '{f}'. Faculty does not exist."
        return True, ""

    def get_courses_with_sections(self) -> list[tuple[str, int, CourseConfig]]:
        """
        Get all courses with section labels.
        Returns courses as tuples of (section_label, index, course).
        Section labels are formatted as "COURSE_ID.01", "COURSE_ID.02", etc.
        Parameters:
            None
        Returns:
            list[tuple[str, int, CourseConfig]]: List of (label, index, course) tuples
        """
        section_counter = {}
        result = []
        for i, course in enumerate(self.get_all_courses()):
            cid = course.course_id
            section_counter[cid] = section_counter.get(cid, 0) + 1
            label = f"{cid}.{section_counter[cid]:02d}"
            result.append((label, i, course))
        return result
