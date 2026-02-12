import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
sys.path.insert(0, '..')
from course import addCourse


class TestAddCourse(unittest.TestCase):

    def _run_addCourse(self, inputs):
        """Helper to run addCourse with simulated input."""
        available_rooms = ["ROOM101", "ROOM102"]
        available_labs = ["LAB101"]
        available_faculty = ["Dr. Smith", "Dr. Jones"]
        with patch('builtins.input', side_effect=inputs):
            return addCourse(available_rooms, available_labs, available_faculty)

    # ------------------------------------------------------------------ #
    #  Successful course creation tests                                    #
    # ------------------------------------------------------------------ #

    def test_add_course_returns_course_config(self):
        """addCourse should return a CourseConfig object on success."""
        inputs = [
            "CMSC161",  # course ID
            "3",        # credits
            "ROOM101",  # room
            "",         # done adding rooms
            "",         # skip labs
            "Dr. Smith",# faculty
            "",         # done adding faculty
            "",         # no conflicts
            "y",        # confirm
        ]
        result = self._run_addCourse(inputs)
        self.assertIsNotNone(result)

    def test_add_course_correct_course_id(self):
        """addCourse should set the correct course ID."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertEqual(result.course_id, "CMSC161")

    def test_add_course_correct_credits(self):
        """addCourse should set the correct credits."""
        inputs = [
            "CMSC161",
            "4",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertEqual(result.credits, 4)

    def test_add_course_correct_room(self):
        """addCourse should set the correct room."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertIn("ROOM101", result.room)

    def test_add_course_multiple_rooms(self):
        """addCourse should allow multiple rooms."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "ROOM102",
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertIn("ROOM101", result.room)
        self.assertIn("ROOM102", result.room)

    def test_add_course_with_lab(self):
        """addCourse should set the correct lab."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "",
            "LAB101",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertIn("LAB101", result.lab)

    def test_add_course_no_lab(self):
        """addCourse should allow no lab."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertEqual(result.lab, [])

    def test_add_course_correct_faculty(self):
        """addCourse should set the correct faculty."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertIn("Dr. Smith", result.faculty)

    def test_add_course_multiple_faculty(self):
        """addCourse should allow multiple faculty."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "Dr. Jones",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertIn("Dr. Smith", result.faculty)
        self.assertIn("Dr. Jones", result.faculty)

    def test_add_course_with_conflict(self):
        """addCourse should set conflicts correctly."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "CMSC162",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertIn("CMSC162", result.conflicts)

    def test_add_course_no_conflicts(self):
        """addCourse should allow no conflicts."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertEqual(result.conflicts, [])

    def test_add_course_course_id_uppercase(self):
        """addCourse should convert course ID to uppercase."""
        inputs = [
            "cmsc161",
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertEqual(result.course_id, "CMSC161")

    # ------------------------------------------------------------------ #
    #  Cancellation tests                                                  #
    # ------------------------------------------------------------------ #

    def test_add_course_cancel_returns_none(self):
        """addCourse should return None when user cancels."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "n",    # don't confirm
            "n",    # don't restart
        ]
        result = self._run_addCourse(inputs)
        self.assertIsNone(result)

    # ------------------------------------------------------------------ #
    #  Validation tests                                                    #
    # ------------------------------------------------------------------ #

    def test_add_course_invalid_credits_rejected(self):
        """addCourse should reject credits outside 1-4."""
        inputs = [
            "CMSC161",
            "0",        # invalid
            "5",        # invalid
            "3",        # valid
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertEqual(result.credits, 3)

    def test_add_course_invalid_room_rejected(self):
        """addCourse should reject rooms not in available list."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM999",  # invalid
            "ROOM101",  # valid
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertIn("ROOM101", result.room)
        self.assertNotIn("ROOM999", result.room)

    def test_add_course_invalid_faculty_rejected(self):
        """addCourse should reject faculty not in available list."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Nobody",   # invalid
            "Dr. Smith",    # valid
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertIn("Dr. Smith", result.faculty)
        self.assertNotIn("Dr. Nobody", result.faculty)

    def test_add_course_self_conflict_rejected(self):
        """addCourse should reject a course conflicting with itself."""
        inputs = [
            "CMSC161",
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "CMSC161",  # self conflict - invalid
            "CMSC162",  # valid
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertNotIn("CMSC161", result.conflicts)
        self.assertIn("CMSC162", result.conflicts)

    def test_add_course_empty_id_rejected(self):
        """addCourse should reject an empty course ID."""
        inputs = [
            "",         # invalid - empty
            "CMSC161",  # valid
            "3",
            "ROOM101",
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertEqual(result.course_id, "CMSC161")

    def test_add_course_empty_room_requires_at_least_one(self):
        """addCourse should require at least one room."""
        inputs = [
            "CMSC161",
            "3",
            "",         # try to finish with no room - invalid
            "ROOM101",  # valid
            "",
            "",
            "Dr. Smith",
            "",
            "",
            "y",
        ]
        result = self._run_addCourse(inputs)
        self.assertIn("ROOM101", result.room)


if __name__ == "__main__":
    unittest.main()
