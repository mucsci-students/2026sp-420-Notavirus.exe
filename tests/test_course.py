import pytest
from unittest.mock import patch
import sys
sys.path.insert(0, '..')
from course import addCourse


@pytest.fixture
def available():
    return {
        "rooms": ["ROOM101", "ROOM102"],
        "labs": ["LAB101"],
        "faculty": ["Dr. Smith", "Dr. Jones"]
    }


def run_addCourse(inputs, available):
    with patch('builtins.input', side_effect=inputs):
        return addCourse(
            available["rooms"],
            available["labs"],
            available["faculty"]
        )


# ------------------------------------------------------------------ #
#  Successful course creation tests                                    #
# ------------------------------------------------------------------ #

def test_add_course_returns_course_config(available):
    """addCourse should return a CourseConfig object on success."""
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
    result = run_addCourse(inputs, available)
    assert result is not None


def test_add_course_correct_course_id(available):
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
    result = run_addCourse(inputs, available)
    assert result.course_id == "CMSC161"


def test_add_course_correct_credits(available):
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
    result = run_addCourse(inputs, available)
    assert result.credits == 4


def test_add_course_correct_room(available):
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
    result = run_addCourse(inputs, available)
    assert "ROOM101" in result.room


def test_add_course_multiple_rooms(available):
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
    result = run_addCourse(inputs, available)
    assert "ROOM101" in result.room
    assert "ROOM102" in result.room


def test_add_course_with_lab(available):
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
    result = run_addCourse(inputs, available)
    assert "LAB101" in result.lab


def test_add_course_no_lab(available):
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
    result = run_addCourse(inputs, available)
    assert result.lab == []


def test_add_course_correct_faculty(available):
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
    result = run_addCourse(inputs, available)
    assert "Dr. Smith" in result.faculty


def test_add_course_multiple_faculty(available):
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
    result = run_addCourse(inputs, available)
    assert "Dr. Smith" in result.faculty
    assert "Dr. Jones" in result.faculty


def test_add_course_with_conflict(available):
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
    result = run_addCourse(inputs, available)
    assert "CMSC162" in result.conflicts


def test_add_course_no_conflicts(available):
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
    result = run_addCourse(inputs, available)
    assert result.conflicts == []


def test_add_course_course_id_uppercase(available):
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
    result = run_addCourse(inputs, available)
    assert result.course_id == "CMSC161"


# ------------------------------------------------------------------ #
#  Cancellation tests                                                  #
# ------------------------------------------------------------------ #

def test_add_course_cancel_returns_none(available):
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
        "n",
        "n",
    ]
    result = run_addCourse(inputs, available)
    assert result is None


# ------------------------------------------------------------------ #
#  Validation tests                                                    #
# ------------------------------------------------------------------ #

def test_add_course_invalid_credits_rejected(available):
    """addCourse should reject credits outside 1-4."""
    inputs = [
        "CMSC161",
        "0",
        "5",
        "3",
        "ROOM101",
        "",
        "",
        "Dr. Smith",
        "",
        "",
        "y",
    ]
    result = run_addCourse(inputs, available)
    assert result.credits == 3


def test_add_course_invalid_room_rejected(available):
    """addCourse should reject rooms not in available list."""
    inputs = [
        "CMSC161",
        "3",
        "ROOM999",
        "ROOM101",
        "",
        "",
        "Dr. Smith",
        "",
        "",
        "y",
    ]
    result = run_addCourse(inputs, available)
    assert "ROOM101" in result.room
    assert "ROOM999" not in result.room


def test_add_course_invalid_faculty_rejected(available):
    """addCourse should reject faculty not in available list."""
    inputs = [
        "CMSC161",
        "3",
        "ROOM101",
        "",
        "",
        "Dr. Nobody",
        "Dr. Smith",
        "",
        "",
        "y",
    ]
    result = run_addCourse(inputs, available)
    assert "Dr. Smith" in result.faculty
    assert "Dr. Nobody" not in result.faculty

def test_add_course_no_room_with_lab(available):
    """addCourse should allow no room but with a lab."""
    inputs = [
        "CMSC300",
        "4",
        "",           # room (empty)
        "LAB101",     # lab
        "",           # finish labs
        "Dr. Jones",
        "",
        "",
        "y",
    ]
    result = run_addCourse(inputs, available)
    assert result is not None
    assert result.room == []
    assert result.lab == ["LAB101"]

def test_add_course_minimal_required_fields_only(available):
    """addCourse should allow a course with only required fields (no room, no lab)."""
    inputs = [
        "CMSC100",
        "3",
        "",          # room (empty)
        "",          # lab (empty)
        "Dr. Smith", # faculty (required - at least one)
        "",
        "",
        "y",
    ]
    result = run_addCourse(inputs, available)
    assert result is not None
    assert result.course_id == "CMSC100"
    assert result.credits == 3
    assert result.room == []
    assert result.lab == []
    assert result.faculty == ["Dr. Smith"]
    assert result.conflicts == []


def test_add_course_self_conflict_rejected(available):
    """addCourse should reject a course conflicting with itself."""
    inputs = [
        "CMSC161",
        "3",
        "ROOM101",
        "",
        "",
        "Dr. Smith",
        "",
        "CMSC161",
        "CMSC162",
        "",
        "y",
    ]
    result = run_addCourse(inputs, available)
    assert "CMSC161" not in result.conflicts
    assert "CMSC162" in result.conflicts


def test_add_course_empty_id_rejected(available):
    """addCourse should reject an empty course ID."""
    inputs = [
        "",
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
    result = run_addCourse(inputs, available)
    assert result.course_id == "CMSC161"


def test_add_course_empty_room_requires_at_least_one(available):
    """addCourse should require at least one room."""
    inputs = [
        "CMSC161",
        "3",
        "",
        "ROOM101",
        "",
        "",
        "Dr. Smith",
        "",
        "",
        "y",
    ]
    result = run_addCourse(inputs, available)
    assert "ROOM101" in result.room
