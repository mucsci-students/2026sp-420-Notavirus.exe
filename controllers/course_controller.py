# controllers/course_controller.py
"""
CourseController - Coordinates course-related workflows

This controller class manages all course workflows including:
- Adding new courses
- Modifying existing courses
- Deleting courses
- Validating course data
"""

from scheduler import CourseConfig


class CourseController:
    """
    Controller for course operations.
    
    Coordinates between CourseModel (data) and CLIView (UI) to
    implement complete course workflows.
    
    Attributes:
        model: CourseModel instance
        view: CLIView instance
        config_model: ConfigModel instance (for getting available items)
    """
    
    def __init__(self, course_model, view, config_model):
        """
        Initialize CourseController.
        
        Parameters:
            course_model (CourseModel): Model for course data operations
            view (CLIView): View for user interface
            config_model (ConfigModel): Config model for accessing rooms/labs/faculty
        
        Returns:
            None
        """
        self.model = course_model
        self.view = view
        self.config_model = config_model
    
    def add_course(self):
        """
        Complete workflow for adding a new course.
        
        Steps:
        1. Get available rooms, labs, faculty
        2. Get user input via View
        3. Build CourseConfig object
        4. Display summary and get confirmation
        5. Add via Model
        6. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Get available items
            available_rooms = self.config_model.get_all_rooms()
            available_labs = self.config_model.get_all_labs()
            available_faculty = [f.name for f in self.config_model.get_all_faculty()]
            
            # Step 2: Get input from user
            course_data = self.view.get_course_input(
                available_rooms,
                available_labs,
                available_faculty
            )
            
            # Step 3: Build CourseConfig object
            course_config = self._build_course_config(course_data)
            
            # Step 4: Show summary and get confirmation
            self.view.display_course_summary(course_data)
            if not self.view.confirm("Is this information correct?"):
                # Ask if they want to restart
                if self.view.confirm("Would you like to restart adding a new course?"):
                    return self.add_course()  # Recursive restart
                else:
                    self.view.display_message("Course addition cancelled.")
                    return
            
            # Step 5: Add via model
            success = self.model.add_course(course_config)
            
            # Step 6: Show result
            if success:
                self.view.display_message(f"Course '{course_data['course_id']}' added successfully!")
            else:
                self.view.display_error(f"Course '{course_data['course_id']}' already exists.")
        
        except Exception as e:
            self.view.display_error(f"Failed to add course: {e}")
    
    def delete_course(self):
        """
        Complete workflow for deleting a course.
        
        Steps:
        1. Display list of courses with sections
        2. Get course section from user
        3. Confirm deletion
        4. Delete via Model
        5. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Get courses with section labels
            courses_with_sections = self.model.get_courses_with_sections()
            
            if not courses_with_sections:
                self.view.display_message("There are no courses in the configuration.")
                return
            
            # Display list
            self.view.display_course_list(courses_with_sections)
            
            # Build valid labels mapping
            valid_labels = {label: index for label, index, _ in courses_with_sections}
            
            # Step 2: Get section input
            section_label = self.view.get_course_section_input(valid_labels)
            target_index = valid_labels[section_label]
            _, _, target_course = courses_with_sections[target_index]
            
            # Display summary
            print(f"\nCourse Summary:")
            print(f"- {section_label} ({target_course.credits} credits)")
            
            # Step 3: Confirm deletion
            if not self.view.confirm("Delete this course section?"):
                self.view.display_message("Course deletion cancelled.")
                return
            
            # Step 4: Delete via model
            success = self.model.delete_course(
                target_course.course_id,
                section_index=target_index
            )
            
            # Step 5: Show result
            if success:
                self.view.display_message(f"Course section '{section_label}' has been permanently deleted.")
            else:
                self.view.display_error(f"Failed to delete course '{section_label}'.")
        
        except Exception as e:
            self.view.display_error(f"Failed to delete course: {e}")
    
    def modify_course(self):
        """
        Complete workflow for modifying a course.
        
        Steps:
        1. Display list and get course ID
        2. Get modification inputs
        3. Display summary and confirm
        4. Apply modifications via Model
        5. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Check if courses exist
            all_courses = self.model.get_all_courses()
            if not all_courses:
                self.view.display_message("There are no courses in the configuration.")
                return
            
            # Display existing courses
            print("\nExisting Courses:")
            for i, course in enumerate(all_courses, 1):
                print(f"{i}. {course.course_id} ({course.credits} credits)")
            
            # Get course ID
            course_id = self.view.get_course_id_input()
            
            # Check if course exists
            course = self.model.get_course_by_id(course_id)
            if not course:
                self.view.display_error(f"No course '{course_id}' found.")
                return
            
            # Step 2: Get modifications
            modifications = self.view.get_course_modifications()
            
            # Step 3: Display summary
            self.view.display_modification_summary(course_id, modifications)
            
            # Confirm
            if not self.view.confirm("Apply these changes?"):
                self.view.display_message("Course modification cancelled.")
                return
            
            # Step 4: Parse and apply modifications
            updates = self._parse_modifications(modifications, course)
            
            if updates is None:
                # Error occurred during parsing
                return
            
            success = self.model.modify_course(course_id, **updates)
            
            # Step 5: Show result
            if success:
                self.view.display_message(f"Course '{course_id}' updated successfully.")
            else:
                self.view.display_error(f"Failed to update course '{course_id}'.")
        
        except Exception as e:
            self.view.display_error(f"Failed to modify course: {e}")
    
    def _build_course_config(self, data: dict) -> CourseConfig:
        """
        Build a CourseConfig object from user input data.
        
        Parameters:
            data (dict): Dictionary containing course data from user input
        
        Returns:
            CourseConfig: Configured course object
        """
        return CourseConfig(
            course_id=data['course_id'],
            credits=data['credits'],
            room=data['rooms'],
            lab=data['labs'],
            faculty=data['faculty'],
            conflicts=data['conflicts']
        )
    
    def _parse_modifications(self, modifications: dict, current_course) -> dict | None:
        """
        Parse modification inputs into update dictionary.
        
        Handles special cases like:
        - Converting comma-separated lists
        - Adding/removing faculty members (prefix with -)
        - Validating credit values
        
        Parameters:
            modifications (dict): Raw modification inputs from user
            current_course: Current course object for reference
        
        Returns:
            dict | None: Dictionary of updates, or None if error occurred
        """
        updates = {}
        
        # Parse credits
        if modifications['credits']:
            try:
                credits_int = int(modifications['credits'])
                if credits_int < 0:
                    self.view.display_error("Credits cannot be negative.")
                    return None
                updates['credits'] = credits_int
            except ValueError:
                self.view.display_error(f"'{modifications['credits']}' is not a valid number.")
                return None
        
        # Parse room (comma-separated list)
        if modifications['room']:
            room_list = [r.strip() for r in modifications['room'].split(",") if r.strip()]
            updates['room'] = room_list
        
        # Parse lab (comma-separated list)
        if modifications['lab']:
            lab_list = [l.strip() for l in modifications['lab'].split(",") if l.strip()]
            updates['lab'] = lab_list
        
        # Parse faculty (supports adding and removing with -)
        if modifications['faculty']:
            changes = [f.strip() for f in modifications['faculty'].split(",") if f.strip()]
            current_faculty = list(current_course.faculty) if current_course.faculty else []
            
            for change in changes:
                if change.startswith("-"):
                    # Removal
                    name_to_remove = change[1:].strip()
                    if name_to_remove in current_faculty:
                        current_faculty.remove(name_to_remove)
                else:
                    # Addition
                    if change not in current_faculty:
                        current_faculty.append(change)
            
            updates['faculty'] = current_faculty
        
        return updates