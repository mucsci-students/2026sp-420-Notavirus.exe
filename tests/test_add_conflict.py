import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from conflict import addConflict_config

class DummyCourse:
    def __init__(self, course_id):
        self.course_id = course_id
        self.conflicts = []


def test_add_conflict_success():
    c1 = DummyCourse("CMSC 140")
    c2 = DummyCourse("CMSC 161")

    result = addConflict_config([c1, c2], "CMSC 140", "CMSC 161")

    assert result is True
    assert "CMSC 161" in c1.conflicts
    assert "CMSC 140" in c2.conflicts


def test_add_conflict_self():
    c1 = DummyCourse("CMSC 140")

    result = addConflict_config([c1], "CMSC 140", "CMSC 140")

    assert result is False


def test_add_conflict_missing_course():
    c1 = DummyCourse("CMSC 140")

    result = addConflict_config([c1], "CMSC 140", "CMSC 161")

    assert result is False


def test_add_conflict_no_duplicates():
    c1 = DummyCourse("CMSC 140")
    c2 = DummyCourse("CMSC 161")

    addConflict_config([c1, c2], "CMSC 140", "CMSC 161")
    addConflict_config([c1, c2], "CMSC 140", "CMSC 161")

    assert c1.conflicts.count("CMSC 161") == 1
    assert c2.conflicts.count("CMSC 140") == 1


def test_add_conflict_multiple_courses():
    c1 = DummyCourse("CMSC 140")
    c2 = DummyCourse("CMSC 161")
    c3 = DummyCourse("CMSC 162")

    addConflict_config([c1, c2, c3], "CMSC 140", "CMSC 161")

    assert "CMSC 161" in c1.conflicts
    assert "CMSC 140" in c2.conflicts
    assert c3.conflicts == []
