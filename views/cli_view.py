# views/cli_view.py
"""
CLIView - Command-line interface for all user interactions

This view class handles all user input/output for the CLI interface across
all features: faculty, courses, conflicts, labs, rooms, and scheduling.
"""

from scheduler import TimeRange

# Constants
MIN_DAYS = 1
MAX_DAYS = 5


class CLIView:
    """
    Complete CLI implementation for user interface.
    
    Contains methods for:
    - General UI (menus, messages, confirmations)
    - Faculty operations
    - Course operations
    - Conflict operations (to be added)
    - Lab operations (to be added)
    - Room operations (to be added)
    """
    
    # ================================================================
    # GENERAL UI METHODS
    # ================================================================
    
    def display_main_menu(self):
        """
        Display the main scheduler menu.
        
        Parameters:
            None
        
        Returns:
            None
        """
        print("\nScheduler Menu")
        print("1.  Add Faculty")
        print("2.  Modify Faculty")
        print("3.  Delete Faculty")
        print("4.  Add Course")
        print("5.  Modify Course")
        print("6.  Delete Course")
        print("7.  Add Conflict")
        print("8.  Modify Conflict")
        print("9.  Delete Conflict")
        print("10. Add Lab")
        print("11. Modify Lab")
        print("12. Delete Lab")
        print("13. Add Room")
        print("14. Modify Room")
        print("15. Delete Room")
        print("16. Print Configuration")
        print("17. Run Scheduler")
        print("18. Display Schedules")
        print("19. Exit")
    
    def get_menu_choice(self) -> str:
        """
        Get user's menu selection.
        
        Parameters:
            None
        
        Returns:
            str: Menu choice as string
        """
        return input("Choose an option (number only): ").strip()
    
    def confirm(self, message: str) -> bool:
        """
        Get yes/no confirmation from user.
        
        Parameters:
            message (str): Confirmation message to display
        
        Returns:
            bool: True if user confirms (y), False otherwise (n)
        """
        while True:
            response = input(f"{message} [y/n]: ").lower().strip()
            if response in ('y', 'n'):
                return response == 'y'
            print("Please enter 'y' or 'n'.")
    
    def display_message(self, message: str):
        """
        Display success message to user.
        
        Parameters:
            message (str): Message to display
        
        Returns:
            None
        """
        print(f"\n✓ {message}")
    
    def display_error(self, error: str):
        """
        Display error message to user.
        
        Parameters:
            error (str): Error message to display
        
        Returns:
            None
        """
        print(f"\n✗ Error: {error}")
    
    def get_integer_input(self, prompt: str, min_val: int = None, max_val: int = None) -> int:
        """
        Get integer input from user with optional validation.
        
        Parameters:
            prompt (str): Prompt message to display
            min_val (int | None): Minimum allowed value
            max_val (int | None): Maximum allowed value
        
        Returns:
            int: Valid integer input from user
        """
        while True:
            try:
                value = int(input(prompt))
                if min_val is not None and value < min_val:
                    print(f"Value must be at least {min_val}.")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Value must be at most {max_val}.")
                    continue
                return value
            except ValueError:
                print("Please enter a valid number.")
    
    # ================================================================
    # FACULTY-SPECIFIC METHODS
    # ================================================================
    
    def get_faculty_input(self) -> dict:
        """
        Collect faculty information from user via CLI prompts.
        
        Parameters:
            None
        
        Returns:
            dict: Dictionary containing faculty data with keys:
                - name (str)
                - is_full_time (bool)
                - days (list[str])
                - course_preferences (dict)
        """
        data = {}
        
        # Get name
        while True:
            data['name'] = input("Enter the new faculty's name: ").strip()
            if data['name']:
                break
            print("Name cannot be empty.")
        
        # Get position type
        while True:
            is_full_time = input("Does the new faculty have a full-time position? [y/n]: ").lower()
            if is_full_time in ('y', 'n'):
                data['is_full_time'] = (is_full_time == 'y')
                break
            print("Please enter 'y' or 'n'.")
        
        # Get availability days
        while True:
            raw_dates = input("Enter available dates (MTWRF): ").upper()
            dates = []
            for char in raw_dates:
                if char in "MTWRF" and char not in dates:
                    dates.append(char)
            if MIN_DAYS <= len(dates) <= MAX_DAYS:
                data['days'] = dates
                break
            print(f"Please enter between {MIN_DAYS} and {MAX_DAYS} valid days (MTWRF).")
        
        # Get course preferences
        courses = input("Enter preferred courses, separated with a semicolon (Ex. CMSC 161; CMSC 162): ").strip()
        data['course_preferences'] = {}
        if courses:
            for course in courses.split(";"):
                course = course.strip().upper()
                while True:
                    try:
                        weight = int(input(f"Enter a weight for {course} (0-10): "))
                        if 0 <= weight <= 10:
                            data['course_preferences'][course] = weight
                            break
                        print("Please enter a whole number between 0 and 10.")
                    except ValueError:
                        print("Please enter a whole number between 0 and 10.")
        
        return data
    
    def display_faculty_summary(self, faculty_data: dict, position: str):
        """
        Display faculty information for confirmation.
        
        Parameters:
            faculty_data (dict): Dictionary containing faculty data
            position (str): Position type ("Full Time" or "Adjunct")
        
        Returns:
            None
        """
        print("\n" + "="*50)
        print("New Faculty Summary:")
        print("="*50)
        print(f"Name: {faculty_data['name']}")
        print(f"Position Type: {position}")
        print(f"Availability: {', '.join(faculty_data['days'])}")
        print(f"Preferred courses: {faculty_data['course_preferences']}")
        print("="*50)
    
    def display_faculty_list(self, faculty_list):
        """
        Display list of all faculty.
        
        Parameters:
            faculty_list (list): List of FacultyConfig objects
        
        Returns:
            None
        """
        print("\nCurrent Faculty:")
        for i, faculty in enumerate(faculty_list, 1):
            print(f"{i}. {faculty.name}")
    
    def get_faculty_name_input(self) -> str:
        """
        Prompt for faculty name.
        
        Parameters:
            None
        
        Returns:
            str: Faculty name entered by user
        """
        while True:
            name = input("\nEnter the faculty name: ").strip()
            if name:
                return name
            print("Name cannot be empty.")
    
    def display_faculty_details(self, faculty, position: str):
        """
        Display detailed faculty information.
        
        Parameters:
            faculty (FacultyConfig): Faculty object
            position (str): Position type ("Full-time" or "Adjunct")
        
        Returns:
            None
        """
        print("\nCurrent Faculty Information:")
        print(f"Name: {faculty.name}")
        print(f"Position: {position}")
        print(f"Maximum Credits: {faculty.maximum_credits}")
        print(f"Minimum Credits: {faculty.minimum_credits}")
        print(f"Unique Course Limit: {faculty.unique_course_limit}")
        print(f"Maximum Days: {faculty.maximum_days}")
        print(f"Times: {faculty.times}")
        print(f"Course Preferences: {faculty.course_preferences}")
        print(f"Room Preferences: {faculty.room_preferences}")
        print(f"Lab Preferences: {faculty.lab_preferences}")
    
    def get_modify_menu_choice(self) -> str:
        """
        Display modification menu and get user choice.
        
        Parameters:
            None
        
        Returns:
            str: Menu choice ('1' through '10')
        """
        print("\nWhat would you like to modify?")
        print("1. Position (Full-time/Adjunct)")
        print("2. Maximum Credits")
        print("3. Minimum Credits")
        print("4. Unique Course Limit")
        print("5. Maximum Days")
        print("6. Availability Times")
        print("7. Course Preferences")
        print("8. Room Preferences")
        print("9. Lab Preferences")
        print("10. Cancel")
        
        while True:
            choice = input("Choose an option (1-10): ").strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
                return choice
            print("Invalid option. Please choose 1-10.")
    
    def get_position_input(self) -> bool:
        """
        Prompt for position type (full-time or adjunct).
        
        Parameters:
            None
        
        Returns:
            bool: True for full-time, False for adjunct
        """
        print("\nYour input will update the min/max credits, position, and unique course limit accordingly")
        while True:
            position = input("Is this faculty full-time? [y/n]: ").lower().strip()
            if position in ('y', 'n'):
                return position == 'y'
            print("Please enter 'y' or 'n'.")
    
    def get_course_preferences_input(self) -> dict:
        """
        Get course preferences with weights from user.
        
        Parameters:
            None
        
        Returns:
            dict: Dictionary mapping course IDs to weights (0-10)
        """
        courses = input("Enter preferred courses, separated with a semicolon (Ex. CMSC 161; CMSC 162): ").strip()
        course_prefs = {}
        
        if courses:
            for course in courses.split(";"):
                course = course.strip().upper()
                while True:
                    try:
                        weight = int(input(f"Enter a weight for {course} (0-10): "))
                        if 0 <= weight <= 10:
                            course_prefs[course] = weight
                            break
                        print("Please enter a whole number between 0 and 10.")
                    except ValueError:
                        print("Please enter a whole number between 0 and 10.")
        
        return course_prefs
    
    def get_room_preferences_input(self) -> dict:
        """
        Get room preferences with weights from user.
        
        Parameters:
            None
        
        Returns:
            dict: Dictionary mapping room names to weights (0-10)
        """
        rooms = input("Enter preferred rooms, separated with a semicolon (Ex. Roddy 136; Roddy 140): ").strip()
        room_prefs = {}
        
        if rooms:
            for room in rooms.split(";"):
                room = room.strip()
                while True:
                    try:
                        weight = int(input(f"Enter a weight for {room} (0-10): "))
                        if 0 <= weight <= 10:
                            room_prefs[room] = weight
                            break
                        print("Please enter a whole number between 0 and 10.")
                    except ValueError:
                        print("Please enter a whole number between 0 and 10.")
        
        return room_prefs
    
    def get_lab_preferences_input(self) -> dict:
        """
        Get lab preferences with weights from user.
        
        Parameters:
            None
        
        Returns:
            dict: Dictionary mapping lab names to weights (0-10)
        """
        labs = input("Enter preferred labs, separated with a semicolon (Ex. Linux; Mac): ").strip()
        lab_prefs = {}
        
        if labs:
            for lab in labs.split(";"):
                lab = lab.strip()
                while True:
                    try:
                        weight = int(input(f"Enter a weight for {lab} (0-10): "))
                        if 0 <= weight <= 10:
                            lab_prefs[lab] = weight
                            break
                        print("Please enter a whole number between 0 and 10.")
                    except ValueError:
                        print("Please enter a whole number between 0 and 10.")
        
        return lab_prefs
    
    # ================================================================
    # COURSE-SPECIFIC METHODS
    # ================================================================
    
    def get_course_input(self, available_rooms: list, available_labs: list, 
                         available_faculty: list) -> dict:
        """
        Collect course information from user via CLI prompts.
        
        Parameters:
            available_rooms (list): List of available room names
            available_labs (list): List of available lab names
            available_faculty (list): List of available faculty names
        
        Returns:
            dict: Dictionary containing course data with keys:
                - course_id (str)
                - credits (int)
                - rooms (list)
                - labs (list)
                - faculty (list)
                - conflicts (list)
        """
        data = {}
        
        # Get course ID
        while True:
            data['course_id'] = input("Enter the course ID (Ex. CMSC161): ").strip().upper()
            if data['course_id']:
                break
            print("Course ID cannot be empty.")
        
        # Get credits
        while True:
            try:
                credits = int(input("Enter the number of credits (1-4): "))
                if 1 <= credits <= 4:
                    data['credits'] = credits
                    break
                print("Please enter a number between 1 and 4.")
            except ValueError:
                print("Please enter a whole number.")
        
        # Get rooms
        print(f"Available rooms: {', '.join(available_rooms)}")
        data['rooms'] = []
        while True:
            room = input("Enter a room for this course (or press Enter to skip): ").strip()
            if room == "":
                break
            if room not in available_rooms:
                print(f"Invalid room. Choose from: {', '.join(available_rooms)}")
                continue
            if room not in data['rooms']:
                data['rooms'].append(room)
        
        # Get labs
        print(f"Available labs: {', '.join(available_labs)}")
        data['labs'] = []
        while True:
            lab = input("Enter a lab for this course (or press Enter to skip/finish): ").strip()
            if lab == "":
                break
            if lab not in available_labs:
                print(f"Invalid lab. Choose from: {', '.join(available_labs)}")
                continue
            if lab not in data['labs']:
                data['labs'].append(lab)
        
        # Get faculty
        print(f"Available faculty: {', '.join(available_faculty)}")
        data['faculty'] = []
        while True:
            f = input("Enter a faculty member for this course (or press Enter to finish): ").strip()
            if f == "":
                if len(data['faculty']) == 0:
                    print("Please enter at least one faculty member.")
                    continue
                break
            if f not in available_faculty:
                print(f"Invalid faculty. Choose from: {', '.join(available_faculty)}")
                continue
            if f not in data['faculty']:
                data['faculty'].append(f)
        
        # Get conflicts
        data['conflicts'] = []
        while True:
            conflict = input("Enter a conflicting course ID (or press Enter to finish): ").strip().upper()
            if conflict == "":
                break
            if conflict == data['course_id']:
                print("A course cannot conflict with itself.")
                continue
            if conflict not in data['conflicts']:
                data['conflicts'].append(conflict)
        
        return data
    
    def display_course_summary(self, course_data: dict):
        """
        Display course information for confirmation.
        
        Parameters:
            course_data (dict): Dictionary containing course data
        
        Returns:
            None
        """
        print("\nNew Course Summary:")
        print(f"Course ID: {course_data['course_id']}")
        print(f"Credits:   {course_data['credits']}")
        print(f"Rooms:     {course_data['rooms']}")
        print(f"Labs:      {course_data['labs']}")
        print(f"Faculty:   {course_data['faculty']}")
        print(f"Conflicts: {course_data['conflicts']}")
    
    def display_course_list(self, courses_with_sections: list):
        """
        Display list of all courses with section labels.
        
        Parameters:
            courses_with_sections (list): List of (label, index, course) tuples
        
        Returns:
            None
        """
        print("\nExisting Courses:")
        for i, (label, _, course) in enumerate(courses_with_sections, 1):
            print(f"{i}. {label} ({course.credits} credits)")
    
    def get_course_id_input(self) -> str:
        """
        Prompt for course ID.
        
        Parameters:
            None
        
        Returns:
            str: Course ID entered by user
        """
        while True:
            course_id = input("\nEnter the full course ID: ").strip().upper()
            if course_id:
                return course_id
            print("Course ID cannot be empty.")
    
    def get_course_section_input(self, valid_labels: dict) -> str:
        """
        Prompt for course section (e.g., "CMSC 340.01").
        
        Parameters:
            valid_labels (dict): Dictionary mapping section labels to indices
        
        Returns:
            str: Valid section label entered by user
        """
        while True:
            course_input = input("\nEnter the course section (e.g. CMSC 340.01): ").strip().upper()
            if course_input in valid_labels:
                return course_input
            print("Invalid section. Please enter a section exactly as shown above.")
    
    def display_course_details(self, course):
        """
        Display detailed course information.
        
        Parameters:
            course (CourseConfig): Course object
        
        Returns:
            None
        """
        print("\nCourse Details:")
        print(f"Course ID: {course.course_id}")
        print(f"Credits:   {course.credits}")
        print(f"Rooms:     {course.room}")
        print(f"Labs:      {course.lab}")
        print(f"Faculty:   {course.faculty}")
        print(f"Conflicts: {course.conflicts}")
    
    def get_course_modifications(self) -> dict:
        """
        Prompt for course field modifications.
        
        Returns empty strings for unchanged fields.
        
        Parameters:
            None
        
        Returns:
            dict: Dictionary with modification data (empty strings for unchanged)
        """
        print("\nEnter new values or press Enter to keep existing ones.")
        
        return {
            'credits': input("New credit value: ").strip(),
            'room': input("New room (comma separated): ").strip(),
            'lab': input("New lab (comma separated): ").strip(),
            'faculty': input("New faculty (comma separated, prefix with - to remove): ").strip()
        }
    
    def display_modification_summary(self, course_id: str, modifications: dict):
        """
        Display summary of modifications before applying.
        
        Parameters:
            course_id (str): Course ID being modified
            modifications (dict): Dictionary of modifications
        
        Returns:
            None
        """
        print("\nModification Summary:")
        print(f"Course: {course_id}")
        print(f"Credits: {modifications['credits'] if modifications['credits'] else '[unchanged]'}")
        print(f"Room: {modifications['room'] if modifications['room'] else '[unchanged]'}")
        print(f"Lab: {modifications['lab'] if modifications['lab'] else '[unchanged]'}")
        print(f"Faculty: {modifications['faculty'] if modifications['faculty'] else '[unchanged]'}")
    
    # ================================================================
    # CONFLICT-SPECIFIC METHODS 
    # ================================================================
    
    def display_conflict_list(self, courses: list, existing_conflicts: list):
        """
        Display existing courses and conflicts.
        
        Parameters:
            courses (list): List of CourseConfig objects
            existing_conflicts (list): List of conflict tuples
        
        Returns:
            None
        """
        print("\nExisting Courses:")
        for course in courses:
            print(f"- {course.course_id}")
        
        print("\nExisting Conflicts:")
        if existing_conflicts:
            for i, (a, b) in enumerate(existing_conflicts, 1):
                print(f"{i}. {a} <-> {b}")
        else:
            print("No conflicts exist.")
    
    def get_conflict_input(self, courses: list) -> tuple[str, str]:
        """
        Get two course IDs for a conflict from user.
        
        Parameters:
            courses (list): List of available CourseConfig objects
        
        Returns:
            tuple[str, str]: Tuple of (course_id_1, course_id_2)
        """
        valid_ids = {c.course_id for c in courses}
        
        # Get first course
        while True:
            course_1 = input("\nEnter the first course ID: ").strip().upper()
            if not course_1:
                print("Course ID cannot be empty.")
                continue
            if course_1 not in valid_ids:
                print(f"Course '{course_1}' not found.")
                continue
            break
        
        # Get second course
        while True:
            course_2 = input("Enter the conflicting course ID: ").strip().upper()
            if not course_2:
                print("Course ID cannot be empty.")
                continue
            if course_2 not in valid_ids:
                print(f"Course '{course_2}' not found.")
                continue
            break
        
        return (course_1, course_2)
    
    def display_conflict_summary(self, course_id_1: str, course_id_2: str):
        """
        Display conflict summary for confirmation.
        
        Parameters:
            course_id_1 (str): First course ID
            course_id_2 (str): Second course ID
        
        Returns:
            None
        """
        print("\nConflict Summary:")
        print(f"- {course_id_1} conflicts with {course_id_2}")
    
    def display_existing_conflicts(self, conflicts: list):
        """
        Display list of existing conflicts.
        
        Parameters:
            conflicts (list): List of conflict tuples (course_id_1, course_id_2)
        
        Returns:
            None
        """
        print("\nExisting Conflicts:")
        for i, (a, b) in enumerate(conflicts, 1):
            print(f"{i}. {a} <-> {b}")
    
    def get_course_id_for_conflict(self, position: str) -> str:
        """
        Prompt for a course ID for conflict operations.
        
        Parameters:
            position (str): Description of which course ("first", "conflicting", etc.)
        
        Returns:
            str: Course ID entered by user
        """
        while True:
            course_id = input(f"\nEnter the {position} course ID (e.g. 'CMSC 340'): ").strip().upper()
            if course_id:
                return course_id
            print("Course ID cannot be empty.")
    
    def display_numbered_conflicts(self, conflicts: list):
        """
        Display numbered list of conflicts for selection.
        
        Parameters:
            conflicts (list): List of (course, conflict_str) tuples
        
        Returns:
            None
        """
        print("Existing Conflicts:")
        for i, (course, conflict_str) in enumerate(conflicts, 1):
            print(f"{i}: {course.course_id} conflicts with {conflict_str}")
    
    def get_conflict_selection(self, max_num: int) -> int:
        """
        Get user's conflict selection from numbered list.
        
        Parameters:
            max_num (int): Maximum valid selection number
        
        Returns:
            int: Zero-based index of selected conflict
        """
        while True:
            selection = input(f"Which conflict would you like to modify? [1-{max_num}]: ").strip()
            if selection.isnumeric() and 1 <= int(selection) <= max_num:
                return int(selection) - 1
            print(f"Please enter a number between 1 and {max_num}.")
    
    def select_course_instance(self, course_id: str, candidates: list, prompt: str):
        """
        Select a specific course instance if multiple sections exist.
        
        Parameters:
            course_id (str): Course ID being selected
            candidates (list): List of CourseConfig objects matching the ID
            prompt (str): Prompt message for user
        
        Returns:
            CourseConfig | None: Selected course object, or None if not found
        """
        if not candidates:
            return None
        
        if len(candidates) == 1:
            return candidates[0]
        
        print(f"\nMultiple sections found for {course_id}. Please select specific instance:")
        for i, c in enumerate(candidates, 1):
            info = f"Credits: {c.credits}"
            if hasattr(c, 'faculty') and c.faculty:
                info += f", Faculty: {c.faculty}"
            print(f"{i}: {c.course_id} ({info})")
        
        while True:
            try:
                selection = int(input(f"{prompt} [1-{len(candidates)}]: ").strip())
                if 1 <= selection <= len(candidates):
                    return candidates[selection - 1]
            except ValueError:
                pass
            print("Invalid selection. Please try again.")
    
    def display_conflict_pair(self, course_id_1: str, course_id_2: str):
        """
        Display the two courses in a conflict pair.
        
        Parameters:
            course_id_1 (str): First course ID
            course_id_2 (str): Second course ID
        
        Returns:
            None
        """
        print("\nCourses in Conflict:")
        print(f"1: {course_id_1}")
        print(f"2: {course_id_2}")
    
    def get_modify_side_choice(self) -> int:
        """
        Get user's choice of which side of conflict to modify.
        
        Parameters:
            None
        
        Returns:
            int: 1 or 2 indicating which course to replace
        """
        while True:
            choice = input("Which course would you like to modify? [1/2]: ").strip()
            if choice in ('1', '2'):
                return int(choice)
            print("Please enter 1 or 2.")
    
    def get_replacement_course_id(self, current_course_id: str) -> str:
        """
        Get the new course ID to replace the current one.
        
        Parameters:
            current_course_id (str): Current course ID being replaced
        
        Returns:
            str: New course ID entered by user
        """
        return input(f"Replace course {current_course_id} with (Enter Course ID): ").strip().upper()

    # ================================================================
    # LAB-SPECIFIC METHODS 
    # ================================================================
    
    def display_lab_list(self, labs: list):
        """
        Display list of current labs.
        
        Parameters:
            labs (list): List of lab names
        
        Returns:
            None
        """
        if labs:
            print(f"Current labs: {', '.join(labs)}")
        else:
            print("No labs currently exist.")
    
    def get_lab_name_input(self) -> str:
        """
        Prompt for lab name.
        
        Parameters:
            None
        
        Returns:
            str: Lab name entered by user
        """
        while True:
            name = input("Enter the lab name: ").strip()
            if name:
                return name
            print("Lab name cannot be empty.")
    
    def display_numbered_labs(self, labs: list):
        """
        Display numbered list of labs for selection.
        
        Parameters:
            labs (list): List of lab names
        
        Returns:
            None
        """
        print("Which lab would you like to delete?")
        for i, lab in enumerate(labs, 1):
            print(f"{i}: {lab}")
    
    def get_lab_selection(self, max_num: int) -> int:
        """
        Get user's lab selection from numbered list.
        
        Returns -1 if user wants to quit.
        
        Parameters:
            max_num (int): Maximum valid selection number
        
        Returns:
            int: Zero-based index of selected lab, or -1 to quit
        """
        while True:
            labnum = input("\nEnter the number of the lab you would like to delete (-1 to quit): ").strip()
            
            # Check for quit
            if labnum == "-1":
                return -1
            
            # Validate numeric and in range
            if labnum.isnumeric():
                num = int(labnum)
                if 1 <= num <= max_num:
                    return num - 1  # Return zero-based index
            
            print(f"Please enter a number between 1 and {max_num}, or -1 to quit.")
    
    def get_lab_to_modify(self, available_labs: list) -> str | None:
        """
        Get the lab name to modify from user.
        
        Parameters:
            available_labs (list): List of available lab names
        
        Returns:
            str | None: Lab name to modify, or None if cancelled
        """
        while True:
            old_name = input("Enter the name of the lab you would like to modify (or press Enter to cancel): ").strip()
            
            if old_name == "":
                return None
            
            if old_name not in available_labs:
                print(f"Error: Lab '{old_name}' does not exist.")
                print(f"Available Labs: {', '.join(available_labs)}")
                continue
            
            return old_name
    
    def get_new_lab_name(self, old_name: str, existing_labs: list) -> str | None:
        """
        Get the new lab name from user.
        
        Parameters:
            old_name (str): Current lab name
            existing_labs (list): List of existing lab names
        
        Returns:
            str | None: New lab name, or None if invalid
        """
        while True:
            new_name = input(f"Enter the new name of the lab '{old_name}': ").strip()
            
            if new_name == "":
                print("Lab name cannot be empty.")
                continue
            
            if new_name in existing_labs:
                print(f"Error: Lab '{new_name}' already exists.")
                continue
            
            return new_name
    
    def display_lab_modification_summary(self, old_name: str, new_name: str,
                                         affected_courses: list, affected_faculty: list):
        """
        Display summary of lab modification and affected items.
        
        Parameters:
            old_name (str): Current lab name
            new_name (str): New lab name
            affected_courses (list): List of affected CourseConfig objects
            affected_faculty (list): List of affected FacultyConfig objects
        
        Returns:
            None
        """
        print(f"\nThis will update:")
        print(f"  - Lab name '{old_name}' -> '{new_name}'")
        
        if affected_courses:
            course_ids = ', '.join(c.course_id for c in affected_courses)
            print(f"  - {len(affected_courses)} course(s): {course_ids}")
        
        if affected_faculty:
            faculty_names = ', '.join(f.name for f in affected_faculty)
            print(f"  - {len(affected_faculty)} faculty: {faculty_names}")
    
    # ================================================================
    # ROOM-SPECIFIC METHODS 
    # ================================================================


    def display_lab_list(self, labs: list):
        """
        Display list of current labs.
        
        Parameters:
            labs (list): List of lab names
        
        Returns:
            None
        """
        if labs:
            print(f"Current labs: {', '.join(labs)}")
        else:
            print("No labs currently exist.")
    
    def get_lab_name_input(self) -> str:
        """
        Prompt for lab name.
        
        Parameters:
            None
        
        Returns:
            str: Lab name entered by user
        """
        while True:
            name = input("Enter the lab name: ").strip()
            if name:
                return name
            print("Lab name cannot be empty.")
    
    def display_numbered_labs(self, labs: list):
        """
        Display numbered list of labs for selection.
        
        Parameters:
            labs (list): List of lab names
        
        Returns:
            None
        """
        print("Which lab would you like to delete?")
        for i, lab in enumerate(labs, 1):
            print(f"{i}: {lab}")
    
    def get_lab_selection(self, max_num: int) -> int:
        """
        Get user's lab selection from numbered list.
        
        Returns -1 if user wants to quit.
        
        Parameters:
            max_num (int): Maximum valid selection number
        
        Returns:
            int: Zero-based index of selected lab, or -1 to quit
        """
        while True:
            labnum = input("\nEnter the number of the lab you would like to delete (-1 to quit): ").strip()
            
            # Check for quit
            if labnum == "-1":
                return -1
            
            # Validate numeric and in range
            if labnum.isnumeric():
                num = int(labnum)
                if 1 <= num <= max_num:
                    return num - 1  # Return zero-based index
            
            print(f"Please enter a number between 1 and {max_num}, or -1 to quit.")
    
    def get_lab_to_modify(self, available_labs: list) -> str | None:
        """
        Get the lab name to modify from user.
        
        Parameters:
            available_labs (list): List of available lab names
        
        Returns:
            str | None: Lab name to modify, or None if cancelled
        """
        while True:
            old_name = input("Enter the name of the lab you would like to modify (or press Enter to cancel): ").strip()
            
            if old_name == "":
                return None
            
            if old_name not in available_labs:
                print(f"Error: Lab '{old_name}' does not exist.")
                print(f"Available Labs: {', '.join(available_labs)}")
                continue
            
            return old_name
    
    def get_new_lab_name(self, old_name: str, existing_labs: list) -> str | None:
        """
        Get the new lab name from user.
        
        Parameters:
            old_name (str): Current lab name
            existing_labs (list): List of existing lab names
        
        Returns:
            str | None: New lab name, or None if invalid
        """
        while True:
            new_name = input(f"Enter the new name of the lab '{old_name}': ").strip()
            
            if new_name == "":
                print("Lab name cannot be empty.")
                continue
            
            if new_name in existing_labs:
                print(f"Error: Lab '{new_name}' already exists.")
                continue
            
            return new_name
    
    def display_lab_modification_summary(self, old_name: str, new_name: str,
                                         affected_courses: list, affected_faculty: list):
        """
        Display summary of lab modification and affected items.
        
        Parameters:
            old_name (str): Current lab name
            new_name (str): New lab name
            affected_courses (list): List of affected CourseConfig objects
            affected_faculty (list): List of affected FacultyConfig objects
        
        Returns:
            None
        """
        print(f"\nThis will update:")
        print(f"  - Lab name '{old_name}' -> '{new_name}'")
        
        if affected_courses:
            course_ids = ', '.join(c.course_id for c in affected_courses)
            print(f"  - {len(affected_courses)} course(s): {course_ids}")
        
        if affected_faculty:
            faculty_names = ', '.join(f.name for f in affected_faculty)
            print(f"  - {len(affected_faculty)} faculty: {faculty_names}")
    
    # ================================================================
    # ROOM-SPECIFIC METHODS
    # ================================================================
    
    def get_room_input(self) -> str:
        """
        Get complete room name (building + number) from user.
        
        Parameters:
            None
        
        Returns:
            str: Full room name (e.g., "Roddy 140")
        """
        building = self.get_room_building_input()
        number = self.get_room_number_input()
        return f"{building.capitalize()} {number}"
    
    def get_room_building_input(self) -> str:
        """
        Prompt for room building name.
        
        Validates that building name has no spaces and is not empty.
        
        Parameters:
            None
        
        Returns:
            str: Building name entered by user
        """
        while True:
            building = input("Building?: ").strip()
            
            if " " in building:
                print("Building name cannot contain spaces.")
                continue
            
            if building == "":
                print("Building name cannot be empty.")
                continue
            
            return building
    
    def get_room_number_input(self) -> str:
        """
        Prompt for room number.
        
        Validates that input is a number.
        
        Parameters:
            None
        
        Returns:
            str: Room number entered by user
        """
        while True:
            room_num = input("Room number?: ").strip()
            if room_num.isdigit():
                return room_num
            print("Not a number, try again.")
    
    def display_numbered_rooms(self, rooms: list):
        """
        Display numbered list of rooms.
        
        Parameters:
            rooms (list): List of room names
        
        Returns:
            None
        """
        print("\nExisting Rooms:")
        for i, room in enumerate(rooms, 1):
            print(f"{i}. {room}")
    
    def get_room_name_for_deletion(self) -> str:
        """
        Prompt for room name to delete.
        
        Parameters:
            None
        
        Returns:
            str: Room name entered by user
        """
        while True:
            room_name = input("\nEnter the room name to delete: ").strip()
            if room_name:
                return room_name
            print("Room name cannot be empty.")
    
    def get_room_modify_choice(self) -> str:
        """
        Ask user which part of room to modify (building or number).
        
        Parameters:
            None
        
        Returns:
            str: "building" or "number"
        """
        while True:
            answer = input("What part do you want to modify (building/number)?: ").strip().lower()
            if answer in ("building", "number"):
                return answer
            print("Not a valid answer. Please enter 'building' or 'number'.")

    # ================================================================
    # SCHEDULER-SPECIFIC METHODS
    # ================================================================
    
    def get_schedule_limit(self) -> int:
        """
        Prompt for maximum number of schedules to generate.
        
        Parameters:
            None
        
        Returns:
            int: Schedule limit (positive integer)
        """
        while True:
            try:
                limit_input = input("What is the max number of schedules you want generated? ").strip()
                limit = int(limit_input)
                
                if limit <= 0:
                    print("Please enter a positive number.")
                    continue
                
                return limit
            except ValueError:
                print("Invalid input. Please enter a valid number.")
    
    def get_output_filename(self) -> str:
        """
        Prompt for output filename (without extension).
        
        Parameters:
            None
        
        Returns:
            str: Filename entered by user
        """
        return input("What do you want to call the output file? (without extension): ").strip()
    
    def get_output_format(self) -> bool:
        """
        Prompt for output format (CSV or JSON).
        
        Parameters:
            None
        
        Returns:
            bool: True for CSV, False for JSON
        """
        while True:
            format_input = input("What output file format do you prefer? (csv/json): ").strip().lower()
            if format_input == 'csv':
                return True
            elif format_input == 'json':
                return False
            print("Invalid input. Please enter 'csv' or 'json'.")
    
    def display_configuration(self, config):
        """
        Display the configuration file in human-readable format.
        
        Parameters:
            config (CombinedConfig): Configuration to display
        
        Returns:
            None
        """
        print("\n" + "=" * 80)
        print(" CONFIGURATION FILE CONTENTS")
        print("=" * 80)
        
        # Display general settings
        print("\nGENERAL SETTINGS:")
        print(f"  Schedule Limit: {config.limit}")
        if hasattr(config, 'optimizer_flags') and config.optimizer_flags:
            print(f"  Optimizer Flags: {', '.join(config.optimizer_flags)}")
        
        # Display courses
        print("\nCOURSES:")
        if config.config.courses:
            print(f"  {'Course ID':<15} {'Credits':<10} {'Rooms':<30} {'Labs':<20} {'Conflicts'}")
            print("  " + "-" * 100)
            for course in config.config.courses:
                course_id = course.course_id if hasattr(course, 'course_id') else "N/A"
                credits = course.credits if hasattr(course, 'credits') else "N/A"
                
                # Handle rooms
                rooms = "N/A"
                if hasattr(course, 'room') and course.room:
                    rooms = ", ".join(course.room) if isinstance(course.room, list) else str(course.room)
                
                # Handle labs
                labs = "N/A"
                if hasattr(course, 'lab') and course.lab:
                    labs = ", ".join(course.lab) if isinstance(course.lab, list) else str(course.lab)
                
                # Handle conflicts
                conflicts = "None"
                if hasattr(course, 'conflicts') and course.conflicts:
                    conflicts = ", ".join(course.conflicts) if isinstance(course.conflicts, list) else str(course.conflicts)
                
                # Truncate long strings for display
                rooms_display = rooms[:28] + ".." if len(rooms) > 30 else rooms
                labs_display = labs[:18] + ".." if len(labs) > 20 else labs
                conflicts_display = conflicts[:30] + ".." if len(conflicts) > 32 else conflicts
                
                print(f"  {course_id:<15} {credits:<10} {rooms_display:<30} {labs_display:<20} {conflicts_display}")
        else:
            print("  No courses configured.")
        
        # Display faculty
        print("\nFACULTY:")
        if config.config.faculty:
            print(f"  {'Name':<15} {'Max Credits':<12} {'Min Credits':<12} {'Unique Limit':<13} {'Max Days':<10} {'Mandatory Days'}")
            print("  " + "-" * 100)
            for faculty in config.config.faculty:
                name = faculty.name if hasattr(faculty, 'name') else "N/A"
                max_cred = faculty.maximum_credits if hasattr(faculty, 'maximum_credits') else "N/A"
                min_cred = faculty.minimum_credits if hasattr(faculty, 'minimum_credits') else "N/A"
                unique = faculty.unique_course_limit if hasattr(faculty, 'unique_course_limit') else "N/A"
                max_days = faculty.maximum_days if hasattr(faculty, 'maximum_days') else "N/A"
                
                # Handle mandatory days
                mandatory = "None"
                if hasattr(faculty, 'mandatory_days') and faculty.mandatory_days:
                    mandatory = ", ".join(faculty.mandatory_days)
                
                print(f"  {name:<15} {str(max_cred):<12} {str(min_cred):<12} {str(unique):<13} {str(max_days):<10} {mandatory}")
            
            # Display faculty preferences summary
            print("\n  FACULTY PREFERENCES:")
            for faculty in config.config.faculty:
                name = faculty.name if hasattr(faculty, 'name') else "Unknown"
                print(f"\n    {name}:")
                
                # Course preferences
                if hasattr(faculty, 'course_preferences') and faculty.course_preferences:
                    prefs = ", ".join([f"{k}({v})" for k, v in faculty.course_preferences.items()])
                    print(f"      Courses: {prefs}")
                
                # Room preferences
                if hasattr(faculty, 'room_preferences') and faculty.room_preferences:
                    prefs = ", ".join([f"{k}({v})" for k, v in faculty.room_preferences.items()])
                    print(f"      Rooms: {prefs}")
                
                # Lab preferences
                if hasattr(faculty, 'lab_preferences') and faculty.lab_preferences:
                    prefs = ", ".join([f"{k}({v})" for k, v in faculty.lab_preferences.items()])
                    print(f"      Labs: {prefs}")
        else:
            print("  No faculty configured.")
        
        # Display rooms
        print("\nROOMS:")
        if config.config.rooms:
            for room in config.config.rooms:
                print(f"  - {room}")
        else:
            print("  No rooms configured.")
        
        # Display labs
        print("\nLABS:")
        if hasattr(config.config, 'labs') and config.config.labs:
            for lab in config.config.labs:
                print(f"  - {lab}")
        else:
            print("  No labs configured.")
        
        # Display time slot patterns
        print("\nTIME SLOT PATTERNS:")
        if hasattr(config, 'time_slot_config') and hasattr(config.time_slot_config, 'classes'):
            for i, pattern in enumerate(config.time_slot_config.classes, 1):
                credits = pattern.credits if hasattr(pattern, 'credits') else "N/A"
                disabled = " [DISABLED]" if hasattr(pattern, 'disabled') and pattern.disabled else ""
                print(f"  Pattern {i} ({credits} credits){disabled}:")
                
                if hasattr(pattern, 'meetings') and pattern.meetings:
                    for meeting in pattern.meetings:
                        day = meeting.day if hasattr(meeting, 'day') else "N/A"
                        duration = meeting.duration if hasattr(meeting, 'duration') else "N/A"
                        lab = " [LAB]" if hasattr(meeting, 'lab') and meeting.lab else ""
                        print(f"    - {day}: {duration} min{lab}")
                
                if hasattr(pattern, 'start_time') and pattern.start_time:
                    print(f"    Start Time: {pattern.start_time}")
        else:
            print("  No time slot patterns configured.")
        
        print("\n" + "=" * 80)
    
    def display_schedules_csv(self, schedules, max_schedules: int):
        """
        Display schedules in CSV format to terminal.
        
        Parameters:
            schedules: Generator of schedule models
            max_schedules (int): Maximum schedules to display
        
        Returns:
            None
        """
        count = 0
        for model in schedules:
            count += 1
            print(f"\nSchedule {count}")
            for course in model:
                try:
                    print(course.as_csv())
                except Exception:
                    # Fallback
                    try:
                        print(course.model_dump_json())
                    except Exception:
                        print(str(course))
            print()  # Blank line between schedules
            
            if count >= max_schedules:
                break
        
        if count == 0:
            print("No valid schedule could be generated.")
    
    def display_schedules_terminal(self, schedules):
        """
        Display schedules in CSV format to terminal (console-only mode).
        
        Parameters:
            schedules: Generator of schedule models
        
        Returns:
            None
        """
        for model in schedules:
            for course in model:
                print(course.as_csv())
            print()  # Blank line between schedules
