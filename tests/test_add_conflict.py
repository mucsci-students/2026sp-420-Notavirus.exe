import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from conflict import addConflict_config

class DummyCourse:
    def __init__(self, course_id):
        self.course_id = course_id
        self.conflicts = []

# Test adding conflicts successfully
def test_add_conflict_success():
    c1 = DummyCourse("CMSC 140")
    c2 = DummyCourse("CMSC 161")

    result = addConflict_config([c1, c2], "CMSC 140", "CMSC 161")

    assert result is True
    assert "CMSC 161" in c1.conflicts
    assert "CMSC 140" in c2.conflicts

# Test conflicts with itself
def test_add_conflict_self():
    c1 = DummyCourse("CMSC 140")

    result = addConflict_config([c1], "CMSC 140", "CMSC 140")

    assert result is False

# Test adding a conflict to a missing course
def test_add_conflict_missing_course():
    c1 = DummyCourse("CMSC 140")

    result = addConflict_config([c1], "CMSC 140", "CMSC 161")

    assert result is False

# Test adding a conflict with no duplicate values
def test_add_conflict_no_duplicates():
    c1 = DummyCourse("CMSC 140")
    c2 = DummyCourse("CMSC 161")

    addConflict_config([c1, c2], "CMSC 140", "CMSC 161")
    addConflict_config([c1, c2], "CMSC 140", "CMSC 161")

    assert c1.conflicts.count("CMSC 161") == 1
    assert c2.conflicts.count("CMSC 140") == 1

# Test adding a conflict with multiple courses
def test_add_conflict_multiple_courses():
    c1 = DummyCourse("CMSC 140")
    c2 = DummyCourse("CMSC 161")
    c3 = DummyCourse("CMSC 162")

    addConflict_config([c1, c2, c3], "CMSC 140", "CMSC 161")

    assert "CMSC 161" in c1.conflicts
    assert "CMSC 140" in c2.conflicts
    assert c3.conflicts == []

# Test one side of a conflict
def test_fix_one_sided_conflict():
    c1 = DummyCourse("CMSC 140")
    c2 = DummyCourse("CMSC 161")

    c1.conflicts.append("CMSC 161")

    addConflict_config([c1, c2], "CMSC 140", "CMSC 161")

    assert "CMSC 140" in c2.conflicts

# Test conflicts with many courses available
def test_conflict_with_many_courses():
    courses = [DummyCourse(f"CMSC {i}") for i in range(100)]

    result = addConflict_config(courses, "CMSC 1", "CMSC 2")

    assert result is True

# Test keeping existing conflicts
def test_preserve_existing_conflicts():
    c1 = DummyCourse("CMSC 140")
    c2 = DummyCourse("CMSC 161")

    c1.conflicts.append("CMSC 200")

    addConflict_config([c1, c2], "CMSC 140", "CMSC 161")

    assert "CMSC 200" in c1.conflicts
    assert "CMSC 161" in c1.conflicts

# Test that whitespace doesn't match
def test_add_conflict_whitespace_in_ids():
    c1 = DummyCourse("CMSC 140")
    c2 = DummyCourse("CMSC 161")

    result = addConflict_config([c1, c2], "CMSC  140", "CMSC 161")  # Extra space

    assert result is False  # Won't find "CMSC  140"

# Test that order of course_id_1 and course_id_2 doesn't matter
def test_add_conflict_order_independence():
    c1 = DummyCourse("CMSC 140")
    c2 = DummyCourse("CMSC 161")

    # Add in reverse order
    result = addConflict_config([c1, c2], "CMSC 161", "CMSC 140")

    assert result is True
    assert "CMSC 161" in c1.conflicts
    assert "CMSC 140" in c2.conflicts

# Test adding a conflict that already exists (both directions)
def test_add_conflict_already_complete():
    c1 = DummyCourse("CMSC 140")
    c2 = DummyCourse("CMSC 161")
    
    c1.conflicts.append("CMSC 161")
    c2.conflicts.append("CMSC 140")

    result = addConflict_config([c1, c2], "CMSC 140", "CMSC 161")

    assert result is True  # Still returns True
    assert c1.conflicts.count("CMSC 161") == 1  # No duplicates
    assert c2.conflicts.count("CMSC 140") == 1