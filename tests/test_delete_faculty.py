import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from faculty import deleteFaculty_config

class DummyFaculty:
    def __init__(self, name):
        self.name = name

# Test deleting an existing faculty
def test_delete_existing_faculty():
    faculty_list = [DummyFaculty("Kunkle"), DummyFaculty("Haldeman")]

    result = deleteFaculty_config(faculty_list, "Kunkle")

    assert result is True
    assert len(faculty_list) == 1
    assert faculty_list[0].name == "Haldeman"

# Test deleting case insensitive
def test_delete_case_insensitive():
    faculty_list = [DummyFaculty("Kunkle")]

    result = deleteFaculty_config(faculty_list, "kunkle")

    assert result is True
    assert faculty_list == []

# Test deleting nonexistent faculty
def test_delete_nonexistent():
    faculty_list = [DummyFaculty("Kunkle")]

    result = deleteFaculty_config(faculty_list, "Haldeman")

    assert result is False
    assert len(faculty_list) == 1

# Test deleting from an empty list
def test_delete_empty_list():
    faculty_list = []

    result = deleteFaculty_config(faculty_list, "Kunkle")

    assert result is False

# Test deleting only one faculty
def test_delete_only_one():
    faculty_list = [DummyFaculty("Kunkle")]

    result = deleteFaculty_config(faculty_list, "Kunkle")

    assert result is True
    assert faculty_list == []

# Test deleting when there are duplicate names
def test_delete_duplicate_names():
    faculty_list = [DummyFaculty("Kunkle"), DummyFaculty("Kunkle")]

    result = deleteFaculty_config(faculty_list, "Kunkle")

    assert result is True
    assert len(faculty_list) == 1

# Test deleting with a partial name
def test_delete_partial_name():
    faculty_list = [DummyFaculty("Ashton Kunkle")]

    result = deleteFaculty_config(faculty_list, "Kunkle")

    assert result is False
    assert len(faculty_list) == 1

# Test deleting with spaces
def test_delete_with_spaces():
    faculty_list = [DummyFaculty("Kunkle")]

    result = deleteFaculty_config(faculty_list, "  Kunkle  ".strip())

    assert result is True

# Test deleting nothing
def test_delete_returns_false_on_empty_string():
    faculty_list = [DummyFaculty("Kunkle")]

    result = deleteFaculty_config(faculty_list, "")

    assert result is False
    assert len(faculty_list) == 1