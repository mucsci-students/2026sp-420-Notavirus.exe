import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from faculty import deleteFaculty_config

class DummyFaculty:
    def __init__(self, name):
        self.name = name


def test_delete_existing_faculty():
    faculty_list = [DummyFaculty("Kunkle"), DummyFaculty("Haldeman")]

    result = deleteFaculty_config(faculty_list, "Kunkle")

    assert result is True
    assert len(faculty_list) == 1
    assert faculty_list[0].name == "Haldeman"


def test_delete_case_insensitive():
    faculty_list = [DummyFaculty("Kunkle")]

    result = deleteFaculty_config(faculty_list, "kunkle")

    assert result is True
    assert faculty_list == []


def test_delete_nonexistent():
    faculty_list = [DummyFaculty("Kunkle")]

    result = deleteFaculty_config(faculty_list, "Haldeman")

    assert result is False
    assert len(faculty_list) == 1


def test_delete_empty_list():
    faculty_list = []

    result = deleteFaculty_config(faculty_list, "Kunkle")

    assert result is False


def test_delete_only_one():
    faculty_list = [DummyFaculty("Kunkle")]

    result = deleteFaculty_config(faculty_list, "Kunkle")

    assert result is True
    assert faculty_list == []
