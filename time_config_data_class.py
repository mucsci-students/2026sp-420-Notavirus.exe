"""
Data class for time_slot_config

has getters and setters for modifying the data within the config
"""

from scheduler import TimeSlotConfig
from scheduler import Meeting


class time_config_data:
    def __init__(self, time_slot_config: TimeSlotConfig):
        self._config = time_slot_config
        # ----------------------

    # BASIC ACCESS
    # ----------------------

    def get_config(self) -> TimeSlotConfig:
        return self._config

    def set_config(self, config: TimeSlotConfig):
        self._config = config

    # ----------------------
    # TIME SLOT GETTERS
    # ----------------------

    def get_all_time_slots(self):
        return self._config.times

    def get_days(self):
        return list(self._config.times.keys())

    def get_time_blocks_for_day(self, day):
        return self._config.times.get(day, [])

    def get_time_block(self, day, index):
        blocks = self._config.times.get(day, [])
        if 0 <= index < len(blocks):
            return blocks[index]
        return None

    # ----------------------
    # TIME SLOT SETTERS
    # ----------------------

    def add_day(self, day):
        if day not in self._config.times:
            self._config.times[day] = []

    def remove_day(self, day):
        if day in self._config.times:
            del self._config.times[day]

    def clear_day(self, day):
        if day in self._config.times:
            self._config.times[day] = []

    def add_time_block(self, day, block):
        if day not in self._config.times:
            self._config.times[day] = []
        self._config.times[day].append(block)

    def update_time_block(self, day, index, new_block):
        if day in self._config.times:
            blocks = self._config.times[day]
            if 0 <= index < len(blocks):
                blocks[index] = new_block

    def remove_time_block(self, day, index):
        if day in self._config.times:
            blocks = self._config.times[day]
            if 0 <= index < len(blocks):
                blocks.pop(index)

    # ----------------------
    # CLASS PATTERN GETTERS/SETTERS
    # ----------------------

    def get_classes(self):
        return self._config.classes

    def add_class(self, class_pattern):
        self._config.classes.append(class_pattern)

    def remove_class(self, index):
        if 0 <= index < len(self._config.classes):
            self._config.classes.pop(index)

    def update_class(self, index, new_class):
        if 0 <= index < len(self._config.classes):
            self._config.classes[index] = new_class

    def set_classes(self, new_classes):
        self._config.classes = new_classes

    def add_meeting(self, cls, meeting: Meeting) -> None:
        if cls.meetings is None:
            cls.meetings = []
        cls.meetings.append(meeting)

    # ----------------------
    # SET / UPDATE MEETING
    # ----------------------
    def set_meeting(self, cls, index: int, meeting: Meeting) -> None:
        if cls.meetings is None:
            raise ValueError("No meetings exist for this class pattern")

        if index < 0 or index >= len(cls.meetings):
            raise IndexError("Meeting index out of range")

        cls.meetings[index] = meeting

    # ----------------------
    # REMOVE MEETING
    # ----------------------
    def remove_meeting(self, cls, index: int) -> None:
        if cls.meetings is None:
            raise ValueError("No meetings to remove")

        if index < 0 or index >= len(cls.meetings):
            raise IndexError("Meeting index out of range")

        cls.meetings.pop(index)

    # ----------------------
    # CONFIG VALUE GETTERS/SETTERS
    # ----------------------

    def get_max_time_gap(self):
        return self._config.max_time_gap

    def set_max_time_gap(self, value):
        self._config.max_time_gap = value

    def get_min_time_overlap(self):
        return self._config.min_time_overlap

    def set_min_time_overlap(self, value):
        self._config.min_time_overlap = value
