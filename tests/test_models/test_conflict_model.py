# tests/test_models/test_conflict_model.py
"""
Unit tests for ConflictModel using MVC architecture.

Tests cover:
- ConflictModel CRUD operations (add, delete, modify)
- Conflict existence checking
- Conflict retrieval methods
- Mutual conflict relationships
"""

import pytest
import shutil
from pathlib import Path
from scheduler import CourseConfig

from models.config_model import ConfigModel
from models.conflict_model import ConflictModel
from models.course_model import CourseModel

# Test configuration
TESTING_CONFIG = "example.json"
TEST_COPY_CONFIG = "test_copy.json"


# ================================================================
# PYTEST FIXTURES
# ================================================================

@pytest.fixture
def test_config():
    """
    Create a fresh copy of example.json for each test.
    
    Yields:
        str: Path to test configuration file
    """
    shutil.copy(TESTING_CONFIG, TEST_COPY_CONFIG)
    yield TEST_COPY_CONFIG
    Path(TEST_COPY_CONFIG).unlink(missing_ok=True)


@pytest.fixture
def conflict_model(test_config):
    """
    Create a ConflictModel with test configuration.
    
    Parameters:
        test_config (str): Path to test config (from test_config fixture)
    
    Returns:
        ConflictModel: Initialized conflict model
    """
    config_model = ConfigModel(test_config)
    return ConflictModel(config_model)


@pytest.fixture
def course_model(test_config):
    """
    Create a CourseModel for setting up test data.
    
    Parameters:
        test_config (str): Path to test config (from test_config fixture)
    
    Returns:
        CourseModel: Initialized course model
    """
    config_model = ConfigModel(test_config)
    return CourseModel(config_model)


# ================================================================
# HELPER FUNCTIONS
# ================================================================

def build_test_course(course_id, credits=3, conflicts=None) -> CourseConfig:
    """
    Build a simple test CourseConfig.
    
    Parameters:
        course_id (str): Course ID
        credits (int): Number of credits
        conflicts (list): List of conflicting course IDs
    
    Returns:
        CourseConfig: Configured course object
    """
    return CourseConfig(
        course_id=course_id,
        credits=credits,
        room=[],
        lab=[],
        faculty=[],
        conflicts=conflicts if conflicts is not None else []
    )


# ================================================================
# TESTS: Add Conflict
# ================================================================

def test_add_conflict_success(conflict_model, course_model):
    """
    Test successfully adding a mutual conflict between two courses.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup: Add two courses
    course_a = build_test_course("CONF A")
    course_b = build_test_course("CONF B")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    
    # Add conflict
    result = conflict_model.add_conflict("CONF A", "CONF B")
    
    # Assert
    assert result == True
    assert conflict_model.conflict_exists("CONF A", "CONF B") == True


def test_add_conflict_self_conflict(conflict_model):
    """
    Test that adding a self-conflict fails.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
    """
    result = conflict_model.add_conflict("SAME 101", "SAME 101")
    
    assert result == False


def test_add_conflict_nonexistent_courses(conflict_model):
    """
    Test that adding conflict between non-existent courses fails.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
    """
    result = conflict_model.add_conflict("FAKE A", "FAKE B")
    
    assert result == False


def test_add_conflict_mutual(conflict_model, course_model):
    """
    Test that adding conflict is mutual (A conflicts with B AND B conflicts with A).
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup
    course_a = build_test_course("MUTUAL A")
    course_b = build_test_course("MUTUAL B")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    
    # Add conflict
    conflict_model.add_conflict("MUTUAL A", "MUTUAL B")
    
    # Check both directions
    course_a_updated = course_model.get_course_by_id("MUTUAL A")
    course_b_updated = course_model.get_course_by_id("MUTUAL B")
    
    assert "MUTUAL B" in course_a_updated.conflicts
    assert "MUTUAL A" in course_b_updated.conflicts


# ================================================================
# TESTS: Delete Conflict
# ================================================================

def test_delete_conflict_success(conflict_model, course_model):
    """
    Test successfully deleting a conflict.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup: Add courses and conflict
    course_a = build_test_course("DEL A")
    course_b = build_test_course("DEL B")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    conflict_model.add_conflict("DEL A", "DEL B")
    
    # Delete conflict
    result = conflict_model.delete_conflict("DEL A", "DEL B")
    
    # Assert
    assert result == True
    assert conflict_model.conflict_exists("DEL A", "DEL B") == False


def test_delete_conflict_not_found(conflict_model, course_model):
    """
    Test deleting a non-existent conflict fails.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup: Add courses but no conflict
    course_a = build_test_course("NO A")
    course_b = build_test_course("NO B")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    
    # Try to delete non-existent conflict
    result = conflict_model.delete_conflict("NO A", "NO B")
    
    assert result == False


