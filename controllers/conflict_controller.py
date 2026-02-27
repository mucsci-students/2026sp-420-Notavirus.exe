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
    
    Coordinates between ConflictModel (data) and view to
    implement complete conflict workflows.
    
    Attributes:
        model: ConflictModel instance
        view: View instance
    """
    
    def __init__(self, conflict_model, view):
        """
        Initialize ConflictController.
        
        Parameters:
            conflict_model (ConflictModel): Model for conflict data operations
            view: View for user interface
        
        Returns:
            None
        """
        self.model = conflict_model
        self.view = view

    # -------------------------
    # GUI methods
    # -------------------------

    def gui_get_all_conflicts(self) -> list[tuple[str, str]]:
        """
        Get all config-level conflict pairs for display.

        Parameters:
            None

        Returns:
            list[tuple[str, str]]: List of unique conflict pairs
        """
        return self.model.get_all_conflicts()

    def gui_get_section_map(self, scheduler_model) -> dict[str, set[str]]:
        """
        Run scheduler and return a map of base course ID to section strings.

        Parameters:
            scheduler_model (SchedulerModel): Model for schedule generation

        Returns:
            dict[str, set[str]]: Map of base course ID to set of section strings
        """
        section_map: dict[str, set[str]] = {}
        for model in scheduler_model.generate_schedules(limit=1):
            for course in model:
                base = self._strip_section(course.course_str)
                section_map.setdefault(base, set()).add(course.course_str)
        return section_map

    def gui_validate_delete(self, section_id_1: str, section_id_2: str) -> tuple[bool, str]:
        """
        Validate a delete conflict request from the GUI.

        Parameters:
            section_id_1 (str): First section ID (e.g. 'CMSC 140.01' or 'CMSC 140')
            section_id_2 (str): Second section ID

        Returns:
            tuple[bool, str]: (is_valid, error_message) — error_message is '' if valid
        """
        if not section_id_1 or not section_id_2:
            return False, "Please enter both section IDs."

        base1 = self._strip_section(section_id_1)
        base2 = self._strip_section(section_id_2)

        if base1 == base2:
            return False, "A course cannot conflict with itself."

        if not self.model.conflict_exists(base1, base2):
            return False, f"No conflict exists between '{section_id_1}' and '{section_id_2}'."

        return True, ""

    def gui_delete_conflict(self, section_id_1: str, section_id_2: str) -> tuple[bool, str]:
        """
        Delete a conflict by section ID or base course ID.

        Parameters:
            section_id_1 (str): First section ID (e.g. 'CMSC 140.01' or 'CMSC 140')
            section_id_2 (str): Second section ID

        Returns:
            tuple[bool, str]: (success, message)
        """
        base1 = self._strip_section(section_id_1)
        base2 = self._strip_section(section_id_2)
        success = self.model.delete_conflict(base1, base2)
        if success:
            return True, f"Conflict between '{section_id_1}' and '{section_id_2}' has been permanently deleted."
        return False, "Failed to delete conflict."

    def _strip_section(self, section_id: str) -> str:
        """
        Strip section suffix from a section ID.

        e.g. 'CMSC 140.01' -> 'CMSC 140', 'CMSC 140' -> 'CMSC 140'

        Parameters:
            section_id (str): Section ID to strip

        Returns:
            str: Base course ID
        """
        parts = section_id.strip().split()
        if parts and '.' in parts[-1]:
            parts[-1] = parts[-1].rsplit('.', 1)[0]
        return ' '.join(parts)

    # -------------------------
    # CLI methods (unchanged)
    # -------------------------

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
            all_courses = self.model.config_model.get_all_courses()
            if not all_courses:
                self.view.display_message("There are no courses in the configuration.")
                return
            
            existing_conflicts = self.model.get_all_conflicts()
            self.view.display_conflict_list(all_courses, existing_conflicts)
            
            course_id_1, course_id_2 = self.view.get_conflict_input(all_courses)
            
            if course_id_1 == course_id_2:
                self.view.display_error("A course cannot conflict with itself.")
                return
            
            if not self.model.get_course_by_id(course_id_1):
                self.view.display_error(f"Course '{course_id_1}' not found.")
                return
            
            if not self.model.get_course_by_id(course_id_2):
                self.view.display_error(f"Course '{course_id_2}' not found.")
                return
            
            self.view.display_conflict_summary(course_id_1, course_id_2)
            if not self.view.confirm("Add this conflict?"):
                self.view.display_message("Conflict addition cancelled.")
                return
            
            success = self.model.add_conflict(course_id_1, course_id_2)
            
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
            existing_conflicts = self.model.get_all_conflicts()
            
            if not existing_conflicts:
                self.view.display_message("There are no conflicts currently in the configuration.")
                return
            
            all_courses = self.model.config_model.get_all_courses()
            self.view.display_existing_conflicts(existing_conflicts)
            
            course_id_1 = self.view.get_course_id_for_conflict("first")
            course_id_2 = self.view.get_course_id_for_conflict("conflicting")
            
            if course_id_1 == course_id_2:
                self.view.display_error("A course cannot conflict with itself.")
                return
            
            if not self.model.conflict_exists(course_id_1, course_id_2):
                self.view.display_error(f"No conflict exists between '{course_id_1}' and '{course_id_2}'.")
                return
            
            self.view.display_conflict_summary(course_id_1, course_id_2)
            if not self.view.confirm("Delete this conflict?"):
                self.view.display_message("Conflict deletion cancelled.")
                return
            
            success = self.model.delete_conflict(course_id_1, course_id_2)
            
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
            all_courses = self.model.config_model.get_all_courses()
            all_conflicts_flat = []
            
            for course in all_courses:
                for conflict_id in course.conflicts:
                    all_conflicts_flat.append((course, conflict_id))
            
            if not all_conflicts_flat:
                self.view.display_message("There are no conflicts to modify.")
                return
            
            self.view.display_numbered_conflicts(all_conflicts_flat)
            
            selection_idx = self.view.get_conflict_selection(len(all_conflicts_flat))
            selected_course, conflict_str = all_conflicts_flat[selection_idx]
            
            target_conflict_course = self.view.select_course_instance(
                conflict_str,
                self.model.get_course_by_id(conflict_str),
                f"Select the specific instance of {conflict_str} involved in this conflict"
            )
            
            if not target_conflict_course:
                self.view.display_error(f"Course {conflict_str} not found.")
                return
            
            self.view.display_conflict_pair(selected_course.course_id, target_conflict_course.course_id)
            modify_mode = self.view.get_modify_side_choice()
            
            if modify_mode == 1:
                new_course_id = self.view.get_replacement_course_id(selected_course.course_id)
            else:
                new_course_id = self.view.get_replacement_course_id(target_conflict_course.course_id)
            
            target_new_course = self.view.select_course_instance(
                new_course_id,
                self.model.get_course_by_id(new_course_id),
                f"Select the specific instance of {new_course_id}"
            )
            
            if not target_new_course:
                self.view.display_error(f"Course {new_course_id} does not exist.")
                return
            
            if not self.view.confirm("Are you sure you want to modify this conflict?"):
                self.view.display_message("Conflict modification cancelled.")
                return
            
            success = self.model.modify_conflict(
                selected_course,
                target_conflict_course,
                target_new_course,
                modify_mode
            )
            
            if success:
                self.view.display_message("Config saved.")
            else:
                self.view.display_error("No changes applied (validation failed or conflict not present).")
        
        except Exception as e:
            self.view.display_error(f"Failed to modify conflict: {e}")