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

    def gui_delete_conflict(self, section_id_1: str, section_id_2: str, index_1: int, index_2: int) -> tuple[bool, str]:
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
