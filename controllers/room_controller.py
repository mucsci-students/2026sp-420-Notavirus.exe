# controllers/room_controller.py
"""
RoomController - Coordinates room-related workflows

✅ MVC rules followed here:
    - All GUI-facing methods return (bool, str) tuples.
    - Temp-save after every in-memory write happens here, not in the View.
    - CLI methods are preserved unchanged for backward compatibility.
"""


class RoomController:
    """
    Controller for room operations.

    Coordinates between RoomModel (data) and the view layer to
    implement complete room workflows.

    Attributes:
        model:        RoomModel instance
        view:         View instance (GUIView or CLIView)
        config_model: ConfigModel instance (for save_feature calls)
    """

    def __init__(self, room_model, view):
        self.model        = room_model
        self.view         = view
        # config_model is reachable via the model — store a shortcut for clarity.
        self.config_model = room_model.config_model

    # ------------------------------------------------------------------
    # Query methods (read-only — safe for View to call)
    # ------------------------------------------------------------------

    def get_all_rooms(self) -> list[str]:
        """Return all room names."""
        return self.model.get_all_rooms()

    # ------------------------------------------------------------------
    # GUI command methods — all return (bool, str) and temp-save
    # ------------------------------------------------------------------

    def add_room(self, name: str) -> tuple[bool, str]:
        """
        Add a room to memory and temp-save.

        ✅ Replaces direct model.add_room() calls from the View.

        Parameters:
            name (str): Room name to add.
        Returns:
            tuple[bool, str]: (success, message)
        """
        if not name or not name.strip():
            return False, "Room name cannot be empty."
        success = self.model.add_room(name.strip())
        if success:
            self.config_model.save_feature('temp', 'all')
            return True, "Room added to memory."
        return False, f"Room '{name}' already exists or is invalid."

    def modify_room(self, old_name: str, new_name: str) -> tuple[bool, str]:
        """
        Modify a room name in memory and temp-save.

        ✅ Replaces direct model.modify_room() calls from the View.

        Parameters:
            old_name (str): Current room name.
            new_name (str): New room name.
        Returns:
            tuple[bool, str]: (success, message)
        """
        if not new_name or not new_name.strip():
            return False, "New room name cannot be empty."
        success = self.model.modify_room(old_name, new_name.strip())
        if success:
            self.config_model.save_feature('temp', 'all')
            return True, "Room modified in memory."
        return False, "Modification failed."

    def delete_room(self, name: str) -> tuple[bool, str]:
        """
        Delete a room from memory and temp-save.

        ✅ Replaces gui_delete_room() — same logic, cleaner name,
           now also does the temp-save the View was doing before.

        Parameters:
            name (str): Room name to delete.
        Returns:
            tuple[bool, str]: (success, message)
        """
        if not name:
            return False, "Please select a room to delete."
        success = self.model.delete_room(name)
        if success:
            self.config_model.save_feature('temp', 'all')
            return True, f"Room '{name}' deleted successfully."
        return False, f"Failed: room '{name}' could not be deleted."

    # ------------------------------------------------------------------
    # CLI methods (unchanged — kept for backward compatibility)
    # ------------------------------------------------------------------

    def cli_add_room(self):
        """CLI workflow for adding rooms. Prompts via self.view."""
        while True:
            try:
                room_name = self.view.get_room_input()
                if not room_name.strip():
                    self.view.display_error("Room cannot be blank.")
                    continue
                success = self.model.add_room(room_name)
                if success:
                    self.view.display_message("Room added.")
                else:
                    self.view.display_error(f"Room '{room_name}' already exists.")
                if not self.view.confirm("Add another room?"):
                    break
            except Exception as e:
                self.view.display_error(f"Failed to add room: {e}")
                break

    def cli_delete_room(self):
        """CLI workflow for deleting a room. Prompts via self.view."""
        try:
            all_rooms = self.model.get_all_rooms()
            if not all_rooms:
                self.view.display_message("There are no rooms in the configuration.")
                return
            self.view.display_numbered_rooms(all_rooms)
            room_name = self.view.get_room_name_for_deletion()
            if not self.model.room_exists(room_name):
                self.view.display_error(f"No room '{room_name}' found.")
                return
            if not self.view.confirm(f"Are you sure you want to delete room '{room_name}'?"):
                self.view.display_message("Deletion cancelled.")
                return
            success = self.model.delete_room(room_name)
            if success:
                self.view.display_message(f"Room '{room_name}' deleted successfully.")
            else:
                self.view.display_error("Failed to delete room.")
        except Exception as e:
            self.view.display_error(f"Failed to delete room: {e}")

    def cli_modify_room(self):
        """CLI workflow for modifying rooms. Prompts via self.view."""
        while True:
            try:
                room_name = self.view.get_room_input()
                if not self.model.room_exists(room_name):
                    self.view.display_error(f"Room '{room_name}' does not exist.")
                    if not self.view.confirm("Modify another room?"):
                        break
                    continue
                modify_choice = self.view.get_room_modify_choice()
                building, number = self._split_room_name(room_name)
                if modify_choice == "building":
                    new_building  = self.view.get_room_building_input()
                    new_room_name = self._build_room_name(new_building, number)
                elif modify_choice == "number":
                    new_number    = self.view.get_room_number_input()
                    new_room_name = self._build_room_name(building, new_number)
                else:
                    self.view.display_error("Invalid modification choice.")
                    continue
                success = self.model.modify_room(room_name, new_room_name)
                if success:
                    self.view.display_message(f"Room modified from '{room_name}' to '{new_room_name}'.")
                else:
                    self.view.display_error(f"Cannot update to '{new_room_name}'.")
                if not self.view.confirm("Modify another room?"):
                    break
            except Exception as e:
                self.view.display_error(f"Failed to modify room: {e}")
                break

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _split_room_name(self, room_name: str) -> tuple[str, str]:
        parts = room_name.partition(" ")
        return (parts[0], parts[2])

    def _build_room_name(self, building: str, number: str) -> str:
        return f"{building.capitalize()} {number}"