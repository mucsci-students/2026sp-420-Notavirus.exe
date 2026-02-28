# controllers/faculty_controller.py
"""
FacultyController - Coordinates faculty-related workflows

This controller class manages all faculty workflows including:
- Adding new faculty
- Modifying existing faculty
- Deleting faculty
- Validating faculty data
"""

from scheduler import FacultyConfig, TimeRange

# Constants
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 0
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1


class FacultyController:
    """
    Controller for faculty operations.
    
    Coordinates between FacultyModel (data) and CLIView (UI) to
    implement complete faculty workflows.
    
    Attributes:
        model: FacultyModel instance
        view: CLIView instance
    """
    
    def __init__(self, faculty_model, view):
        """
        Initialize FacultyController.
        
        Parameters:
            faculty_model (FacultyModel): Model for faculty data operations
            view (CLIView): View for user interface
        
        Returns:
            None
        """
        self.model = faculty_model
        self.view = view
    
    def add_faculty(self, faculty_data: dict = None):
        """
        Complete workflow for adding a new faculty member.
        
        Parameters:
            faculty_data (dict, optional): Data from GUI to add directly. If None, it will prompt via CLI view.
        
        Returns:
            bool: True if added successfully, False otherwise
        """
        try:
            # If no data provided, get it from CLI (original behavior)
            if faculty_data is None:
                if not hasattr(self, 'view') or self.view is None:
                    print("Error: No view available to get input.")
                    return False
                    
                # Step 1: Get input from user (CLI)
                faculty_data = self.view.get_faculty_input()
                position = "Full Time" if faculty_data['is_full_time'] else "Adjunct"
                self.view.display_faculty_summary(faculty_data, position)
                if not self.view.confirm("Is this information correct?"):
                    self.view.display_message("Faculty addition cancelled.")
                    return False

            # Step 2: Build FacultyConfig from raw data
            faculty_config = self._build_faculty_config(faculty_data)
            
            # Step 3: Add via model
            success = self.model.add_faculty(faculty_config)
            
            # Step 4: Show result
            if success:
                if hasattr(self, 'view') and self.view is not None:
                    self.view.display_message(f"Faculty '{faculty_data['name']}' added successfully!")
                return True
            else:
                if hasattr(self, 'view') and self.view is not None:
                    self.view.display_error(f"Faculty '{faculty_data['name']}' already exists.")
                return False
        
        except Exception as e:
            if hasattr(self, 'view') and self.view is not None:
                self.view.display_error(f"Failed to add faculty: {e}")
            else:
                print(f"Failed to add faculty: {e}")
            return False
            
    def delete_faculty(self):
        """
        Complete workflow for deleting a faculty member.
        
        Steps:
        1. Display list of faculty
        2. Get faculty name from user
        3. Confirm deletion
        4. Delete via Model
        5. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Display list
            faculty_list = self.model.get_all_faculty()
            if not faculty_list:
                self.view.display_message("No faculty available to delete.")
                return
            
            self.view.display_faculty_list(faculty_list)
            
            # Step 2: Get name
            name = self.view.get_faculty_name_input()
            
            # Check if faculty exists
            faculty = self.model.get_faculty_by_name(name)
            if not faculty:
                self.view.display_error(f"No faculty named '{name}' found.")
                return
            
            # Step 3: Confirm deletion
            if not self.view.confirm(f"Delete {faculty.name}?"):
                self.view.display_message("Deletion cancelled.")
                return
            
            # Step 4: Delete via model
            success = self.model.delete_faculty(name)
            
            # Step 5: Show result
            if success:
                self.view.display_message(f"{faculty.name} deleted successfully.")
            else:
                self.view.display_error(f"Failed to delete {name}.")
        
        except Exception as e:
            self.view.display_error(f"Failed to delete faculty: {e}")
    
    def modify_faculty(self):
        """
        Complete workflow for modifying a faculty member.
        
        Steps:
        1. Display list and get faculty name
        2. Show current information
        3. Get modification choice
        4. Apply modification based on choice
        5. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Get faculty to modify
            faculty_list = self.model.get_all_faculty()
            if not faculty_list:
                self.view.display_message("There are no faculty in the configuration.")
                return
            
            self.view.display_faculty_list(faculty_list)
            faculty_name = self.view.get_faculty_name_input()
            
            # Find faculty
            faculty = self.model.get_faculty_by_name(faculty_name)
            if not faculty:
                self.view.display_error(f"No faculty '{faculty_name}' found. No changes were made.")
                return
            
            # Step 2: Display current information
            position = "Full-time" if faculty.maximum_credits == FULL_TIME_MAX_CREDITS else "Adjunct"
            self.view.display_faculty_details(faculty, position)
            
            # Step 3: Get modification choice
            choice = self.view.get_modify_menu_choice()
            
            if choice == '10':
                self.view.display_message("Modification cancelled.")
                return
            
            # Step 4: Apply modification based on choice
            success = self._handle_modification(faculty_name, choice, faculty)
            
            # Step 5: Display result
            if success:
                self.view.display_message(f"Faculty '{faculty_name}' has been successfully modified.")
            else:
                self.view.display_error("Modification failed.")
        
        except Exception as e:
            self.view.display_error(f"Failed to modify faculty: {e}")
    
    def validate_faculty_references(self):
        """
        Validate and fix faculty references in courses.
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            invalid_count = self.model.validate_faculty_references()
            
            if invalid_count > 0:
                self.view.display_message(f"Fixed {invalid_count} invalid faculty reference(s).")
            else:
                self.view.display_message("All course-faculty references are valid.")
        
        except Exception as e:
            self.view.display_error(f"Failed to validate references: {e}")
    
    def _build_faculty_config(self, data: dict) -> FacultyConfig:
        """
        Build a FacultyConfig object from user input data.
        
        Parameters:
            data (dict): Dictionary containing faculty data from user input
        
        Returns:
            FacultyConfig: Configured faculty object
        """
        # Determine credits and course limit based on position
        if data['is_full_time']:
            max_credits = FULL_TIME_MAX_CREDITS
            unique_course_limit = FULL_TIME_UNIQUE_COURSE_LIMIT
        else:
            max_credits = ADJUNCT_MAX_CREDITS
            unique_course_limit = ADJUNCT_UNIQUE_COURSE_LIMIT
        
        # Build availability times
        times = {}
        day_map = {'M': 'MON', 'T': 'TUE', 'W': 'WED', 'R': 'THU', 'F': 'FRI',
                   'Monday': 'MON', 'Tuesday': 'TUE', 'Wednesday': 'WED', 'Thursday': 'THU', 'Friday': 'FRI'}
        
        # Check if we have the advanced GUI format dictionary
        if 'times' in data:
            # Data from GUI that gives direct time lists
            for day, day_times in data['times'].items():
                if day in day_map:
                    times[day_map[day]] = [TimeRange(start=t['start'], end=t['end']) for t in day_times]
        else:
            # Fallback to CLI basic behavior
            for day in data.get('days', []):
                day_name = day_map.get(day, day)
                times[day_name] = [TimeRange(start='09:00', end='17:00')]
        
        # Create and return FacultyConfig
        return FacultyConfig(
            name=data['name'],
            maximum_credits=max_credits,
            minimum_credits=MIN_CREDITS,
            unique_course_limit=unique_course_limit,
            course_preferences=data.get('course_preferences', {}),
            maximum_days=MAX_DAYS,
            times=times,
            room_preferences={},
            lab_preferences={}
        )
    
    def _handle_modification(self, faculty_name: str, choice: str, faculty) -> bool:
        """
        Handle specific modification based on user's menu choice.
        
        Parameters:
            faculty_name (str): Name of faculty being modified
            choice (str): Menu choice ('1' through '9')
            faculty: Current faculty object for reference
        
        Returns:
            bool: True if modification successful, False otherwise
        """
        if choice == '1':
            # Modify position type
            is_full_time = self.view.get_position_input()
            
            if is_full_time:
                self.model.modify_faculty(faculty_name, 'maximum_credits', FULL_TIME_MAX_CREDITS)
                self.model.modify_faculty(faculty_name, 'unique_course_limit', FULL_TIME_UNIQUE_COURSE_LIMIT)
                if faculty.minimum_credits > FULL_TIME_MAX_CREDITS:
                    self.model.modify_faculty(faculty_name, 'minimum_credits', FULL_TIME_MAX_CREDITS)
            else:
                self.model.modify_faculty(faculty_name, 'maximum_credits', ADJUNCT_MAX_CREDITS)
                self.model.modify_faculty(faculty_name, 'unique_course_limit', ADJUNCT_UNIQUE_COURSE_LIMIT)
                if faculty.minimum_credits > ADJUNCT_MAX_CREDITS:
                    self.model.modify_faculty(faculty_name, 'minimum_credits', ADJUNCT_MAX_CREDITS)
            
            return True
        
        elif choice == '2':
            # Modify maximum credits
            new_max = self.view.get_integer_input(
                "Enter new maximum credits: ",
                min_val=faculty.minimum_credits
            )
            return self.model.modify_faculty(faculty_name, 'maximum_credits', new_max)
        
        elif choice == '3':
            # Modify minimum credits
            new_min = self.view.get_integer_input(
                "Enter new minimum credits: ",
                min_val=0,
                max_val=faculty.maximum_credits
            )
            return self.model.modify_faculty(faculty_name, 'minimum_credits', new_min)
        
        elif choice == '4':
            # Modify unique course limit
            new_limit = self.view.get_integer_input(
                "Enter new unique course limit: ",
                min_val=1
            )
            return self.model.modify_faculty(faculty_name, 'unique_course_limit', new_limit)
        
        elif choice == '5':
            # Modify maximum days
            new_max_days = self.view.get_integer_input(
                "Enter new maximum days (0-5): ",
                min_val=0,
                max_val=5
            )
            return self.model.modify_faculty(faculty_name, 'maximum_days', new_max_days)
        
        elif choice == '6':
            # Modify availability times
            # This is complex and would need more view methods
            # For now, simplified version
            self.view.display_message("Availability time modification not yet implemented in MVC.")
            return False
        
        elif choice == '7':
            # Modify course preferences
            course_prefs = self.view.get_course_preferences_input()
            return self.model.modify_faculty(faculty_name, 'course_preferences', course_prefs)
        
        elif choice == '8':
            # Modify room preferences
            room_prefs = self.view.get_room_preferences_input()
            return self.model.modify_faculty(faculty_name, 'room_preferences', room_prefs)
        
        elif choice == '9':
            # Modify lab preferences
            lab_prefs = self.view.get_lab_preferences_input()
            return self.model.modify_faculty(faculty_name, 'lab_preferences', lab_prefs)
        
        return False