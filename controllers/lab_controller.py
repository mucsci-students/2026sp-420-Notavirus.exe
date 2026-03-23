# controllers/lab_controller.py
"""
LabController - Coordinates lab-related workflows

✅ MVC rules followed here:
    - All GUI-facing methods return (bool, str) tuples.
    - Temp-save after every in-memory write happens here, not in the View.
    - CLI methods are preserved unchanged for backward compatibility.
"""


class LabController:
    """
    Controller for lab operations.

    Coordinates between LabModel (data) and the view layer to
    implement complete lab workflows.

    Attributes:
        model:        LabModel instance
        view:         View instance (GUIView or CLIView)
        config_model: ConfigModel instance (for save_feature calls)
    """

    def __init__(self, lab_model, view):
        self.model        = lab_model
        self.view         = view
        self.config_model = lab_model.config_model

    # ------------------------------------------------------------------
    # Query methods (read-only — safe for View to call)
    # ------------------------------------------------------------------

    def get_all_labs(self) -> list[str]:
        """Return all lab names."""
        return self.model.get_all_labs()

    # ------------------------------------------------------------------
    # GUI command methods — all return (bool, str) and temp-save
    # ------------------------------------------------------------------

    def add_lab(self, lab_name: str) -> tuple[bool, str]:
        """
        Add a lab to memory and temp-save.

        ✅ Replaces gui_add_lab() — same logic, cleaner name,
           now also does the temp-save the View was doing before.

        Parameters:
            lab_name (str): Name of the lab to add.
        Returns:
            tuple[bool, str]: (success, message)
        """
        if not lab_name or not lab_name.strip():
            return False, "Lab name cannot be empty."
        lab_name = lab_name.strip()
        success  = self.model.add_lab(lab_name)
        if success:
            self.config_model.save_feature('temp', 'all')
            return True, f"Lab '{lab_name}' added successfully."
        return False, f"Failed: lab '{lab_name}' already exists."

    def modify_lab(self, old_name: str, new_name: str) -> tuple[bool, str]:
        """
        Modify a lab name in memory and temp-save.

        ✅ Replaces gui_modify_lab() — same logic, cleaner name,
           now also does the temp-save the View was doing before.

        Parameters:
            old_name (str): Current lab name.
            new_name (str): New lab name.
        Returns:
            tuple[bool, str]: (success, message)
        """
        if not new_name or not new_name.strip():
            return False, "Lab name cannot be empty."
        if not old_name:
            return False, "Please select a lab to modify."
        new_name = new_name.strip()
        all_labs = self.model.get_all_labs()
        for lab in all_labs:
            if lab.lower() == new_name.lower() and lab.lower() != old_name.lower():
                return False, f"Failed: '{lab}' already exists."
        success = self.model.modify_lab(old_name, new_name)
        if success:
            self.config_model.save_feature('temp', 'all')
            return True, f"Lab '{old_name}' renamed to '{new_name}'."
        return False, f"Failed: '{new_name}' already exists."

    def delete_labs(self, labs_to_delete: list[str]) -> tuple[bool, str]:
        """
        Delete a list of labs from memory and temp-save.

        ✅ Replaces delete_labs_gui() which returned bare bool and
           left temp-save to the View.

        Parameters:
            labs_to_delete (list[str]): Lab names to delete.
        Returns:
            tuple[bool, str]: (success, message)
        """
        if not labs_to_delete:
            return False, "No labs selected."
        failed = []
        for lab in labs_to_delete:
            if not self.model.delete_lab(lab):
                failed.append(lab)
        if failed:
            return False, f"Failed to delete: {', '.join(failed)}"
        self.config_model.save_feature('temp', 'all')
        return True, "✓ Deleted from memory."

    # ------------------------------------------------------------------
    # Legacy GUI helpers (kept for any code that still calls them)
    # ------------------------------------------------------------------

    def gui_add_lab(self, lab_name: str) -> tuple[bool, str]:
        """Alias for add_lab(). Kept for backward compatibility."""
        return self.add_lab(lab_name)

    def gui_modify_lab(self, old_name: str, new_name: str) -> tuple[bool, str]:
        """Alias for modify_lab(). Kept for backward compatibility."""
        return self.modify_lab(old_name, new_name)

    def gui_delete_lab(self, lab_name: str) -> tuple[bool, str]:
        """Delete a single lab. Kept for backward compatibility."""
        return self.delete_labs([lab_name])

    def delete_labs_gui(self, labs_to_delete: list[str]) -> bool:
        """
        Legacy method that returns bare bool.
        Kept for backward compatibility — prefer delete_labs() for new code.
        """
        success, _ = self.delete_labs(labs_to_delete)
        return success

    # ------------------------------------------------------------------
    # CLI methods (unchanged — kept for backward compatibility)
    # ------------------------------------------------------------------

    def cli_add_lab(self):
        """CLI workflow for adding a lab. Prompts via self.view."""
        try:
            existing_labs = self.model.get_all_labs()
            self.view.display_lab_list(existing_labs)
            lab_name = self.view.get_lab_name_input()
            if not self.view.confirm("Is this information correct?"):
                if self.view.confirm("Would you like to restart?"):
                    return self.cli_add_lab()
                self.view.display_message("Lab addition cancelled.")
                return
            success = self.model.add_lab(lab_name)
            if success:
                self.view.display_message(f"Lab '{lab_name}' added successfully.")
            else:
                self.view.display_error(f"Lab '{lab_name}' already exists.")
        except Exception as e:
            self.view.display_error(f"Failed to add lab: {e}")

    def cli_delete_lab(self):
        """CLI workflow for deleting a lab. Prompts via self.view."""
        try:
            all_labs = self.model.get_all_labs()
            if not all_labs:
                self.view.display_message("No labs exist.")
                return
            self.view.display_numbered_labs(all_labs)
            selection = self.view.get_lab_selection(len(all_labs))
            if selection == -1:
                self.view.display_message("Quitting.")
                return
            lab_name = all_labs[selection]
            if not self.view.confirm(f"Delete '{lab_name}'?"):
                self.view.display_message("Cancelled.")
                return
            success = self.model.delete_lab(lab_name)
            if success:
                self.view.display_message("Lab deleted.")
            else:
                self.view.display_error("Failed to delete lab.")
        except Exception as e:
            self.view.display_error(f"Failed to delete lab: {e}")

    def cli_modify_lab(self):
        """CLI workflow for modifying a lab. Prompts via self.view."""
        try:
            all_labs = self.model.get_all_labs()
            if not all_labs:
                self.view.display_message("No labs available.")
                return
            print(f"\nCurrent labs: {', '.join(all_labs)}")
            old_name = self.view.get_lab_to_modify(all_labs)
            if old_name is None:
                self.view.display_message("Cancelled.")
                return
            new_name = self.view.get_new_lab_name(old_name, all_labs)
            if new_name is None:
                return
            affected_courses = self.model.get_affected_courses(old_name)
            affected_faculty = self.model.get_affected_faculty(old_name)
            self.view.display_lab_modification_summary(old_name, new_name, affected_courses, affected_faculty)
            if not self.view.confirm("Proceed with these changes?"):
                self.view.display_message("Cancelled.")
                return
            success = self.model.modify_lab(old_name, new_name)
            if success:
                self.view.display_message(f"Lab updated to '{new_name}'.")
            else:
                self.view.display_error("Failed to modify lab.")
        except Exception as e:
            self.view.display_error(f"Failed to modify lab: {e}")