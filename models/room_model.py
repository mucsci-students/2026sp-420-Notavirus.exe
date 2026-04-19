# models/room_model.py
"""RoomModel - CRUD operations for rooms."""

from models.location_model import LocationModel


class RoomModel(LocationModel):
    """Model class for room data operations."""

    def __init__(self, config_model):
        super().__init__(config_model, "rooms", "room", "room_preferences")

    def add_room(self, room_name: str) -> bool:
        if not room_name or not room_name.strip():
            return False
        return self._add(room_name)

    def delete_room(self, room_name: str) -> bool:
        return self._delete(room_name)

    def modify_room(self, old_name: str, new_name: str) -> bool:
        if not new_name or not new_name.strip():
            return False
        return self._modify(old_name, new_name)

    def room_exists(self, room_name: str) -> bool:
        return self._exists(room_name)

    def get_all_rooms(self) -> list[str]:
        return self._get_all()

    def get_affected_courses(self, room_name: str) -> list:
        return self._get_affected_courses(room_name)

    def get_affected_faculty(self, room_name: str) -> list:
        return self._get_affected_faculty(room_name)

    def _split_room_name(self, room_name: str) -> tuple[str, str]:
        parts = room_name.partition(" ")
        return (parts[0], parts[2])

    def _build_room_name(self, building: str, number: str) -> str:
        return f"{building.capitalize()} {number}"