def test_delete_conflict_mutual(conflict_model, course_model):
    """
    Test that deleting conflict removes it from both courses.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup
    course_a = build_test_course("DELMUT A")
    course_b = build_test_course("DELMUT B")
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    conflict_model.add_conflict("DELMUT A", "DELMUT B")
    
    # Delete conflict
    conflict_model.delete_conflict("DELMUT A", "DELMUT B")
    
    # Check both directions removed
    course_a_updated = course_model.get_course_by_id("DELMUT A")
    course_b_updated = course_model.get_course_by_id("DELMUT B")
    
    assert "DELMUT B" not in course_a_updated.conflicts
    assert "DELMUT A" not in course_b_updated.conflicts


# ================================================================
# TESTS: Modify Conflict (Mode 1 - Replace Left Side)
# ================================================================

def test_modify_conflict_mode_1_replace_left_side(conflict_model, course_model):
    """
    Test mode 1: Replace course_id of conflict (A-B -> C-B).
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup: Add three courses
    course_a = build_test_course("MOD1 A")
    course_b = build_test_course("MOD1 B")
    course_c = build_test_course("MOD1 C")
    
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    course_model.add_course(course_c)
    
    # Add initial conflict A-B
    conflict_model.add_conflict("MOD1 A", "MOD1 B")
    
    # Get course objects for modify
    selected_course = course_model.get_course_by_id("MOD1 A")
    target_conflict_course = course_model.get_course_by_id("MOD1 B")
    target_new_course = course_model.get_course_by_id("MOD1 C")
    
    # Modify: A-B -> C-B
    result = conflict_model.modify_conflict(
        selected_course,
        target_conflict_course,
        target_new_course,
        modify_mode=1
    )
    
    # Assert
    assert result == True
    
    # Verify: A no longer conflicts with B
    course_a_updated = course_model.get_course_by_id("MOD1 A")
    assert "MOD1 B" not in course_a_updated.conflicts
    
    # Verify: C now conflicts with B
    course_c_updated = course_model.get_course_by_id("MOD1 C")
    assert "MOD1 B" in course_c_updated.conflicts
    
    # Verify: B conflicts with C (not A)
    course_b_updated = course_model.get_course_by_id("MOD1 B")
    assert "MOD1 C" in course_b_updated.conflicts
    assert "MOD1 A" not in course_b_updated.conflicts


def test_modify_conflict_mode_1_no_duplicates(conflict_model, course_model):
    """
    Test mode 1: Ensure no duplicate entries are created on target course.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup
    course_a = build_test_course("DUP1 A")
    course_b = build_test_course("DUP1 B")
    course_c = build_test_course("DUP1 C", conflicts=["DUP1 B"])  # C already conflicts with B
    
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    course_model.add_course(course_c)
    
    # Add A-B conflict
    conflict_model.add_conflict("DUP1 A", "DUP1 B")
    
    # Get course objects
    selected_course = course_model.get_course_by_id("DUP1 A")
    target_conflict_course = course_model.get_course_by_id("DUP1 B")
    target_new_course = course_model.get_course_by_id("DUP1 C")
    
    # Modify: A-B -> C-B (C already has B as conflict)
    conflict_model.modify_conflict(
        selected_course,
        target_conflict_course,
        target_new_course,
        modify_mode=1
    )
    
    # Verify no duplicates
    course_c_updated = course_model.get_course_by_id("DUP1 C")
    assert course_c_updated.conflicts.count("DUP1 B") == 1


# ================================================================
# TESTS: Modify Conflict (Mode 2 - Replace Right Side)
# ================================================================

def test_modify_conflict_mode_2_replace_right_side(conflict_model, course_model):
    """
    Test mode 2: Replace course stored as a conflict (A-B -> A-C).
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup: Add three courses
    course_a = build_test_course("MOD2 A")
    course_b = build_test_course("MOD2 B")
    course_c = build_test_course("MOD2 C")
    
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    course_model.add_course(course_c)
    
    # Add initial conflict A-B
    conflict_model.add_conflict("MOD2 A", "MOD2 B")
    
    # Get course objects
    selected_course = course_model.get_course_by_id("MOD2 A")
    target_conflict_course = course_model.get_course_by_id("MOD2 B")
    target_new_course = course_model.get_course_by_id("MOD2 C")
    
    # Modify: A-B -> A-C
    result = conflict_model.modify_conflict(
        selected_course,
        target_conflict_course,
        target_new_course,
        modify_mode=2
    )
    
    # Assert
    assert result == True
    
    # Verify: A no longer conflicts with B, now conflicts with C
    course_a_updated = course_model.get_course_by_id("MOD2 A")
    assert "MOD2 B" not in course_a_updated.conflicts
    assert "MOD2 C" in course_a_updated.conflicts
    
    # Verify: B no longer conflicts with A
    course_b_updated = course_model.get_course_by_id("MOD2 B")
    assert "MOD2 A" not in course_b_updated.conflicts
    
    # Verify: C now conflicts with A
    course_c_updated = course_model.get_course_by_id("MOD2 C")
    assert "MOD2 A" in course_c_updated.conflicts


