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

    Coordinates between ConflictModel (data) and the view layer to
    implement complete conflict workflows.

    Attributes:
        model:        ConflictModel instance
        view:         View instance
        config_model: ConfigModel shortcut (via model.config_model)
    """

    def __init__(self, conflict_model, view):
        self.model        = conflict_model
        self.view         = view
        self.config_model = conflict_model.config_model

    def get_all_courses(self) -> list:
        """
        Return all course objects from the config.

        Parameters:
            None
        Returns:
            list: All course objects.
        """
        return self.config_model.get_all_courses()

    def get_courses_with_sections(self) -> list:
        """
        Return courses with section labels as a list of (label, index, course).

        Parameters:
            None
        Returns:
            list: Tuples of (section_label, global_index, course_object).
        """
        courses       = self.config_model.get_all_courses()
        course_counts: dict[str, int] = {}
        result        = []
        for idx, course in enumerate(courses):
            cid = course.course_id
            course_counts[cid] = course_counts.get(cid, 0) + 1
            label = f"{cid}.{course_counts[cid]:02d}"
            result.append((label, idx, course))
        return result

    def gui_get_all_conflicts(self) -> list[tuple[str, str, int, int]]:
        """
        Get all config-level conflict pairs for display.

        Returns:
            list[tuple[str, str, int, int]]: List of (c1, c2, index1, index2)
        """
        return self.model.get_all_conflicts()

    def gui_get_conflict_labels(
        self,
        existing_conflicts: list,
        section_label_map: dict,
    ) -> dict[str, tuple[str, str, int, int]]:
        """
        Build a label -> (c1, c2, i1, i2) map for GUI dropdowns.

        Parameters:
            existing_conflicts (list): Output of gui_get_all_conflicts()
            section_label_map  (dict): index -> section label
        Returns:
            dict[str, tuple]: label string -> conflict tuple
        """
        result = {}
        for c1, c2, i1, i2 in existing_conflicts:
            label1 = section_label_map.get(i1, c1)
            label2 = section_label_map.get(i2, c2)
            result[f"{label1}  ↔  {label2}"] = (c1, c2, i1, i2)
        return result

    def gui_validate_delete(
        self,
        index_1: int,
        index_2: int,
        existing_conflicts: list,
    ) -> tuple[bool, str]:
        """
        Validate a delete conflict request from the GUI.

        Parameters:
            index_1            (int):  First section index.
            index_2            (int):  Second section index.
            existing_conflicts (list): Current conflict list.
        Returns:
            tuple[bool, str]: (is_valid, error_message)
        """
        key   = (min(index_1, index_2), max(index_1, index_2))
        match = next(
            ((c1, c2, i1, i2) for c1, c2, i1, i2 in existing_conflicts
             if (min(i1, i2), max(i1, i2)) == key),
            None,
        )
        if not match:
            return False, "No conflict found for the selected pair."
        return True, ""

    def add_conflict(
        self,
        course_id_a: str,
        course_id_b: str,
        section_index_a: int = None,
        section_index_b: int = None,
    ) -> tuple[bool, str]:
        """
        Add a conflict between two courses and temp-save.

        If section indices are provided, only that specific section pair is
        affected. If not provided, all sections of both courses receive the
        conflict (base-level behavior used by CLI and base-mode GUI).

        Parameters:
            course_id_a     (str):      First course ID.
            course_id_b     (str):      Second course ID.
            section_index_a (int|None): Global index of first section, or None.
            section_index_b (int|None): Global index of second section, or None.
        Returns:
            tuple[bool, str]: (success, message)
        """
        ok = self.model.add_conflict(
            course_id_a, course_id_b, section_index_a, section_index_b
        )
        if ok:
            self.config_model.save_feature('temp', 'courses')
            return True, f"Conflict added between '{course_id_a}' and '{course_id_b}'."
        return False, "Failed to add conflict."

    def gui_delete_conflict(
        self,
        section_id_1: str,
        section_id_2: str,
        index_1: int,
        index_2: int,
    ) -> tuple[bool, str]:
        """
        Delete a conflict by section ID and temp-save.

        Parameters:
            section_id_1 (str): First section ID.
            section_id_2 (str): Second section ID.
            index_1      (int): Global index of first course section (or None).
            index_2      (int): Global index of second course section (or None).
        Returns:
            tuple[bool, str]: (success, message)
        """
        base1   = self._strip_section(section_id_1)
        base2   = self._strip_section(section_id_2)
        success = self.model.delete_conflict(base1, base2, index_1, index_2)
        if success:
            self.config_model.save_feature('temp', 'courses')
            return True, f"Conflict between '{section_id_1}' and '{section_id_2}' deleted."
        return False, "Failed to delete conflict."

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
        Modify an existing conflict and temp-save.

        Parameters:
            old_c1 (str):      Original first class (section label or base ID).
            old_c2 (str):      Original second class.
            new_c1 (str):      New first class.
            new_c2 (str):      New second class.
            i1     (int|None): Global index of old_c1 section, or None for base mode.
            i2     (int|None): Global index of old_c2 section, or None for base mode.
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

        courses = self.config_model.config.config.courses

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
            self.config_model.save_feature('temp', 'courses')
            return True, "Conflict modified successfully."
        return False, "Failed to modify conflict."

    def _strip_section(self, section_id: str) -> str:
        """
        Strip section suffix from a section ID.

        e.g. 'CMSC 140.01' -> 'CMSC 140', 'CMSC 140' -> 'CMSC 140'
        """
        parts = section_id.strip().split()
        if parts and '.' in parts[-1]:
            parts[-1] = parts[-1].rsplit('.', 1)[0]
        return ' '.join(parts)