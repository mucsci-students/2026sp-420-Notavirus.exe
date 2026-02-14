import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
sys.path.insert(0, '..')
from ourScheduler import display_Schedule


def make_mock_course_instance(course_id, section, credits, faculty, room, days, time_str):
    """Helper to create a mock CourseInstance for testing."""
    ci = MagicMock()
    ci.course.course_id = course_id
    ci.course.section = section
    ci.course.credits = credits
    ci.faculty = faculty
    ci.room = room

    ci.time.__str__ = MagicMock(return_value=time_str)

    time_instances = []
    for day in days:
        ti = MagicMock()
        ti.day.name = day
        time_instances.append(ti)
    ci.time.times = time_instances

    return ci


@pytest.fixture
def mock_schedule():
    return [
        make_mock_course_instance(
            course_id="CMSC 161",
            section=1,
            credits=4,
            faculty="Dr. Smith",
            room="Roddy 147",
            days=["MON", "WED", "FRI"],
            time_str="MON 09:00-09:50,WED 09:00-09:50,FRI 09:00-09:50"
        ),
        make_mock_course_instance(
            course_id="CMSC 162",
            section=1,
            credits=4,
            faculty="Dr. Jones",
            room="Roddy 140",
            days=["TUE", "THU"],
            time_str="TUE 11:00-11:50,THU 11:00-11:50"
        ),
    ]


# ------------------------------------------------------------------ #
#  Empty schedule tests                                                #
# ------------------------------------------------------------------ #

def test_empty_schedule_prints_message(capsys):
    """display_Schedule should print a message for empty input."""
    display_Schedule([])
    captured = capsys.readouterr()
    assert "No schedule to display" in captured.out


def test_none_schedule_prints_message(capsys):
    """display_Schedule should handle None input gracefully."""
    display_Schedule(None)
    captured = capsys.readouterr()
    assert "No schedule to display" in captured.out


# ------------------------------------------------------------------ #
#  Section header tests                                                #
# ------------------------------------------------------------------ #

def test_timetable_grid_header_present(mock_schedule, capsys):
    """Output should contain the timetable grid header."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    assert "FULL TIMETABLE GRID" in captured.out


def test_room_layout_header_present(mock_schedule, capsys):
    """Output should contain the room layout header."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    assert "ROOM / TIME SLOT LAYOUT" in captured.out


def test_faculty_assignments_header_present(mock_schedule, capsys):
    """Output should contain the faculty assignments header."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    assert "FACULTY ASSIGNMENTS" in captured.out


# ------------------------------------------------------------------ #
#  Timetable grid tests                                                #
# ------------------------------------------------------------------ #

def test_grid_contains_day_headers(mock_schedule, capsys):
    """Grid should show all five day columns."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    for day in ["MON", "TUE", "WED", "THU", "FRI"]:
        assert day in captured.out


def test_grid_contains_course_ids(mock_schedule, capsys):
    """Grid should contain course IDs."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    assert "CMSC 161" in captured.out
    assert "CMSC 162" in captured.out


def test_grid_contains_time_slots(mock_schedule, capsys):
    """Grid should show time slot labels."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    assert "09:00-09:50" in captured.out
    assert "11:00-11:50" in captured.out


def test_grid_contains_rooms(mock_schedule, capsys):
    """Grid should show room names under courses."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    assert "Roddy 147" in captured.out
    assert "Roddy 140" in captured.out


# ------------------------------------------------------------------ #
#  Room layout tests                                                   #
# ------------------------------------------------------------------ #

def test_room_layout_contains_rooms(mock_schedule, capsys):
    """Room layout should list all rooms."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    assert "Room: Roddy 147" in captured.out
    assert "Room: Roddy 140" in captured.out


def test_room_layout_contains_faculty(mock_schedule, capsys):
    """Room layout should show faculty names."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    assert "Dr. Smith" in captured.out
    assert "Dr. Jones" in captured.out


# ------------------------------------------------------------------ #
#  Faculty assignment tests                                            #
# ------------------------------------------------------------------ #

def test_faculty_assignments_contains_names(mock_schedule, capsys):
    """Faculty assignments should list all faculty."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    assert "Dr. Smith" in captured.out
    assert "Dr. Jones" in captured.out


def test_faculty_assignments_shows_credits(mock_schedule, capsys):
    """Faculty assignments should show total credits."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    assert "Total Credits: 4" in captured.out


def test_faculty_assignments_shows_course_ids(mock_schedule, capsys):
    """Faculty assignments should show course IDs."""
    display_Schedule(mock_schedule)
    captured = capsys.readouterr()
    assert "CMSC 161" in captured.out
    assert "CMSC 162" in captured.out


# ------------------------------------------------------------------ #
#  No room tests                                                       #
# ------------------------------------------------------------------ #

def test_no_room_displays_no_room(capsys):
    """Courses with no room should display 'No Room'."""
    schedule = [
        make_mock_course_instance(
            course_id="CMSC 200",
            section=1,
            credits=3,
            faculty="Dr. Smith",
            room=None,
            days=["MON", "WED", "FRI"],
            time_str="MON 10:00-10:50,WED 10:00-10:50,FRI 10:00-10:50"
        )
    ]
    display_Schedule(schedule)
    captured = capsys.readouterr()
    assert "No Room" in captured.out