def test_modify_conflict_mode_2_no_duplicates(conflict_model, course_model):
    """
    Test mode 2: Ensure no duplicate entries are created on target course.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup
    course_a = build_test_course("DUP2 A")
    course_b = build_test_course("DUP2 B")
    course_c = build_test_course("DUP2 C", conflicts=["DUP2 A"])  # C already conflicts with A
    
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    course_model.add_course(course_c)
    
    # Add A-B conflict
    conflict_model.add_conflict("DUP2 A", "DUP2 B")
    
    # Get course objects
    selected_course = course_model.get_course_by_id("DUP2 A")
    target_conflict_course = course_model.get_course_by_id("DUP2 B")
    target_new_course = course_model.get_course_by_id("DUP2 C")
    
    # Modify: A-B -> A-C (C already has A as conflict)
    conflict_model.modify_conflict(
        selected_course,
        target_conflict_course,
        target_new_course,
        modify_mode=2
    )
    
    # Verify no duplicates
    course_c_updated = course_model.get_course_by_id("DUP2 C")
    assert course_c_updated.conflicts.count("DUP2 A") == 1


# ================================================================
# TESTS: Modify Conflict Validation
# ================================================================

def test_modify_conflict_not_present_fails(conflict_model, course_model):
    """
    Test that modification fails if the conflict is not present.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup: Add courses but no conflict
    course_a = build_test_course("NOPRES A")
    course_b = build_test_course("NOPRES B")
    course_c = build_test_course("NOPRES C")
    
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    course_model.add_course(course_c)
    
    # Get course objects
    selected_course = course_model.get_course_by_id("NOPRES A")
    target_conflict_course = course_model.get_course_by_id("NOPRES B")
    target_new_course = course_model.get_course_by_id("NOPRES C")
    
    # Try to modify non-existent conflict
    result = conflict_model.modify_conflict(
        selected_course,
        target_conflict_course,
        target_new_course,
        modify_mode=1
    )
    
    # Assert fails
    assert result == False


def test_modify_conflict_invalid_mode(conflict_model, course_model):
    """
    Test that modification fails with invalid mode.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup
    course_a = build_test_course("INVMODE A")
    course_b = build_test_course("INVMODE B")
    course_c = build_test_course("INVMODE C")
    
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    course_model.add_course(course_c)
    conflict_model.add_conflict("INVMODE A", "INVMODE B")
    
    # Get course objects
    selected_course = course_model.get_course_by_id("INVMODE A")
    target_conflict_course = course_model.get_course_by_id("INVMODE B")
    target_new_course = course_model.get_course_by_id("INVMODE C")
    
    # Try invalid mode (3)
    result = conflict_model.modify_conflict(
        selected_course,
        target_conflict_course,
        target_new_course,
        modify_mode=3  # Invalid
    )
    
    # Assert fails
    assert result == False


# ================================================================
# TESTS: Get Conflicts
# ================================================================

def test_get_all_conflicts(conflict_model, course_model):
    """
    Test getting all unique conflict pairs.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup: Add courses and conflicts
    course_a = build_test_course("ALL A")
    course_b = build_test_course("ALL B")
    course_c = build_test_course("ALL C")
    
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    course_model.add_course(course_c)
    
    conflict_model.add_conflict("ALL A", "ALL B")
    conflict_model.add_conflict("ALL B", "ALL C")
    
    # Get all conflicts
    all_conflicts = conflict_model.get_all_conflicts()
    
    # Assert
    assert isinstance(all_conflicts, list)
    assert len(all_conflicts) >= 2  # At least our two conflicts
    
    # Check conflicts are unique pairs (sorted tuples)
    assert ("ALL A", "ALL B") in all_conflicts or ("ALL B", "ALL A") in all_conflicts


def test_conflict_exists_true(conflict_model, course_model):
    """
    Test conflict_exists returns True for existing conflict.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup
    course_a = build_test_course("EXISTS A")
    course_b = build_test_course("EXISTS B")
    
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    conflict_model.add_conflict("EXISTS A", "EXISTS B")
    
    # Test
    assert conflict_model.conflict_exists("EXISTS A", "EXISTS B") == True
    assert conflict_model.conflict_exists("EXISTS B", "EXISTS A") == True  # Order shouldn't matter


def test_conflict_exists_false(conflict_model, course_model):
    """
    Test conflict_exists returns False for non-existent conflict.
    
    Parameters:
        conflict_model (ConflictModel): Conflict model fixture
        course_model (CourseModel): Course model fixture
    """
    # Setup: Add courses but no conflict
    course_a = build_test_course("NOEXIST A")
    course_b = build_test_course("NOEXIST B")
    
    course_model.add_course(course_a)
    course_model.add_course(course_b)
    
    # Test
    assert conflict_model.conflict_exists("NOEXIST A", "NOEXIST B") == False