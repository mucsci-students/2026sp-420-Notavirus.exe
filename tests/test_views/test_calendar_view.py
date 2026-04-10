"""
Test calendar view helper functions in views/schedule_gui_view.py
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class MockCourseInstance:
    """Mock course instance for testing."""

    def __init__(
        self,
        course_str,
        faculty,
        room=None,
        lab=None,
        times=None,
        lab_index=None,
    ):
        self.course_str = course_str
        self.faculty = faculty
        self.room = room
        self.lab = lab
        self.times = times or []
        self.lab_index = lab_index


def test_parse_time_string():
    """Test _parse_time_string function."""
    from views.schedule_gui_view import _parse_time_string

    # Valid time strings
    assert _parse_time_string("MON 09:00-10:30") == (9, 0)
    assert _parse_time_string("TUE 14:30-16:00") == (14, 30)
    assert _parse_time_string("WED 08:00-09:30") == (8, 0)

    # Edge cases
    assert _parse_time_string("  FRI 15:45-17:15  ") == (15, 45)
    assert _parse_time_string("INVALID") is None
    assert _parse_time_string("") is None

    print("[PASS] test_parse_time_string passed")


def test_extract_calendar_metadata():
    """Test _extract_calendar_metadata function."""
    from views.schedule_gui_view import _extract_calendar_metadata

    schedule = [
        MockCourseInstance(
            "CMSC 476.01",
            "Zoppetti",
            room="Roddy 136",
            times=["MON 10:00-11:30", "WED 10:00-11:30", "FRI 10:00-11:30"],
        ),
        MockCourseInstance(
            "CMSC 453.01",
            "Yang",
            room="Roddy 136",
            times=["TUE 11:00-12:30", "THU 11:00-12:30"],
        ),
    ]

    days, time_slots = _extract_calendar_metadata(schedule)

    assert "MON" in days
    assert "TUE" in days
    assert "WED" in days
    assert "THU" in days
    assert "FRI" in days
    assert days == ["MON", "TUE", "WED", "THU", "FRI"]

    # time_slots are now hourly buckets like "10:00-11:00", not full course strings
    assert "10:00-11:00" in time_slots
    assert "11:00-12:00" in time_slots

    print("[PASS] test_extract_calendar_metadata passed")


def test_build_calendar_grid_by_room():
    """Test _build_calendar_grid_by_room function."""
    from views.schedule_gui_view import _build_calendar_grid_by_room

    schedule = [
        MockCourseInstance(
            "CMSC 476.01",
            "Zoppetti",
            room="Roddy 136",
            times=["MON 10:00-11:30"],
        ),
        MockCourseInstance(
            "CMSC 453.01",
            "Yang",
            lab="Linux Lab",
            lab_index=0,
            times=["WED 14:00-15:30"],
        ),
    ]

    calendar_data = _build_calendar_grid_by_room(schedule)

    assert "Roddy 136" in calendar_data
    assert "MON" in calendar_data["Roddy 136"]

    # Keys are now hourly slots; "MON 10:00-11:30" spans "10:00-11:00" and "11:00-12:00"
    assert "10:00-11:00" in calendar_data["Roddy 136"]["MON"]
    assert "11:00-12:00" in calendar_data["Roddy 136"]["MON"]

    course_info = calendar_data["Roddy 136"]["MON"]["10:00-11:00"][0]
    assert course_info["course"] == "CMSC 476"
    assert course_info["section"] == "01"
    assert course_info["faculty"] == "Zoppetti"
    assert course_info["type"] == "Lecture"

    assert "Linux Lab" in calendar_data
    assert "WED" in calendar_data["Linux Lab"]

    print("[PASS] test_build_calendar_grid_by_room passed")


def test_build_calendar_grid_by_room_with_filter():
    """Test _build_calendar_grid_by_room with location filter."""
    from views.schedule_gui_view import _build_calendar_grid_by_room

    schedule = [
        MockCourseInstance(
            "CMSC 476.01",
            "Zoppetti",
            room="Roddy 136",
            times=["MON 10:00-11:30"],
        ),
        MockCourseInstance(
            "CMSC 453.01",
            "Yang",
            room="Roddy 140",
            times=["TUE 11:00-12:30"],
        ),
    ]

    calendar_data = _build_calendar_grid_by_room(schedule, location_filter="Roddy 136")

    assert "Roddy 136" in calendar_data
    assert "Roddy 140" not in calendar_data

    print("[PASS] test_build_calendar_grid_by_room_with_filter passed")


def test_build_calendar_grid_by_faculty():
    """Test _build_calendar_grid_by_faculty function."""
    from views.schedule_gui_view import _build_calendar_grid_by_faculty

    schedule = [
        MockCourseInstance(
            "CMSC 476.01",
            "Zoppetti",
            room="Roddy 136",
            times=["MON 10:00-11:30"],
        ),
        MockCourseInstance(
            "CMSC 453.01",
            "Yang",
            room="Roddy 140",
            times=["TUE 11:00-12:30"],
        ),
    ]

    calendar_data = _build_calendar_grid_by_faculty(schedule)

    assert "Zoppetti" in calendar_data
    assert "Yang" in calendar_data

    # Keys are now hourly slots; "MON 10:00-11:30" maps to "10:00-11:00" and "11:00-12:00"
    assert "10:00-11:00" in calendar_data["Zoppetti"]["MON"]
    course_info = calendar_data["Zoppetti"]["MON"]["10:00-11:00"][0]
    assert course_info["course"] == "CMSC 476"
    assert course_info["location"] == "Roddy 136"
    assert course_info["type"] == "Room"

    print("[PASS] test_build_calendar_grid_by_faculty passed")


def test_build_calendar_grid_by_faculty_with_filter():
    """Test _build_calendar_grid_by_faculty with faculty filter."""
    from views.schedule_gui_view import _build_calendar_grid_by_faculty

    schedule = [
        MockCourseInstance(
            "CMSC 476.01",
            "Zoppetti",
            room="Roddy 136",
            times=["MON 10:00-11:30"],
        ),
        MockCourseInstance(
            "CMSC 453.01",
            "Yang",
            room="Roddy 140",
            times=["TUE 11:00-12:30"],
        ),
    ]

    calendar_data = _build_calendar_grid_by_faculty(schedule, faculty_filter="Zoppetti")

    assert "Zoppetti" in calendar_data
    assert "Yang" not in calendar_data

    print("[PASS] test_build_calendar_grid_by_faculty_with_filter passed")


def test_room_lab_separation():
    """Test that rooms and labs are properly separated in calendar view."""
    from views.schedule_gui_view import _build_calendar_grid_by_room

    schedule = [
        MockCourseInstance(
            "CMSC 476.01",
            "Zoppetti",
            room="Roddy 136",
            lab="Linux Lab",
            lab_index=1,
            times=["MON 10:00-11:30", "MON 14:00-15:30"],
        ),
    ]

    calendar_data = _build_calendar_grid_by_room(schedule)

    # Should have both room and lab entries
    assert "Roddy 136" in calendar_data
    assert "Linux Lab" in calendar_data

    # Room should have lecture time — "MON 10:00-11:30" spans "10:00-11:00" and "11:00-12:00"
    assert "10:00-11:00" in calendar_data["Roddy 136"]["MON"]
    assert calendar_data["Roddy 136"]["MON"]["10:00-11:00"][0]["type"] == "Lecture"

    # Lab should have lab time — "MON 14:00-15:30" spans "14:00-15:00" and "15:00-16:00"
    assert "14:00-15:00" in calendar_data["Linux Lab"]["MON"]
    assert calendar_data["Linux Lab"]["MON"]["14:00-15:00"][0]["type"] == "Lab"

    print("[PASS] test_room_lab_separation passed")


def test_extract_time_portion():
    """Test _extract_time_portion extracts only the time part."""
    from views.schedule_gui_view import _extract_time_portion

    assert _extract_time_portion("MON 09:00-10:30") == "09:00-10:30"
    assert _extract_time_portion("TUE 14:30-16:00") == "14:30-16:00"
    assert _extract_time_portion("  WED 08:00-09:30  ") == "08:00-09:30"

    print("[PASS] test_extract_time_portion passed")


def test_sort_time_slots():
    """Test _sort_time_slots sorts by chronological time."""
    from views.schedule_gui_view import _sort_time_slots

    # Unsorted time slots — strings already have day prefix, no "DAY " prepended
    time_slots = {
        "THU 14:10-16:00",
        "MON 09:00-10:30",
        "WED 08:00-09:30",
        "MON 17:00-18:50",
        "TUE 11:00-12:30",
    }

    sorted_slots = _sort_time_slots(time_slots)

    # Should be sorted by start time only (day is ignored in sort key)
    expected_order = [
        "WED 08:00-09:30",
        "MON 09:00-10:30",
        "TUE 11:00-12:30",
        "THU 14:10-16:00",
        "MON 17:00-18:50",
    ]

    assert sorted_slots == expected_order, (
        f"Got {sorted_slots}, expected {expected_order}"
    )

    print("[PASS] test_sort_time_slots passed")


def test_get_color_for_key():
    """Test _build_color_map assigns unique colors to each item."""
    from views.schedule_gui_view import _build_color_map

    faculty_list = ["Zoppetti", "Yang", "Rogers", "Hardy"]
    color_map = _build_color_map(faculty_list)

    # All faculty should have a color
    assert len(color_map) == 4
    assert "Zoppetti" in color_map
    assert "Yang" in color_map
    assert "Rogers" in color_map
    assert "Hardy" in color_map

    # Different faculty should have different colors (with only 12 colors, this is likely)
    colors_used = set(color_map.values())
    assert len(colors_used) >= 3, (
        "Should have at least 3 different colors for 4 faculty"
    )

    # Each color should be a tuple
    for color in colors_used:
        assert isinstance(color, tuple)
        assert len(color) == 2
        assert "bg-" in color[0]
        assert "dark:" in color[1]

    print("[PASS] test_get_color_for_key passed")


def test_color_map_consistency():
    """Test that _build_color_map produces consistent results."""
    from views.schedule_gui_view import _build_color_map

    # Same list should produce same colors
    list1 = ["A", "B", "C"]
    list2 = ["A", "B", "C"]

    map1 = _build_color_map(list1)
    map2 = _build_color_map(list2)

    assert map1 == map2, "Same list should produce consistent color map"

    # Different order should still assign same colors (sorted alphabetically)
    list3 = ["C", "B", "A"]
    map3 = _build_color_map(list3)
    assert map1 == map3, "Order shouldn't matter - colors based on alphabetical sort"

    print("[PASS] test_color_map_consistency passed")


def test_get_color_classes():
    """Test _get_color_classes converts color tuple to string."""
    from views.schedule_gui_view import _get_color_classes

    color_tuple = ("bg-blue-100", "dark:bg-blue-900")
    color_string = _get_color_classes(color_tuple)

    assert "bg-blue-100" in color_string
    assert "dark:bg-blue-900" in color_string
    assert color_string == "bg-blue-100 dark:bg-blue-900"

    print("[PASS] test_get_color_classes passed")


if __name__ == "__main__":
    test_parse_time_string()
    test_extract_calendar_metadata()
    test_build_calendar_grid_by_room()
    test_build_calendar_grid_by_room_with_filter()
    test_build_calendar_grid_by_faculty()
    test_build_calendar_grid_by_faculty_with_filter()
    test_room_lab_separation()
    test_extract_time_portion()
    test_sort_time_slots()
    test_get_color_for_key()
    test_color_map_consistency()
    test_get_color_classes()

    print("\n[PASS] All calendar view tests passed!")
