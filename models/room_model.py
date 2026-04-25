# models/room_model.py
"""RoomModel - CRUD operations for rooms."""

from models.location_model import LocationModel


class RoomModel(LocationModel):
    """Model class for room data operations."""

    def __init__(self, config_model):
        super().__init__(config_model, "rooms", "room", "room_preferences")

    def add_room(self, room_name: str) -> bool:
        return self._add(room_name)

    def delete_room(self, room_name: str) -> bool:
        return self._delete(room_name)

    def modify_room(self, old_name: str, new_name: str) -> bool:
        return self._modify(old_name, new_name)

    def room_exists(self, room_name: str) -> bool:
        return self._exists(room_name)

    def get_all_rooms(self) -> list[str]:
        return self._get_all()
