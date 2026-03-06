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

    def gui_get_all_conflicts(self) -> list[tuple[str, str, int, int]]:
        """
        Get all config-level conflict pairs for display.

        Parameters:
            None

        Returns:
            list[tuple[str, str, int, int]]: List of unique conflict pairs
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

    def gui_validate_delete(self, index_1: str, index_2: str, existing_conflicts: list) -> tuple[bool, str]:
        """
        Validate a delete conflict request from the GUI.

        Parameters:
            index_1 (str): First section index
            index_2 (str): Second section index
            existing_conflicts (list): Current conflict list

        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        key = (min(index_1, index_2), max(index_1, index_2))
        match = next(
            ((c1, c2, i1, i2) for c1, c2, i1, i2 in existing_conflicts
            if (min(i1, i2), max(i1, i2)) == key),
            None
        )
        if not match:
            return False, "No conflict found for the selected pair."
        return True, ""

    def gui_delete_conflict(self, section_id_1: str, section_id_2: str, index_1: int, index_2: int) -> tuple[bool, str]:
        """
        Delete a conflict by section ID or base course ID.

        Parameters:
            section_id_1 (str): First section ID
            section_id_2 (str): Second section ID
            index_1 (int): Global index of first course section (or None for base delete)
            index_2 (int): Global index of second course section (or None for base delete)

        Returns:
            tuple[bool, str]: (success, message)
        """
        base1 = self._strip_section(section_id_1)
        base2 = self._strip_section(section_id_2)
        success = self.model.delete_conflict(base1, base2, index_1, index_2)
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

    def gui_modify_conflict(
        self,
        old_c1: str,
        old_c2: str,
        new_c1: str,
        new_c2: str,
        i1: int = None,
        i2: int = None,
    ) -> tuple[bool, str]:
        """
        Modify an existing conflict.

        When i1/i2 are provided (section mode), only the specific section
        pair is modified. When None (base mode), all sections are affected.

        Parameters:
            old_c1 (str): Original first class (section label or base ID)
            old_c2 (str): Original second class (section label or base ID)
            new_c1 (str): New first class (section label or base ID)
            new_c2 (str): New second class (section label or base ID)
            i1 (int | None): Global index of old_c1 section, or None for base mode
            i2 (int | None): Global index of old_c2 section, or None for base mode

        Returns:
            tuple[bool, str]: (success, message)
        """
        old_base1 = self._strip_section(old_c1)
        old_base2 = self._strip_section(old_c2)
        new_base1 = self._strip_section(new_c1)
        new_base2 = self._strip_section(new_c2)

        if old_base1 == new_base1 and old_base2 == new_base2:
            return True, "No changes made."

        if new_base1 == new_base2:
            return False, "Cannot conflict a course with itself."

        courses = self.model.config_model.config.config.courses

        # Get the specific course objects by index if available, else fall back to first match
        if i1 is not None and i2 is not None:
            if i1 >= len(courses) or i2 >= len(courses):
                return False, "Section index out of range."
            course_old1 = courses[i1]
            course_old2 = courses[i2]
        else:
            all_old1 = self.model.get_course_by_id(old_base1)
            all_old2 = self.model.get_course_by_id(old_base2)
            if not all_old1 or not all_old2:
                return False, "One or more courses not found."
            course_old1 = all_old1[0]
            course_old2 = all_old2[0]

        all_new1 = self.model.get_course_by_id(new_base1)
        all_new2 = self.model.get_course_by_id(new_base2)
        if not all_new1 or not all_new2:
            return False, "One or more new courses not found."
        course_new1 = all_new1[0]
        course_new2 = all_new2[0]

        if old_base1 != new_base1 and old_base2 == new_base2:
            success = self.model.modify_conflict(course_old1, course_old2, course_new1, 1)
        elif old_base2 != new_base2 and old_base1 == new_base1:
            success = self.model.modify_conflict(course_old1, course_old2, course_new2, 2)
        else:
            self.model.delete_conflict(old_base1, old_base2, i1, i2)
            success = self.model.add_conflict(new_base1, new_base2)

        if success:
            return True, "Conflict modified successfully."
        return False, "Failed to modify conflict."

    def gui_get_conflict_labels(self, existing_conflicts: list, section_label_map: dict) -> dict[str, tuple[str, str, int, int]]:
        """
        Build a label -> (c1, c2, i1, i2) map for GUI dropdowns.

        Parameters:
            existing_conflicts (list): Output of gui_get_all_conflicts()
            section_label_map (dict): index -> section label

        Returns:
            dict[str, tuple]: label string -> conflict tuple
        """
        result = {}
        for c1, c2, i1, i2 in existing_conflicts:
            label1 = section_label_map.get(i1, c1)
            label2 = section_label_map.get(i2, c2)
            label = f"{label1}  ↔  {label2}"
            result[label] = (c1, c2, i1, i2)
        return result