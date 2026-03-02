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
        Add room to configuration (in-memory only).
        Call config_model.safe_save() to persist changes to disk.
        
        Parameters:
            room_name (str): Name of room to add (e.g., "Roddy 140")
        
        Returns:
            bool: True if successful, False if room already exists or name is invalid
        """
        if not room_name or not room_name.strip():
            return False
        if self.room_exists(room_name):
            return False
        self.config_model.config.config.rooms.append(room_name)
        return True
    
    def delete_room(self, room_name: str) -> bool:
        """
        Delete room from configuration (in-memory only).
        Also removes all references to this room from courses and faculty.
        Removes references BEFORE removing from rooms list to avoid validation errors.
        Call config_model.safe_save() to persist changes to disk.
        
        Parameters:
            room_name (str): Name of room to delete
        
        Returns:
            bool: True if successful, False if room not found
        """
        if not self.room_exists(room_name):
            return False
        try:
            for course in self.config_model.config.config.courses:
                course.room = [r for r in course.room if r != room_name]
            for faculty in self.config_model.config.config.faculty:
                if room_name in faculty.room_preferences:
                    del faculty.room_preferences[room_name]
            self.config_model.config.config.rooms = [
                r for r in self.config_model.config.config.rooms if r != room_name
            ]
            return True
        except Exception as e:
            print(f"DEBUG delete_room exception: {e}")
            return False
    
    def modify_room(self, old_name: str, new_name: str) -> bool:
        """
        Modify room name and update all references (in-memory only).
        Call config_model.safe_save() to persist changes to disk.
        
        Parameters:
            old_name (str): Current room name
            new_name (str): New room name
        
        Returns:
            bool: True if successful, False if old room doesn't exist or new name already exists
        """
        if not self.room_exists(old_name):
            return False
        if self.room_exists(new_name):
            return False
        try:
            rooms = self.config_model.config.config.rooms
            index = rooms.index(old_name)
            rooms[index] = new_name
            for course in self.config_model.config.config.courses:
                course.room = [new_name if r == old_name else r for r in course.room]
            for faculty in self.config_model.config.config.faculty:
                if old_name in faculty.room_preferences:
                    faculty.room_preferences[new_name] = faculty.room_preferences.pop(old_name)
            return True
        except Exception as e:
            print(f"DEBUG modify_room exception: {e}")
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