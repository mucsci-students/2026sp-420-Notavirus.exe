import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
sys.path.insert(0, '..')  # make sure main.py is importable
from main import display_Schedule


def make_mock_course_instance(course_id, section, credits, faculty, room, days, time_str):
    """Helper to create a mock CourseInstance for testing."""
    ci = MagicMock()
    ci.course.course_id = course_id
    ci.course.section = section
    ci.course.credits = credits
    ci.faculty = faculty
    ci.room = room

    # Mock time
    ci.time.__str__ = MagicMock(return_value=time_str)
    
    # Mock time.times (list of TimeInstance)
    time_instances = []
    for day in days:
        ti = MagicMock()
        ti.day.name = day
        time_instances.append(ti)
    ci.time.times = time_instances

    return ci


class TestDisplaySchedule(unittest.TestCase):

    def setUp(self):
        """Set up mock schedule data for testing."""
        self.mock_schedule = [
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

    def _capture_output(self, schedule):
        """Helper to capture printed output."""
        captured = StringIO()
        with patch('sys.stdout', captured):
            display_Schedule(schedule)
        return captured.getvalue()

    # ------------------------------------------------------------------ #
    #  Empty schedule tests                                                #
    # ------------------------------------------------------------------ #

    def test_empty_schedule_prints_message(self):
        """display_Schedule should print a message for empty input."""
        captured = StringIO()
        with patch('sys.stdout', captured):
            display_Schedule([])
        self.assertIn("No schedule to display", captured.getvalue())

    def test_none_schedule_prints_message(self):
        """display_Schedule should handle None input gracefully."""
        captured = StringIO()
        with patch('sys.stdout', captured):
            display_Schedule(None)
        self.assertIn("No schedule to display", captured.getvalue())

    # ------------------------------------------------------------------ #
    #  Section header tests                                                #
    # ------------------------------------------------------------------ #

    def test_timetable_grid_header_present(self):
        """Output should contain the timetable grid header."""
        output = self._capture_output(self.mock_schedule)
        self.assertIn("FULL TIMETABLE GRID", output)

    def test_room_layout_header_present(self):
        """Output should contain the room layout header."""
        output = self._capture_output(self.mock_schedule)
        self.assertIn("ROOM / TIME SLOT LAYOUT", output)

    def test_faculty_assignments_header_present(self):
        """Output should contain the faculty assignments header."""
        output = self._capture_output(self.mock_schedule)
        self.assertIn("FACULTY ASSIGNMENTS", output)

    # ------------------------------------------------------------------ #
    #  Timetable grid tests                                                #
    # ------------------------------------------------------------------ #

    def test_grid_contains_day_headers(self):
        """Grid should show all five day columns."""
        output = self._capture_output(self.mock_schedule)
        for day in ["MON", "TUE", "WED", "THU", "FRI"]:
            self.assertIn(day, output)

    def test_grid_contains_course_ids(self):
        """Grid should contain course IDs."""
        output = self._capture_output(self.mock_schedule)
        self.assertIn("CMSC 161", output)
        self.assertIn("CMSC 162", output)

    def test_grid_contains_time_slots(self):
        """Grid should show time slot labels."""
        output = self._capture_output(self.mock_schedule)
        self.assertIn("09:00-09:50", output)
        self.assertIn("11:00-11:50", output)

    def test_grid_contains_rooms(self):
        """Grid should show room names under courses."""
        output = self._capture_output(self.mock_schedule)
        self.assertIn("Roddy 147", output)
        self.assertIn("Roddy 140", output)

    # ------------------------------------------------------------------ #
    #  Room layout tests                                                   #
    # ------------------------------------------------------------------ #

    def test_room_layout_contains_rooms(self):
        """Room layout should list all rooms."""
        output = self._capture_output(self.mock_schedule)
        self.assertIn("Room: Roddy 147", output)
        self.assertIn("Room: Roddy 140", output)

    def test_room_layout_contains_faculty(self):
        """Room layout should show faculty names."""
        output = self._capture_output(self.mock_schedule)
        self.assertIn("Dr. Smith", output)
        self.assertIn("Dr. Jones", output)

    # ------------------------------------------------------------------ #
    #  Faculty assignment tests                                            #
    # ------------------------------------------------------------------ #

    def test_faculty_assignments_contains_names(self):
        """Faculty assignments should list all faculty."""
        output = self._capture_output(self.mock_schedule)
        self.assertIn("Dr. Smith", output)
        self.assertIn("Dr. Jones", output)

    def test_faculty_assignments_shows_credits(self):
        """Faculty assignments should show total credits."""
        output = self._capture_output(self.mock_schedule)
        self.assertIn("Total Credits: 4", output)

    def test_faculty_assignments_shows_course_ids(self):
        """Faculty assignments should show course IDs."""
        output = self._capture_output(self.mock_schedule)
        self.assertIn("CMSC 161", output)
        self.assertIn("CMSC 162", output)

    # ------------------------------------------------------------------ #
    #  No room tests                                                       #
    # ------------------------------------------------------------------ #

    def test_no_room_displays_no_room(self):
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
        output = self._capture_output(schedule)
        self.assertIn("No Room", output)


if __name__ == "__main__":
    unittest.main()