# controllers/room_controller.py
"""
RoomController - Coordinates room-related workflows

   MVC rules followed here:
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
        self.model = room_model
        self.view = view
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

        Parameters:
            name (str): Room name to add.
        Returns:
            tuple[bool, str]: (success, message)
        """
        if not name or not name.strip():
            return False, "Room name cannot be empty."
        success = self.model.add_room(name.strip())
        if success:
            self.config_model.save_feature("temp", "all")
            return True, "Room added to memory."
        return False, f"Room '{name}' already exists or is invalid."

    def modify_room(self, old_name: str, new_name: str) -> tuple[bool, str]:
        """
        Modify a room name in memory and temp-save.

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
            self.config_model.save_feature("temp", "all")
            return True, "Room modified in memory."
        return False, "Modification failed."

    def delete_room(self, name: str) -> tuple[bool, str]:
        """
        Delete a room from memory and temp-save.

        Parameters:
            name (str): Room name to delete.
        Returns:
            tuple[bool, str]: (success, message)
        """
        if not name:
            return False, "Please select a room to delete."
        success = self.model.delete_room(name)
        if success:
            self.config_model.save_feature("temp", "all")
            return True, f"Room '{name}' deleted successfully."
        return False, f"Failed: room '{name}' could not be deleted."

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _split_room_name(self, room_name: str) -> tuple[str, str]:
        parts = room_name.partition(" ")
        return (parts[0], parts[2])

    def _build_room_name(self, building: str, number: str) -> str:
        return f"{building.capitalize()} {number}"
