import pytest
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


@pytest.fixture
def labs():
    return ["LAB101", "LAB102"]


@pytest.fixture
def courses():
    return [
        make_mock_course("CMSC161", ["LAB101"]),
        make_mock_course("CMSC162", ["LAB101"]),
        make_mock_course("CMSC200", []),
    ]


@pytest.fixture
def faculty():
    return [
        make_mock_faculty("Dr. Smith", {"LAB101": 8}),
        make_mock_faculty("Dr. Jones", {}),
    ]


def run_modifyLab(inputs, labs, courses, faculty):
    """Helper to run modifyLab with simulated input."""
    with patch('builtins.input', side_effect=inputs):
        return modifyLab(labs, courses, faculty)


# ------------------------------------------------------------------ #
#  Empty lab list tests                                                #
# ------------------------------------------------------------------ #

def test_empty_labs_returns_unchanged(courses, faculty):
    """modifyLab should return unchanged lists if no labs exist."""
    with patch('builtins.input', side_effect=[]):
        result_labs, _, _ = modifyLab([], courses, faculty)
    assert result_labs == []


def test_empty_labs_prints_message(courses, faculty, capsys):
    """modifyLab should print a message if no labs exist."""
    with patch('builtins.input', side_effect=[]):
        modifyLab([], courses, faculty)
    captured = capsys.readouterr()
    assert "No labs available" in captured.out


# ------------------------------------------------------------------ #
#  Cancellation tests                                                  #
# ------------------------------------------------------------------ #

def test_cancel_on_lab_selection_returns_unchanged(labs, courses, faculty):
    """modifyLab should return unchanged lists if user cancels."""
    result_labs, _, _ = run_modifyLab([""], labs.copy(), courses, faculty)
    assert result_labs == labs


def test_cancel_on_confirm_returns_unchanged(labs, courses, faculty):
    """modifyLab should return unchanged lists if user cancels at confirm."""
    inputs = [
        "LAB101",   # select lab
        "LAB201",   # new name
        "n",        # cancel
    ]
    result_labs, _, _ = run_modifyLab(inputs, labs.copy(), courses, faculty)
    assert "LAB101" in result_labs
    assert "LAB201" not in result_labs


# ------------------------------------------------------------------ #
#  Successful rename tests                                             #
# ------------------------------------------------------------------ #

def test_rename_lab_updates_labs_list(labs, courses, faculty):
    """modifyLab should update the lab name in the labs list."""
    inputs = [
        "LAB101",
        "LAB201",
        "y",
    ]
    result_labs, _, _ = run_modifyLab(inputs, labs.copy(), courses, faculty)
    assert "LAB201" in result_labs
    assert "LAB101" not in result_labs


def test_rename_lab_updates_course_references(labs, courses, faculty):
    """modifyLab should update lab references in courses."""
    inputs = ["LAB101", "LAB201", "y"]
    _, result_courses, _ = run_modifyLab(inputs, labs.copy(), courses, faculty)
    for course in result_courses:
        if course.course_id in ["CMSC161", "CMSC162"]:
            assert "LAB201" in course.lab
            assert "LAB101" not in course.lab


def test_rename_lab_updates_faculty_preferences(labs, courses, faculty):
    """modifyLab should update lab preferences in faculty."""
    inputs = ["LAB101", "LAB201", "y"]
    _, _, result_faculty = run_modifyLab(inputs, labs.copy(), courses, faculty)
    dr_smith = next(f for f in result_faculty if f.name == "Dr. Smith")
    assert "LAB201" in dr_smith.lab_preferences
    assert "LAB101" not in dr_smith.lab_preferences


def test_rename_lab_does_not_affect_faculty_without_preference(labs, courses, faculty):
    """modifyLab should not affect faculty without lab preferences."""
    inputs = ["LAB101", "LAB201", "y"]
    _, _, result_faculty = run_modifyLab(inputs, labs.copy(), courses, faculty)
    dr_jones = next(f for f in result_faculty if f.name == "Dr. Jones")
    assert dr_jones.lab_preferences == {}


