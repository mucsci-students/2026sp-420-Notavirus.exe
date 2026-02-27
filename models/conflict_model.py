# models/conflict_model.py
"""
ConflictModel - Handles conflict data operations

This model class manages all conflict-related data operations including:
- Adding conflicts between courses
- Deleting conflicts between courses
- Modifying existing conflicts
- Managing mutual conflict relationships
"""

from scheduler.config import CourseConfig


class ConflictModel:
    """
    Model class for conflict data operations.
    
    Attributes:
        config_model: Reference to ConfigModel for file operations
    """
    
    def __init__(self, config_model):
        """
        Initialize ConflictModel.
        
        Parameters:
            config_model (ConfigModel): Central configuration model
        
        Returns:
            None
        """
        self.config_model = config_model
    
    def add_conflict(self, course_id_1: str, course_id_2: str) -> bool:
        """
        Add mutual conflict between two courses.
        
        Adds course_id_2 to course_id_1's conflicts list and vice versa.
        
        Parameters:
            course_id_1 (str): First course ID
            course_id_2 (str): Second course ID
        
        Returns:
            bool: True if successful, False if courses don't exist or already conflict
        """
        if course_id_1 == course_id_2:
            return False
        
        # Reload to ensure we have latest data
        self.config_model.reload()
        
        try:
            with self.config_model.config.config.edit_mode() as editable:
                # Find ALL courses matching the IDs
                c1_list = [c for c in editable.courses if c.course_id == course_id_1]
                c2_list = [c for c in editable.courses if c.course_id == course_id_2]
                
                if not c1_list or not c2_list:
                    return False
                
                # Add conflict to all matching courses
                for course in c1_list:
                    if course_id_2 not in course.conflicts:
                        course.conflicts.append(course_id_2)
                
                for course in c2_list:
                    if course_id_1 not in course.conflicts:
                        course.conflicts.append(course_id_1)
            
            # Save changes
            if not self.config_model.safe_save():
                return False
            
            self.config_model.reload()
            return True
            
        except Exception:
            return False
    
    def delete_conflict(self, course_id_1: str, course_id_2: str, section_index_1: int, section_index_2: int) -> bool:
        """
        Delete mutual conflict between two specific course sections.
        
        Parameters:
            course_id_1 (str): First course ID
            course_id_2 (str): Second course ID
            section_index_1 (int): Global index of the first course section
            section_index_2 (int): Global index of the second course section
        
        Returns:
            bool: True if successful, False if conflict doesn't exist
        """
        self.config_model.reload()
            
        try:
            with self.config_model.config.config.edit_mode() as editable:                    
                found = False
                courses = editable.courses
                    
                c1 = courses[section_index_1] if section_index_1 < len(courses) else None
                c2 = courses[section_index_2] if section_index_2 < len(courses) else None
                    
                if not c1 or not c2:
                    return False
                    
                if c1.course_id == course_id_1 and course_id_2 in c1.conflicts:
                    c1.conflicts.remove(course_id_2)
                    found = True
                    
                if c2.course_id == course_id_2 and course_id_1 in c2.conflicts:
                    c2.conflicts.remove(course_id_1)
                    found = True

                if not found:
                    return False
            
                if not self.config_model.safe_save():
                    return False

                self.config_model.reload()
                return True

        except Exception:
            return False
        

    def modify_conflict(self, selected_course: CourseConfig, 
                       target_conflict_course: CourseConfig,
                       target_new_course: CourseConfig,
                       modify_mode: int) -> bool:
        """
        Modify an existing conflict by replacing one of the courses.
        
        Mode 1: Replace left course (A-B -> C-B)
        Mode 2: Replace right course (A-B -> A-C)
        
        Parameters:
            selected_course (CourseConfig): The course object being modified
            target_conflict_course (CourseConfig): The current conflict partner
            target_new_course (CourseConfig): The new course to involve in conflict
            modify_mode (int): 1 to replace left side, 2 to replace right side
        
        Returns:
            bool: True if successful, False otherwise
        """
        old_course_id = selected_course.course_id
        conflict_id = target_conflict_course.course_id
        new_course_id = target_new_course.course_id
        
        # Validate mode
        if modify_mode not in (1, 2):
            return False
        
        # Reload to ensure we have latest data
        self.config_model.reload()
        
        try:
            with self.config_model.config.config.edit_mode() as editable:
                # Find the actual course objects in the editable config
                selected_list = [c for c in editable.courses if c.course_id == old_course_id]
                conflict_list = [c for c in editable.courses if c.course_id == conflict_id]
                new_list = [c for c in editable.courses if c.course_id == new_course_id]
                
                if not selected_list or not conflict_list or not new_list:
                    return False
                
                # Validate that conflict exists (check AFTER finding courses in config)
                if conflict_id not in selected_list[0].conflicts:
                    return False
                
                if modify_mode == 1:
                    # A-B -> C-B
                    for course in selected_list:
                        # Remove B from A
                        course.conflicts = [c for c in course.conflicts if c != conflict_id]
                    
                    for course in new_list:
                        # Add B to C
                        if conflict_id not in course.conflicts:
                            course.conflicts.append(conflict_id)
                    
                    for course in conflict_list:
                        # In B, replace A with C
                        updated = [new_course_id if c == old_course_id else c
                                   for c in course.conflicts]
                        course.conflicts = list(dict.fromkeys(updated))
                
                elif modify_mode == 2:
                    # A-B -> A-C
                    for course in selected_list:
                        # In A, replace B with C
                        updated = [new_course_id if c == conflict_id else c
                                   for c in course.conflicts]
                        course.conflicts = list(dict.fromkeys(updated))
                    
                    for course in conflict_list:
                        # Remove A from B
                        course.conflicts = [c for c in course.conflicts if c != old_course_id]
                    
                    for course in new_list:
                        # Add A to C
                        if old_course_id not in course.conflicts:
                            course.conflicts.append(old_course_id)
            
            # Save changes
            if not self.config_model.safe_save():
                return False
            
            self.config_model.reload()
            return True
            
        except Exception:
            return False
    
    def get_all_conflicts(self) -> list[tuple[str, str, int, int]]:
        """
        Get all unique conflict pairs with section indices.

        Parameters:
            None

        Returns:
            list[tuple[str, str, int, int]]: List of (course_id_1, course_id_2, index_1, index_2)
        """
        conflicts = []
        courses = self.config_model.config.config.courses
        for i, course in enumerate(courses):
            for conflict_id in course.conflicts:
                # Find the first matching section index for the conflict partner
                for j, other in enumerate(courses):
                    if other.course_id == conflict_id:
                        pair_key = tuple(sorted([(course.course_id, i), (conflict_id, j)]))
                        entry = (course.course_id, conflict_id, i, j)
                        reverse = (conflict_id, course.course_id, j, i)
                        if entry not in conflicts and reverse not in conflicts:
                            conflicts.append(entry)
                        break
        return conflicts
    
    def conflict_exists(self, course_id_1: str, course_id_2: str) -> bool:
        """
        Check if conflict exists between two courses.
        
        Parameters:
            course_id_1 (str): First course ID
            course_id_2 (str): Second course ID
        
        Returns:
            bool: True if conflict exists, False otherwise
        """
        return any(
            (c1 == course_id_1 and c2 == course_id_2) or
            (c1 == course_id_2 and c2 == course_id_1)
            for c1, c2, i1, i2 in self.get_all_conflicts()
        )
    
    def get_course_by_id(self, course_id: str) -> list[CourseConfig]:
        """
        Get all course instances matching a course ID.
        
        Parameters:
            course_id (str): Course ID to find
        
        Returns:
            list[CourseConfig]: List of matching course objects
        """
        return [
            c for c in self.config_model.config.config.courses
            if c.course_id == course_id
        ]