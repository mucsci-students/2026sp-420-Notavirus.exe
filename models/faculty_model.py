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

# Constants
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 0
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
        Add faculty to configuration.
        
        Parameters:
            faculty (FacultyConfig): Faculty object to add
        
        Returns:
            bool: True if successful, False if faculty already exists
        """
        # Check if faculty already exists
        if self.faculty_exists(faculty.name):
            return False
        
        # Add faculty to config
        self.config_model.config.config.faculty.append(faculty)
        
        # Save and reload
        self.config_model.safe_save()
        self.config_model.reload()
        
        return True
    
    def delete_faculty(self, name: str) -> bool:
        """
        Delete faculty by name (case-insensitive).
        
        Also removes all references to this faculty from courses.
        
        Parameters:
            name (str): Name of faculty to delete
        
        Returns:
            bool: True if successful, False if faculty not found
        """
        # Find the faculty
        faculty_to_delete = self.get_faculty_by_name(name)
        if not faculty_to_delete:
            return False
        
        try:
            with self.config_model.config.config.edit_mode() as editable:
                # Remove faculty references from courses FIRST
                for course in editable.courses:
                    if faculty_to_delete.name in course.faculty:
                        course.faculty.remove(faculty_to_delete.name)
                
                # Then remove the faculty from faculty list
                editable.faculty = [
                    f for f in editable.faculty
                    if f.name.lower() != name.lower()
                ]
            
            # Save changes
            self.config_model.safe_save()
            self.config_model.reload()
            return True
            
        except Exception:
            return False
    
    def modify_faculty(self, faculty_name: str, field: str, new_value) -> bool:
        """
        Modify a specific field of a faculty member.
        
        Parameters:
            faculty_name (str): Name of faculty to modify
            field (str): Field name to modify (e.g., 'maximum_credits')
            new_value: New value for the field
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with self.config_model.config.config.edit_mode() as editable:
                # Find faculty in editable config
                for faculty in editable.faculty:
                    if faculty.name == faculty_name:
                        setattr(faculty, field, new_value)
                        break
                else:
                    return False
            
            # Save changes
            self.config_model.safe_save()
            self.config_model.reload()
            return True
            
        except Exception:
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
    
    def validate_faculty_references(self) -> int:
        """
        Validate that all faculty references in courses exist.
        
        Removes any invalid faculty references from courses.
        
        Parameters:
            None
        
        Returns:
            int: Number of invalid references removed
        """
        # Get set of valid faculty names
        valid_faculty_names = {f.name for f in self.get_all_faculty()}
        
        invalid_count = 0
        
        # Check all courses for invalid faculty references
        for course in self.config_model.config.config.courses:
            invalid_refs = [f for f in course.faculty if f not in valid_faculty_names]
            if invalid_refs:
                invalid_count += len(invalid_refs)
                course.faculty = [f for f in course.faculty if f in valid_faculty_names]
        
        if invalid_count > 0:
            # Save cleaned config
            self.config_model.safe_save()
            self.config_model.reload()
        
        return invalid_count