def test_rename_prints_success_message(labs, courses, faculty, capsys):
    """modifyLab should print success message after rename."""
    inputs = ["LAB101", "LAB201", "y"]
    with patch('builtins.input', side_effect=inputs):
        modifyLab(labs.copy(), courses, faculty)
    captured = capsys.readouterr()
    assert "successfully" in captured.out


# ------------------------------------------------------------------ #
#  Validation tests                                                    #
# ------------------------------------------------------------------ #

def test_nonexistent_lab_makes_no_changes(labs, courses, faculty):
    """modifyLab should make no changes if lab does not exist."""
    inputs = ["LAB999", ""]
    result_labs, _, _ = run_modifyLab(inputs, labs.copy(), courses, faculty)
    assert result_labs == labs


def test_duplicate_new_name_rejected(labs, courses, faculty):
    """modifyLab should reject a new name that already exists."""
    inputs = [
        "LAB101",
        "LAB102",   # already exists - invalid
        "LAB201",   # valid
        "y",
    ]
    result_labs, _, _ = run_modifyLab(inputs, labs.copy(), courses, faculty)
    assert "LAB201" in result_labs
    assert result_labs.count("LAB102") == 1

    
# ------------------------------------------------------------------ #
#  Case and spacing tests                                              #
# ------------------------------------------------------------------ #

def test_lowercase_lab_name_without_space_not_found(labs, courses, faculty, capsys):
    """modifyLab should not find 'lab101' when list contains 'LAB101' - case sensitive."""
    inputs = [
        "lab101",   # lowercase - won't match "LAB101"
        "",         # cancel
    ]
    result_labs, _, _ = run_modifyLab(inputs, labs.copy(), courses, faculty)
    captured = capsys.readouterr()
    assert "does not exist" in captured.out
    assert result_labs == labs  # no changes made


def test_lowercase_lab_name_with_space_not_found(labs, courses, faculty, capsys):
    """modifyLab should not find 'lab 101' when list contains 'LAB101' - case sensitive."""
    inputs = [
        "lab 101",  # lowercase with space - won't match "LAB101"
        "",         # cancel
    ]
    result_labs, _, _ = run_modifyLab(inputs, labs.copy(), courses, faculty)
    captured = capsys.readouterr()
    assert "does not exist" in captured.out
    assert result_labs == labs  # no changes made


def test_lab_with_space_not_found(labs, courses, faculty, capsys):
    """modifyLab should not find 'LAB 101' when list contains 'LAB101' - exact match only."""
    inputs = [
        "LAB 101",  # space between LAB and 101 - won't match "LAB101"
        "",         # cancel
    ]
    result_labs, _, _ = run_modifyLab(inputs, labs.copy(), courses, faculty)
    captured = capsys.readouterr()
    assert "does not exist" in captured.out
    assert result_labs == labs  # no changes made


def test_lab_with_space_works_if_in_list(courses, faculty):
    """modifyLab should find 'LAB 101' if the list actually contains 'LAB 101'."""
    labs_with_space = ["LAB 101", "LAB102"]
    inputs = [
        "LAB 101",  # exact match
        "LAB 201",  # new name
        "y",
    ]
    result_labs, _, _ = run_modifyLab(inputs, labs_with_space, courses, faculty)
    assert "LAB 201" in result_labs
    assert "LAB 101" not in result_labs


def test_lowercase_lab_works_if_in_list(courses, faculty):
    """modifyLab should find 'lab101' if the list actually contains 'lab101'."""
    labs_lowercase = ["lab101", "LAB102"]
    inputs = [
        "lab101",   # exact match
        "lab201",   # new name
        "y",
    ]
    result_labs, _, _ = run_modifyLab(inputs, labs_lowercase, courses, faculty)
    assert "lab201" in result_labs
    assert "lab101" not in result_labs


# ------------------------------------------------------------------ #
#  Return value tests                                                  #
# ------------------------------------------------------------------ #

def test_returns_three_values(labs, courses, faculty):
    """modifyLab should always return three values."""
    result = run_modifyLab([""], labs.copy(), courses, faculty)
    assert len(result) == 3