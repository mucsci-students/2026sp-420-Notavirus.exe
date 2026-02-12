import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
sys.path.insert(0, '..')
from lab import modifyLab


def make_mock_course(course_id, labs):
    """Helper to create a mock CourseConfig for testing."""
    course = MagicMock()
    course.course_id = course_id
    course.lab = labs
    return course


def make_mock_faculty(name, lab_preferences):
    """Helper to create a mock FacultyConfig for testing."""
    faculty = MagicMock()
    faculty.name = name
    faculty.lab_preferences = lab_preferences
    return faculty


class TestModifyLab(unittest.TestCase):

    def setUp(self):
        """Set up test data."""
        self.labs = ["LAB101", "LAB102"]
        self.courses = [
            make_mock_course("CMSC161", ["LAB101"]),
            make_mock_course("CMSC162", ["LAB101"]),
            make_mock_course("CMSC200", []),
        ]
        self.faculty = [
            make_mock_faculty("Dr. Smith", {"LAB101": 8}),
            make_mock_faculty("Dr. Jones", {}),
        ]

    def _run_modifyLab(self, inputs, labs=None, courses=None, faculty=None):
        """Helper to run modifyLab with simulated input."""
        with patch('builtins.input', side_effect=inputs):
            return modifyLab(
                labs if labs is not None else self.labs.copy(),
                courses if courses is not None else self.courses,
                faculty if faculty is not None else self.faculty
            )

    # ------------------------------------------------------------------ #
    #  Empty lab list tests                                                #
    # ------------------------------------------------------------------ #

    def test_empty_labs_returns_unchanged(self):
        """modifyLab should return unchanged lists if no labs exist."""
        with patch('builtins.input', side_effect=[]):
            labs, courses, faculty = modifyLab([], self.courses, self.faculty)
        self.assertEqual(labs, [])

    def test_empty_labs_prints_message(self):
        """modifyLab should print a message if no labs exist."""
        captured = StringIO()
        with patch('sys.stdout', captured):
            with patch('builtins.input', side_effect=[]):
                modifyLab([], self.courses, self.faculty)
        self.assertIn("No labs available", captured.getvalue())

    # ------------------------------------------------------------------ #
    #  Cancellation tests                                                  #
    # ------------------------------------------------------------------ #

    def test_cancel_on_lab_selection_returns_unchanged(self):
        """modifyLab should return unchanged lists if user cancels."""
        inputs = [""]  # press Enter to cancel
        labs, courses, faculty = self._run_modifyLab(inputs)
        self.assertEqual(labs, self.labs.copy())


    def test_cancel_on_confirm_returns_unchanged(self):
        """modifyLab should return unchanged lists if user cancels at confirm."""
        inputs = [
            "LAB101",   # select lab
            "LAB201",   # new name
            "n",        # cancel
        ]
        labs, courses, faculty = self._run_modifyLab(inputs)
        self.assertIn("LAB101", labs)
        self.assertNotIn("LAB201", labs)

    # ------------------------------------------------------------------ #
    #  Successful rename tests                                             #
    # ------------------------------------------------------------------ #

    def test_rename_lab_updates_labs_list(self):
        """modifyLab should update the lab name in the labs list."""
        inputs = [
            "LAB101",   # select lab
            "LAB201",   # new name
            "y",        # confirm
        ]
        labs, courses, faculty = self._run_modifyLab(inputs)
        self.assertIn("LAB201", labs)
        self.assertNotIn("LAB101", labs)

    def test_rename_lab_updates_course_references(self):
        """modifyLab should update lab references in courses."""
        inputs = [
            "LAB101",
            "LAB201",
            "y",
        ]
        labs, courses, faculty = self._run_modifyLab(inputs)
        for course in courses:
            if course.course_id in ["CMSC161", "CMSC162"]:
                self.assertIn("LAB201", course.lab)
                self.assertNotIn("LAB101", course.lab)

    def test_rename_lab_updates_faculty_preferences(self):
        """modifyLab should update lab preferences in faculty."""
        inputs = [
            "LAB101",
            "LAB201",
            "y",
        ]
        labs, courses, faculty = self._run_modifyLab(inputs)
        dr_smith = next(f for f in faculty if f.name == "Dr. Smith")
        self.assertIn("LAB201", dr_smith.lab_preferences)
        self.assertNotIn("LAB101", dr_smith.lab_preferences)


    def test_rename_lab_does_not_affect_faculty_without_preference(self):
        """modifyLab should not affect faculty without lab preferences."""
        inputs = [
            "LAB101",
            "LAB201",
            "y",
        ]
        labs, courses, faculty = self._run_modifyLab(inputs)
        dr_jones = next(f for f in faculty if f.name == "Dr. Jones")
        self.assertEqual(dr_jones.lab_preferences, {})


    def test_rename_prints_success_message(self):
        """modifyLab should print success message after rename."""
        captured = StringIO()
        inputs = ["LAB101", "LAB201", "y"]
        with patch('sys.stdout', captured):
            with patch('builtins.input', side_effect=inputs):
                modifyLab(self.labs.copy(), self.courses, self.faculty)
        self.assertIn("successfully", captured.getvalue())

    # ------------------------------------------------------------------ #
    #  Validation tests                                                    #
    # ------------------------------------------------------------------ #

    def test_nonexistent_lab_makes_no_changes(self):
        """modifyLab should make no changes if lab does not exist."""
        inputs = [
            "LAB999",   # does not exist
            "",         # cancel
        ]
        labs, courses, faculty = self._run_modifyLab(inputs)
        self.assertEqual(labs, self.labs.copy())

    def test_duplicate_new_name_rejected(self):
        """modifyLab should reject a new name that already exists."""
        inputs = [
            "LAB101",
            "LAB102",   # already exists - invalid
            "LAB201",   # valid
            "y",
        ]
        labs, courses, faculty = self._run_modifyLab(inputs)
        self.assertIn("LAB201", labs)
        self.assertEqual(labs.count("LAB102"), 1)


    # ------------------------------------------------------------------ #
    #  Return value tests                                                  #
    # ------------------------------------------------------------------ #

    def test_returns_three_values(self):
        """modifyLab should always return three values."""
        inputs = [""]
        result = self._run_modifyLab(inputs)
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()
