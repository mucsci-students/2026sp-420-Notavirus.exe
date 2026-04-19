# models/lab_model.py
"""LabModel - CRUD operations for labs."""

from models.location_model import LocationModel


class LabModel(LocationModel):
    """Model class for lab data operations."""

    def __init__(self, config_model):
        super().__init__(config_model, "labs", "lab", "lab_preferences")

    def add_lab(self, lab_name: str) -> bool:
        return self._add(lab_name)

    def delete_lab(self, lab_name: str) -> bool:
        return self._delete(lab_name)

    def modify_lab(self, old_name: str, new_name: str) -> bool:
        return self._modify(old_name, new_name)

    def lab_exists(self, lab_name: str) -> bool:
        return self._exists(lab_name)

    def get_all_labs(self) -> list[str]:
        return self._get_all()

