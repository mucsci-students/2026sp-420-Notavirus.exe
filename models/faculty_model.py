# models/faculty_model.py
"""
FacultyModel - Handles faculty data operations (CRUD)

This model class manages all faculty-related data operations including:
- Adding faculty to configuration
- Deleting faculty from configuration
- Checking for duplicate faculty
- Validating faculty references in courses
"""

import scheduler
from scheduler import FacultyConfig, load_config_from_file, CombinedConfig
from scheduler.config import TimeRange

# Constants
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 0
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1


class FacultyModel:
    """
    Model class for faculty data operations.
    
    Attributes:
        config_model: Reference to ConfigModel for file operations
    """
    
    def __init__(self, config_model):
        """
        Initialize FacultyModel.
        
        Parameters:
            config_model (ConfigModel): Central configuration model
        
        Returns:
            None
        """
        self.config_model = config_model
    
    def add_faculty(self, faculty: FacultyConfig) -> bool:
        """
        Add faculty to configuration (in-memory only).
        Call config_model.safe_save() to persist changes to disk.
        
        Parameters:
            faculty (FacultyConfig): Faculty object to add
        
        Returns:
            bool: True if successful, False if faculty already exists
        """
        if self.faculty_exists(faculty.name):
            return False
        self.config_model.config.config.faculty.append(faculty)
        return True

    def delete_faculty(self, name: str) -> bool:
        """
        Delete faculty by name (in-memory only).
        Also removes all references to this faculty from courses.
        Call config_model.safe_save() to persist changes to disk.
        
        Parameters:
            name (str): Name of faculty to delete
        
        Returns:
            bool: True if successful, False if faculty not found
        """
        if not self.faculty_exists(name):
            return False
        faculty_to_delete = self.get_faculty_by_name(name)
        try:
            for course in self.config_model.config.config.courses:
                if faculty_to_delete.name in course.faculty:
                    course.faculty = [f for f in course.faculty if f != faculty_to_delete.name]
            self.config_model.config.config.faculty = [
                f for f in self.config_model.config.config.faculty
                if f.name.lower() != name.lower()
            ]
            return True
        except Exception as e:
            print(f"DEBUG delete_faculty exception: {e}")
            return False
    
    def modify_faculty(self, faculty_name: str, field: str, new_value) -> bool:
        """
        Modify a specific field of a faculty member (in-memory only).
        Directly mutates the live in-memory faculty object via setattr.
        Does not save to disk — call config_model.safe_save() to persist.
        Does not reload after saving to avoid cross-reference validation
        errors when faculty course preferences reference hypothetical courses
        that do not yet exist in the configuration.
        
        Parameters:
            faculty_name (str): Name of faculty to modify
            field (str): Field name to modify (e.g., 'maximum_credits', 'course_preferences')
            new_value: New value for the field
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.faculty_exists(faculty_name):
            return False
        try:
            faculty = self.get_faculty_by_name(faculty_name)
            if not faculty:
                return False
            setattr(faculty, field, new_value)
            return True
        except Exception as e:
            print(f"DEBUG modify_faculty exception: {e}")
            return False
    
    def faculty_exists(self, name: str) -> bool:
        """
        Check if faculty with given name exists (case-insensitive).
        
        Parameters:
            name (str): Faculty name to check
        
        Returns:
            bool: True if faculty exists, False otherwise
        """
        return any(
            f.name.lower() == name.lower()
            for f in self.config_model.config.config.faculty
        )
    
    def get_faculty_by_name(self, name: str) -> FacultyConfig | None:
        """
        Get faculty by name (case-insensitive).
        
        Parameters:
            name (str): Faculty name to find
        
        Returns:
            FacultyConfig | None: Faculty object if found, None otherwise
        """
        for faculty in self.config_model.config.config.faculty:
            if faculty.name.lower() == name.lower():
                return faculty
        return None
    
    def get_all_faculty(self) -> list[FacultyConfig]:
        """
        Get all faculty from configuration.
        
        Parameters:
            None
        
        Returns:
            list[FacultyConfig]: List of all faculty
        """
        return self.config_model.config.config.faculty
    
    def set_position_type(self, faculty_name: str, is_fulltime: bool) -> bool:
        """
        Set faculty position type and enforce corresponding credit/course-limit defaults.

        Parameters:
            faculty_name (str): Name of faculty to modify
            is_fulltime (bool): True for full-time, False for adjunct

        Returns:
            bool: True if successful, False if faculty not found
        """
        faculty = self.get_faculty_by_name(faculty_name)
        if not faculty:
            return False
        if is_fulltime:
            self.modify_faculty(faculty_name, 'unique_course_limit', FULL_TIME_UNIQUE_COURSE_LIMIT)
            self.modify_faculty(faculty_name, 'maximum_credits', FULL_TIME_MAX_CREDITS)
            if faculty.minimum_credits > FULL_TIME_MAX_CREDITS:
                self.modify_faculty(faculty_name, 'minimum_credits', FULL_TIME_MAX_CREDITS)
        else:
            self.modify_faculty(faculty_name, 'unique_course_limit', ADJUNCT_UNIQUE_COURSE_LIMIT)
            if faculty.minimum_credits > ADJUNCT_MAX_CREDITS:
                self.modify_faculty(faculty_name, 'minimum_credits', ADJUNCT_MAX_CREDITS)
            self.modify_faculty(faculty_name, 'maximum_credits', ADJUNCT_MAX_CREDITS)
        return True

    def set_maximum_credits(self, faculty_name: str, new_max: int) -> bool:
        """
        Set faculty maximum credits and keep minimum_credits and unique_course_limit consistent.

        Parameters:
            faculty_name (str): Name of faculty to modify
            new_max (int): New maximum credits value

        Returns:
            bool: True if successful, False if faculty not found
        """
        faculty = self.get_faculty_by_name(faculty_name)
        if not faculty:
            return False
        if faculty.minimum_credits > new_max:
            self.modify_faculty(faculty_name, 'minimum_credits', new_max)
        self.modify_faculty(faculty_name, 'maximum_credits', new_max)
        if new_max <= ADJUNCT_MAX_CREDITS:
            self.modify_faculty(faculty_name, 'unique_course_limit', ADJUNCT_UNIQUE_COURSE_LIMIT)
        else:
            if faculty.unique_course_limit < FULL_TIME_UNIQUE_COURSE_LIMIT:
                self.modify_faculty(faculty_name, 'unique_course_limit', FULL_TIME_UNIQUE_COURSE_LIMIT)
        return True

    def build_faculty_config(self, data: dict) -> FacultyConfig:
        """
        Build a FacultyConfig object from raw input data.

        Parameters:
            data (dict): Dictionary containing faculty data with keys:
                - name, is_full_time, days (CLI) or times (GUI),
                  course_preferences, lab_preferences

        Returns:
            FacultyConfig: Configured faculty object
        """
        if data['is_full_time']:
            max_credits = FULL_TIME_MAX_CREDITS
            unique_course_limit = FULL_TIME_UNIQUE_COURSE_LIMIT
        else:
            max_credits = ADJUNCT_MAX_CREDITS
            unique_course_limit = ADJUNCT_UNIQUE_COURSE_LIMIT

        day_map = {
            'M': 'MON', 'T': 'TUE', 'W': 'WED', 'R': 'THU', 'F': 'FRI',
            'Monday': 'MON', 'Tuesday': 'TUE', 'Wednesday': 'WED',
            'Thursday': 'THU', 'Friday': 'FRI',
        }
        times = {}
        if 'times' in data:
            for day, day_times in data['times'].items():
                if day in day_map:
                    times[day_map[day]] = [TimeRange(start=t['start'], end=t['end']) for t in day_times]
        else:
            for day in data.get('days', []):
                day_name = day_map.get(day, day)
                times[day_name] = [TimeRange(start='09:00', end='17:00')]

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

    def validate_faculty_references(self) -> int:
        """
        Validate that all faculty references in courses exist.
        Removes any invalid faculty references from courses.
        
        Parameters:
            None
        
        Returns:
            int: Number of invalid references removed
        """
        valid_faculty_names = {f.name for f in self.get_all_faculty()}
        invalid_count = 0
        for course in self.config_model.config.config.courses:
            invalid_refs = [f for f in course.faculty if f not in valid_faculty_names]
            if invalid_refs:
                invalid_count += len(invalid_refs)
                course.faculty = [f for f in course.faculty if f in valid_faculty_names]
        return invalid_count