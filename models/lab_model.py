# models/lab_model.py
"""
LabModel - Handles lab data operations (CRUD)

This model class manages all lab-related data operations including:
- Adding labs to configuration
- Deleting labs from configuration
- Modifying existing labs
- Managing lab references in courses and faculty
"""


class LabModel:
    """
    Model class for lab data operations.
    
    Attributes:
        config_model: Reference to ConfigModel for file operations
    """
    
    def __init__(self, config_model):
        """
        Initialize LabModel.
        
        Parameters:
            config_model (ConfigModel): Central configuration model
        
        Returns:
            None
        """
        self.config_model = config_model
    
    def add_lab(self, lab_name: str) -> bool:
        """
        Add lab to configuration.
        
        Parameters:
            lab_name (str): Name of lab to add
        
        Returns:
            bool: True if successful, False if lab already exists
        """
        # Check if lab already exists
        if self.lab_exists(lab_name):
            return False
        
        # Add lab to config
        self.config_model.config.config.labs.append(lab_name)
        
        # Save and reload
        if not self.config_model.safe_save():
            return False
        
        self.config_model.reload()
        return True
    
    def delete_lab(self, lab_name: str) -> bool:
        """
        Delete lab from configuration.
        
        Also removes all references to this lab from courses and faculty.
        
        Parameters:
            lab_name (str): Name of lab to delete
        
        Returns:
            bool: True if successful, False if lab not found
        """
        if not self.lab_exists(lab_name):
            return False
        
        try:
            with self.config_model.config.config.edit_mode() as editable:
                # Remove lab references from courses
                for course in editable.courses:
                    if lab_name in course.lab:
                        course.lab.remove(lab_name)
                
                # Remove lab from faculty preferences
                for faculty in editable.faculty:
                    if lab_name in faculty.lab_preferences:
                        del faculty.lab_preferences[lab_name]
                
                # Remove lab from labs list
                editable.labs.remove(lab_name)
            
            # Save changes
            if not self.config_model.safe_save():
                return False
            
            self.config_model.reload()
            return True
            
        except Exception:
            return False
    
    def modify_lab(self, old_name: str, new_name: str) -> bool:
        """
        Modify lab name and update all references.
        
        Updates lab name in:
        - Labs list
        - Course lab assignments
        - Faculty lab preferences
        
        Parameters:
            old_name (str): Current lab name
            new_name (str): New lab name
        
        Returns:
            bool: True if successful, False if old lab doesn't exist or new name already exists
        """
        # Validate
        if not self.lab_exists(old_name):
            return False
        
        if self.lab_exists(new_name):
            return False
        
        try:
            # Update lab name in list
            labs = self.config_model.config.config.labs
            index = labs.index(old_name)
            labs[index] = new_name
            
            # Update course references
            for course in self.config_model.config.config.courses:
                if old_name in course.lab:
                    course.lab = [new_name if lab == old_name else lab for lab in course.lab]
            
            # Update faculty preferences
            for faculty in self.config_model.config.config.faculty:
                if old_name in faculty.lab_preferences:
                    faculty.lab_preferences[new_name] = faculty.lab_preferences.pop(old_name)
            
            # Save changes
            if not self.config_model.safe_save():
                return False
            
            self.config_model.reload()
            return True
            
        except Exception:
            return False
    
    def lab_exists(self, lab_name: str) -> bool:
        """
        Check if lab exists in configuration.
        
        Parameters:
            lab_name (str): Lab name to check
        
        Returns:
            bool: True if lab exists, False otherwise
        """
        return lab_name in self.config_model.config.config.labs
    
    def get_all_labs(self) -> list[str]:
        """
        Get all labs from configuration.
        
        Parameters:
            None
        
        Returns:
            list[str]: List of all lab names
        """
        return self.config_model.config.config.labs
    
    def get_affected_courses(self, lab_name: str) -> list:
        """
        Get all courses that use this lab.
        
        Parameters:
            lab_name (str): Lab name to search for
        
        Returns:
            list: List of CourseConfig objects that use this lab
        """
        return [
            c for c in self.config_model.config.config.courses
            if lab_name in c.lab
        ]
    
    def get_affected_faculty(self, lab_name: str) -> list:
        """
        Get all faculty that have preferences for this lab.
        
        Parameters:
            lab_name (str): Lab name to search for
        
        Returns:
            list: List of FacultyConfig objects with preferences for this lab
        """
        return [
            f for f in self.config_model.config.config.faculty
            if lab_name in f.lab_preferences
        ]