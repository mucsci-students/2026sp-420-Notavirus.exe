"""
Proxy data class for time_slot_config

All getters/setters operate on a working copy.
Changes are only applied to the real config when save() is called.

Undo/redo support: pass an on_change callback to __init__. It will be called
BEFORE every mutation so the caller can snapshot the current state. Use
_snapshot() to capture state and restore_snapshot() to apply it.
"""

import copy
from typing import Callable, Optional
from scheduler import TimeSlotConfig, Meeting


class time_config_data:
    def __init__(
        self,
        time_slot_config: TimeSlotConfig,
        on_change: Optional[Callable[[], None]] = None,
    ):
        self._config = time_slot_config
        self._on_change = on_change  # called BEFORE each mutation

        # WORKING COPY (proxy state)
        self.times = copy.deepcopy(self._config.times)
        self.classes = copy.deepcopy(self._config.classes)
        self.max_time_gap = self._config.max_time_gap
        self.min_time_overlap = self._config.min_time_overlap

    # ----------------------
    # UNDO/REDO SUPPORT
    # ----------------------

    def _notify(self):
        """Fire the on_change hook before a mutation so callers can snapshot."""
        if self._on_change:
            self._on_change()

    def _snapshot(self) -> dict:
        """Return a deep-copy snapshot of the current working state."""
        return {
            "times": copy.deepcopy(self.times),
            "classes": copy.deepcopy(self.classes),
            "max_time_gap": self.max_time_gap,
            "min_time_overlap": self.min_time_overlap,
        }

    def restore_snapshot(self, snap: dict) -> None:
        """Restore the working state from a snapshot dict (used by undo/redo)."""
        self.times = copy.deepcopy(snap["times"])
        self.classes = copy.deepcopy(snap["classes"])
        self.max_time_gap = snap["max_time_gap"]
        self.min_time_overlap = snap["min_time_overlap"]

    # ----------------------
    # BASIC ACCESS
    # ----------------------

    def get_config(self) -> TimeSlotConfig:
        return self._config

    def set_config(self, config: TimeSlotConfig):
        self._config = config
        self.reset()  # reload working copy

    # ----------------------
    # TIME SLOT GETTERS
    # ----------------------

    def get_all_time_slots(self):
        return self.times

    def get_days(self):
        return list(self.times.keys())

    def get_time_blocks_for_day(self, day):
        return self.times.get(day, [])

    def get_time_block(self, day, index):
        blocks = self.times.get(day, [])
        if 0 <= index < len(blocks):
            return blocks[index]
        return None

    # ----------------------
    # TIME SLOT SETTERS
    # ----------------------

    def add_day(self, day):
        self._notify()
        if day not in self.times:
            self.times[day] = []

    def remove_day(self, day):
        self._notify()
        if day in self.times:
            del self.times[day]

    def clear_day(self, day):
        self._notify()
        if day in self.times:
            self.times[day] = []

    def add_time_block(self, day, block):
        self._notify()
        if day not in self.times:
            self.times[day] = []
        self.times[day].append(block)

    def update_time_block(self, day, index, new_block):
        self._notify()
        if day in self.times:
            blocks = self.times[day]
            if 0 <= index < len(blocks):
                blocks[index] = new_block

    def remove_time_block(self, day, index):
        if day in self.times:
            blocks = self.times[day]
            if 0 <= index < len(blocks) and len(blocks) > 1:
                self._notify()
                blocks.pop(index)
            else:
                raise ValueError("Cannot remove time block from days")

    # ----------------------
    # CLASS PATTERN GETTERS/SETTERS
    # ----------------------

    def get_classes(self):
        return self.classes

    def add_class(self, class_pattern):
        self._notify()
        self.classes.append(class_pattern)

    def remove_class(self, index):
        if 0 <= index < len(self.classes):
            self._notify()
            self.classes.pop(index)

    def update_class(self, index, new_class):
        self._notify()
        if 0 <= index < len(self.classes):
            self.classes[index] = new_class

    def set_classes(self, new_classes):
        self._notify()
        self.classes = new_classes

    def add_meeting(self, cls, meeting: Meeting) -> None:
        self._notify()
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

        self._notify()
        cls.meetings[index] = meeting

    # ----------------------
    # REMOVE MEETING
    # ----------------------

    def remove_meeting(self, cls, index: int) -> None:
        if cls.meetings is None:
            raise ValueError("No meetings to remove")

        if index < 0 or index >= len(cls.meetings):
            raise IndexError("Meeting index out of range")

        self._notify()
        cls.meetings.pop(index)

    # ----------------------
    # CONFIG VALUE GETTERS/SETTERS
    # ----------------------

    def get_max_time_gap(self):
        return self.max_time_gap

    def set_max_time_gap(self, value):
        self._notify()
        self.max_time_gap = value

    def get_min_time_overlap(self):
        return self.min_time_overlap

    def set_min_time_overlap(self, value):
        self._notify()
        self.min_time_overlap = value

    # ----------------------
    # SAVE / RESET (KEY PART)
    # ----------------------

    def save(self):
        """Commit working copy to real config."""
        self._config.times = copy.deepcopy(self.times)
        self._config.classes = copy.deepcopy(self.classes)
        self._config.max_time_gap = self.max_time_gap
        self._config.min_time_overlap = self.min_time_overlap

    def reset(self):
        """Discard changes and reload from real config."""
        self.times = copy.deepcopy(self._config.times)
        self.classes = copy.deepcopy(self._config.classes)
        self.max_time_gap = self._config.max_time_gap
        self.min_time_overlap = self._config.min_time_overlap
