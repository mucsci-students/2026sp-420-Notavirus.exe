# controllers/conflict_controller.py
"""
ConflictController - Coordinates conflict-related workflows

This controller class manages all conflict workflows including:
- Adding new conflicts
- Modifying existing conflicts
- Deleting conflicts
- Validating conflict data
"""

from scheduler.config import CourseConfig


class ConflictController:
    """
    Controller for conflict operations.
    
    Coordinates between ConflictModel (data) and CLIView (UI) to
    implement complete conflict workflows.
    
    Attributes:
        model: ConflictModel instance
        view: CLIView instance
    """
    
    def __init__(self, conflict_model, view):
        """
        Initialize ConflictController.
        
        Parameters:
            conflict_model (ConflictModel): Model for conflict data operations
            view (CLIView): View for user interface
        
        Returns:
            None
        """
        self.model = conflict_model
        self.view = view
    
    def add_conflict(self):
        """
        Complete workflow for adding a new conflict.
        
        Steps:
        1. Display existing courses and conflicts
        2. Get two course IDs from user
        3. Validate courses exist and aren't the same
        4. Display summary and confirm
        5. Add via Model
        6. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Display existing data
            all_courses = self.model.config_model.get_all_courses()
            if not all_courses:
                self.view.display_message("There are no courses in the configuration.")
                return
            
            existing_conflicts = self.model.get_all_conflicts()
            self.view.display_conflict_list(all_courses, existing_conflicts)
            
            # Step 2: Get course IDs
            course_id_1, course_id_2 = self.view.get_conflict_input(all_courses)
            
            # Step 3: Validate
            if course_id_1 == course_id_2:
                self.view.display_error("A course cannot conflict with itself.")
                return
            
            # Check if courses exist
            if not self.model.get_course_by_id(course_id_1):
                self.view.display_error(f"Course '{course_id_1}' not found.")
                return
            
            if not self.model.get_course_by_id(course_id_2):
                self.view.display_error(f"Course '{course_id_2}' not found.")
                return
            
            # Step 4: Display summary and confirm
            self.view.display_conflict_summary(course_id_1, course_id_2)
            if not self.view.confirm("Add this conflict?"):
                self.view.display_message("Conflict addition cancelled.")
                return
            
            # Step 5: Add via model
            success = self.model.add_conflict(course_id_1, course_id_2)
            
            # Step 6: Display result
            if success:
                self.view.display_message("Conflict added successfully.")
            else:
                self.view.display_error("Failed to add conflict.")
        
        except Exception as e:
            self.view.display_error(f"Failed to add conflict: {e}")
    
    def delete_conflict(self):
        """
        Complete workflow for deleting a conflict.
        
        Steps:
        1. Display existing conflicts
        2. Get two course IDs from user
        3. Validate conflict exists
        4. Confirm deletion
        5. Delete via Model
        6. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Display existing conflicts
            existing_conflicts = self.model.get_all_conflicts()
            
            if not existing_conflicts:
                self.view.display_message("There are no conflicts currently in the configuration.")
                return
            
            all_courses = self.model.config_model.get_all_courses()
            self.view.display_existing_conflicts(existing_conflicts)
            
            # Step 2: Get course IDs
            course_id_1 = self.view.get_course_id_for_conflict("first")
            course_id_2 = self.view.get_course_id_for_conflict("conflicting")
            
            # Step 3: Validate
            if course_id_1 == course_id_2:
                self.view.display_error("A course cannot conflict with itself.")
                return
            
            if not self.model.conflict_exists(course_id_1, course_id_2):
                self.view.display_error(f"No conflict exists between '{course_id_1}' and '{course_id_2}'.")
                return
            
            # Step 4: Display summary and confirm
            self.view.display_conflict_summary(course_id_1, course_id_2)
            if not self.view.confirm("Delete this conflict?"):
                self.view.display_message("Conflict deletion cancelled.")
                return
            
            # Step 5: Delete via model
            success = self.model.delete_conflict(course_id_1, course_id_2)
            
            # Step 6: Display result
            if success:
                self.view.display_message(f"Conflict between '{course_id_1}' and '{course_id_2}' has been permanently deleted.")
            else:
                self.view.display_error("Failed to delete conflict.")
        
        except Exception as e:
            self.view.display_error(f"Failed to delete conflict: {e}")
    
    def modify_conflict(self):
        """
        Complete workflow for modifying a conflict.
        
        Steps:
        1. Display existing conflicts
        2. Get conflict selection from user
        3. Ask which side to modify
        4. Get new course ID
        5. Confirm modification
        6. Apply via Model
        7. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Display existing conflicts
            all_courses = self.model.config_model.get_all_courses()
            all_conflicts_flat = []
            
            for course in all_courses:
                for conflict_id in course.conflicts:
                    all_conflicts_flat.append((course, conflict_id))
            
            if not all_conflicts_flat:
                self.view.display_message("There are no conflicts to modify.")
                return
            
            self.view.display_numbered_conflicts(all_conflicts_flat)
            
            # Step 2: Get conflict selection
            selection_idx = self.view.get_conflict_selection(len(all_conflicts_flat))
            selected_course, conflict_str = all_conflicts_flat[selection_idx]
            
            # Resolve conflict string to specific course object
            target_conflict_course = self.view.select_course_instance(
                conflict_str,
                self.model.get_course_by_id(conflict_str),
                f"Select the specific instance of {conflict_str} involved in this conflict"
            )
            
            if not target_conflict_course:
                self.view.display_error(f"Course {conflict_str} not found.")
                return
            
            # Step 3: Ask which side to modify
            self.view.display_conflict_pair(selected_course.course_id, target_conflict_course.course_id)
            modify_mode = self.view.get_modify_side_choice()
            
            # Step 4: Get new course ID
            if modify_mode == 1:
                new_course_id = self.view.get_replacement_course_id(selected_course.course_id)
            else:
                new_course_id = self.view.get_replacement_course_id(target_conflict_course.course_id)
            
            # Get new course object
            target_new_course = self.view.select_course_instance(
                new_course_id,
                self.model.get_course_by_id(new_course_id),
                f"Select the specific instance of {new_course_id}"
            )
            
            if not target_new_course:
                self.view.display_error(f"Course {new_course_id} does not exist.")
                return
            
            # Step 5: Confirm
            if not self.view.confirm("Are you sure you want to modify this conflict?"):
                self.view.display_message("Conflict modification cancelled.")
                return
            
            # Step 6: Apply modification
            success = self.model.modify_conflict(
                selected_course,
                target_conflict_course,
                target_new_course,
                modify_mode
            )
            
            # Step 7: Display result
            if success:
                self.view.display_message("Config saved.")
            else:
                self.view.display_error("No changes applied (validation failed or conflict not present).")
        
        except Exception as e:
            self.view.display_error(f"Failed to modify conflict: {e}")