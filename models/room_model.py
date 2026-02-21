# models/room_model.py
"""
RoomModel - Handles room data operations (CRUD)

This model class manages all room-related data operations including:
- Adding rooms to configuration
- Deleting rooms from configuration
- Modifying existing rooms
- Managing room references in courses and faculty
"""


class RoomModel:
    """
    Model class for room data operations.
    
    Attributes:
        config_model: Reference to ConfigModel for file operations
    """
    
    def __init__(self, config_model):
        """
        Initialize RoomModel.
        
        Parameters:
            config_model (ConfigModel): Central configuration model
        
        Returns:
            None
        """
        self.config_model = config_model
    
    def add_room(self, room_name: str) -> bool:
        """
        Add room to configuration.
        
        Parameters:
            room_name (str): Name of room to add (e.g., "Roddy 140")
        
        Returns:
            bool: True if successful, False if room already exists or name is invalid
        """
        # Validate room name
        if not room_name or not room_name.strip():
            return False
        
        # Check if room already exists
        if self.room_exists(room_name):
            return False
        
        # Add room to config
        self.config_model.config.config.rooms.append(room_name)
        
        # Save and reload
        if not self.config_model.safe_save():
            return False
        
        self.config_model.reload()
        return True
    
    def delete_room(self, room_name: str) -> bool:
        """
        Delete room from configuration.
        
        Also removes all references to this room from courses and faculty.
        IMPORTANT: Removes references BEFORE removing from rooms list to avoid validation errors.
        
        Parameters:
            room_name (str): Name of room to delete
        
        Returns:
            bool: True if successful, False if room not found
        """
        if not self.room_exists(room_name):
            return False
        
        try:
            # Remove room references from courses
            for course in self.config_model.config.config.courses:
                course.room = [r for r in course.room if r != room_name]
            
            # Remove room from faculty preferences
            for faculty in self.config_model.config.config.faculty:
                if room_name in faculty.room_preferences:
                    del faculty.room_preferences[room_name]
            
            # NOW remove room from rooms list (do this LAST)
            self.config_model.config.config.rooms = [
                r for r in self.config_model.config.config.rooms if r != room_name
            ]
            
            # Save changes
            if not self.config_model.safe_save():
                return False
            
            self.config_model.reload()
            return True
            
        except Exception:
            return False
    
    def modify_room(self, old_name: str, new_name: str) -> bool:
        """
        Modify room name and update all references.
        
        Updates room name in:
        - Rooms list
        - Course room assignments
        - Faculty room preferences
        
        Parameters:
            old_name (str): Current room name
            new_name (str): New room name
        
        Returns:
            bool: True if successful, False if old room doesn't exist or new name already exists
        """
        # Validate
        if not self.room_exists(old_name):
            return False
        
        if self.room_exists(new_name):
            return False
        
        try:
            with self.config_model.config.config.edit_mode() as editable:
                # Update room name in list
                rooms = editable.rooms
                index = rooms.index(old_name)
                rooms[index] = new_name
                
                # Update course references
                for course in editable.courses:
                    course.room = [new_name if r == old_name else r for r in course.room]
                
                # Update faculty preferences
                for faculty in editable.faculty:
                    if old_name in faculty.room_preferences:
                        faculty.room_preferences[new_name] = faculty.room_preferences.pop(old_name)
            
            # Save changes
            if not self.config_model.safe_save():
                return False
            
            self.config_model.reload()
            return True
            
        except Exception:
            return False
    
    def room_exists(self, room_name: str) -> bool:
        """
        Check if room exists in configuration.
        
        Parameters:
            room_name (str): Room name to check
        
        Returns:
            bool: True if room exists, False otherwise
        """
        return room_name in self.config_model.config.config.rooms
    
    def get_all_rooms(self) -> list[str]:
        """
        Get all rooms from configuration.
        
        Parameters:
            None
        
        Returns:
            list[str]: List of all room names
        """
        return self.config_model.config.config.rooms
    
    def get_affected_courses(self, room_name: str) -> list:
        """
        Get all courses that use this room.
        
        Parameters:
            room_name (str): Room name to search for
        
        Returns:
            list: List of CourseConfig objects that use this room
        """
        return [
            c for c in self.config_model.config.config.courses
            if room_name in c.room
        ]
    
    def get_affected_faculty(self, room_name: str) -> list:
        """
        Get all faculty that have preferences for this room.
        
        Parameters:
            room_name (str): Room name to search for
        
        Returns:
            list: List of FacultyConfig objects with preferences for this room
        """
        return [
            f for f in self.config_model.config.config.faculty
            if room_name in f.room_preferences
        ]