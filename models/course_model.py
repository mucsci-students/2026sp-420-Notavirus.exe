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
        Add course to configuration.
        
        Parameters:
            course (CourseConfig): Course object to add
        
        Returns:
            bool: True if successful, False if course already exists
        """
        # Check if course already exists
        if self.course_exists(course.course_id):
            return False
        
        # Add course to config
        self.config_model.config.config.courses.append(course)
        
        # Save and reload
        if not self.config_model.safe_save():
            return False
        
        self.config_model.reload()
        return True
    
    def delete_course(self, course_id: str, section_index: int = None) -> bool:
        """
        Delete course by ID and optional section index.
        
        Also removes all references to this course from conflicts and faculty preferences.
        
        Parameters:
            course_id (str): Course ID to delete (e.g., "CMSC 340")
            section_index (int | None): Specific index to delete, or None to delete all
        
        Returns:
            bool: True if successful, False if course not found
        """
        try:
            with self.config_model.config.config.edit_mode() as editable:
                # Clean up conflict references in other courses
                for course in editable.courses:
                    if course.course_id != course_id:
                        while course_id in course.conflicts:
                            course.conflicts.remove(course_id)
                
                # Clean up faculty preferences
                for faculty in editable.faculty:
                    if course_id in faculty.course_preferences:
                        del faculty.course_preferences[course_id]
                
                # Remove course(s)
                if section_index is not None:
                    # Remove specific section by index
                    editable.courses = [
                        c for i, c in enumerate(editable.courses)
                        if i != section_index
                    ]
                else:
                    # Remove all courses with this ID
                    editable.courses = [
                        c for c in editable.courses
                        if c.course_id != course_id
                    ]
            
            # Save changes
            if not self.config_model.safe_save():
                return False
            
            self.config_model.reload()
            return True
            
        except Exception:
            return False
    
    def modify_course(self, course_id: str, **updates) -> bool:
        """
        Modify a course's attributes.
        
        Parameters:
            course_id (str): Course ID to modify
            **updates: Keyword arguments for fields to update
                - credits (int): New credit value
                - room (list): New room list
                - lab (list): New lab list
                - faculty (list): New faculty list
        
        Returns:
            bool: True if successful, False if course not found
        """
        try:
            with self.config_model.config.config.edit_mode() as editable:
                # Find all courses with this ID
                modified = False
                for course in editable.courses:
                    if course.course_id == course_id:
                        # Apply updates
                        if 'credits' in updates:
                            if updates['credits'] < 0:
                                return False
                            course.credits = updates['credits']
                        
                        if 'room' in updates:
                            course.room = updates['room']
                        
                        if 'lab' in updates:
                            course.lab = updates['lab']
                        
                        if 'faculty' in updates:
                            course.faculty = updates['faculty']
                        
                        modified = True
                
                if not modified:
                    return False
            
            # Save changes
            if not self.config_model.safe_save():
                return False
            
            self.config_model.reload()
            return True
            
        except Exception:
            return False
    
    def course_exists(self, course_id: str) -> bool:
        """
        Check if course with given ID exists.
        
        Parameters:
            course_id (str): Course ID to check
        
        Returns:
            bool: True if course exists, False otherwise
        """
        return any(
            c.course_id == course_id
            for c in self.config_model.config.config.courses
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