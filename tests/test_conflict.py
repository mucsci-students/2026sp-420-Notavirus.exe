import pytest
from scheduler import CourseConfig, SchedulerConfig, CombinedConfig, load_config_from_file
from conflict import modifyConflict_JSON


@pytest.fixture
def sample_config():
    """Load a sample config from the example JSON file."""
    return load_config_from_file(CombinedConfig, "example.json")


class TestModifyConflictJSON:
    """Test suite for modifyConflict_JSON function."""

    def test_mode_1_replace_left_side(self, sample_config):
        """Test mode 1: Replace course_id of conflict (A-B -> C-B)."""
        # Find a course with conflicts
        selected_course = None
        selected_conflict = None
        for course in sample_config.config.courses:
            if course.conflicts:
                selected_course = course
                selected_conflict = course.conflicts[0]
                break
        
        if not selected_course or not selected_conflict:
            pytest.skip("No conflicts found in sample config")
        
        # Select a different course as the replacement
        new_course = None
        for course in sample_config.config.courses:
            if course.course_id != selected_course.course_id and course.course_id != selected_conflict:
                new_course = course.course_id
                break
        
        if not new_course:
            pytest.skip("Not enough courses for test")
        
        # Act
        result = modifyConflict_JSON(
            selectedCourse=selected_course,
            selectedConflict=selected_conflict,
            newCourse=new_course,
            modifyMode=1,
            config=sample_config
        )
        
        # Assert
        assert result is True
        # The selected conflict should no longer be in the selected course
        assert selected_conflict not in selected_course.conflicts
        # The new course should now have the conflict
        for course in sample_config.config.courses:
            if course.course_id == new_course:
                assert selected_conflict in course.conflicts
                break

    def test_mode_2_replace_right_side(self, sample_config):
        """Test mode 2: Replace course stored as a conflict (A-B -> A-C)."""
        # Find a course with conflicts
        selected_course = None
        selected_conflict = None
        for course in sample_config.config.courses:
            if course.conflicts:
                selected_course = course
                selected_conflict = course.conflicts[0]
                break
        
        if not selected_course or not selected_conflict:
            pytest.skip("No conflicts found in sample config")
        
        # Select a different course as the replacement
        new_course = None
        for course in sample_config.config.courses:
            if course.course_id != selected_course.course_id and course.course_id != selected_conflict:
                new_course = course.course_id
                break
        
        if not new_course:
            pytest.skip("Not enough courses for test")
        
        # Act
        result = modifyConflict_JSON(
            selectedCourse=selected_course,
            selectedConflict=selected_conflict,
            newCourse=new_course,
            modifyMode=2,
            config=sample_config
        )
        
        # Assert
        assert result is True
        # The old conflict should be replaced with the new one
        assert selected_conflict not in selected_course.conflicts
        assert new_course in selected_course.conflicts

    def test_mode_1_no_duplicates_on_target(self, sample_config):
        """Test mode 1: Ensure no duplicate entries are created on target course."""
        # Find a course with conflicts
        selected_course = None
        selected_conflict = None
        for course in sample_config.config.courses:
            if course.conflicts:
                selected_course = course
                selected_conflict = course.conflicts[0]
                break
        
        if not selected_course or not selected_conflict:
            pytest.skip("No conflicts found in sample config")
        
        # Select a different course and pre-add the conflict to it
        new_course = None
        for course in sample_config.config.courses:
            if course.course_id != selected_course.course_id and course.course_id != selected_conflict:
                new_course = course.course_id
                course.conflicts.append(selected_conflict)  # Pre-add conflict
                break
        
        if not new_course:
            pytest.skip("Not enough courses for test")
        
        # Act
        result = modifyConflict_JSON(
            selectedCourse=selected_course,
            selectedConflict=selected_conflict,
            newCourse=new_course,
            modifyMode=1,
            config=sample_config
        )
        
        # Assert
        assert result is True
        for course in sample_config.config.courses:
            if course.course_id == new_course:
                # Should have exactly one instance of the conflict, not two
                assert course.conflicts.count(selected_conflict) == 1
                break

    def test_mode_2_no_duplicates_on_target(self, sample_config):
        """Test mode 2: Ensure no duplicate entries are created on target course."""
        # Find a course with conflicts
        selected_course = None
        selected_conflict = None
        for course in sample_config.config.courses:
            if course.conflicts:
                selected_course = course
                selected_conflict = course.conflicts[0]
                break
        
        if not selected_course or not selected_conflict:
            pytest.skip("No conflicts found in sample config")
        
        # Select a different course and pre-add the course to it
        new_course = None
        for course in sample_config.config.courses:
            if course.course_id != selected_course.course_id and course.course_id != selected_conflict:
                new_course = course.course_id
                course.conflicts.append(selected_course.course_id)  # Pre-add reciprocal
                break
        
        if not new_course:
            pytest.skip("Not enough courses for test")
        
        # Act
        result = modifyConflict_JSON(
            selectedCourse=selected_course,
            selectedConflict=selected_conflict,
            newCourse=new_course,
            modifyMode=2,
            config=sample_config
        )
        
        # Assert
        assert result is True
        for course in sample_config.config.courses:
            if course.course_id == new_course:
                # Should have exactly one instance of the selected course, not two
                assert course.conflicts.count(selected_course.course_id) == 1
                break

    def test_conflict_not_present_validation_fails(self, sample_config):
        """Test that modification fails if the conflict is not present."""
        # Find a course with conflicts
        selected_course = None
        for course in sample_config.config.courses:
            if course.conflicts:
                selected_course = course
                break
        
        if not selected_course:
            pytest.skip("No conflicts found in sample config")
        
        selected_conflict = "NULL 999"
        new_course = "test_replacement"
        
        # Act
        result = modifyConflict_JSON(
            selectedCourse=selected_course,
            selectedConflict=selected_conflict,
            newCourse=new_course,
            modifyMode=1,
            config=sample_config
        )
        
        # Assert
        assert result is False

    def test_invalid_selected_conflict_type(self, sample_config):
        """Test that modification fails with invalid selected_conflict type."""
        # Find a course with conflicts
        selected_course = None
        for course in sample_config.config.courses:
            if course.conflicts:
                selected_course = course
                break
        
        if not selected_course:
            pytest.skip("No conflicts found in sample config")
        
        selected_conflict = 12345  # Invalid: int instead of str
        new_course = "NULL 999"
        
        # Act
        result = modifyConflict_JSON(
            selectedCourse=selected_course,
            selectedConflict=selected_conflict,
            newCourse=new_course,
            modifyMode=1,
            config=sample_config
        )
        
        # Assert
        assert result is False

    def test_invalid_new_course_type(self, sample_config):
        """Test that modification fails with invalid new_course type."""
        # Find a course with conflicts
        selected_course = None
        selected_conflict = None
        for course in sample_config.config.courses:
            if course.conflicts:
                selected_course = course
                selected_conflict = course.conflicts[0]
                break
        
        if not selected_course or not selected_conflict:
            pytest.skip("No conflicts found in sample config")
        
        new_course = ["INVALID_LIST"]  # Invalid: list instead of str
        
        # Act
        result = modifyConflict_JSON(
            selectedCourse=selected_course,
            selectedConflict=selected_conflict,
            newCourse=new_course,
            modifyMode=1,
            config=sample_config
        )
        
        # Assert
        assert result is False

    def test_course_id_unchanged(self, sample_config):
        """Test that course_id is never modified."""
        # Find a course with conflicts
        selected_course = None
        selected_conflict = None
        for course in sample_config.config.courses:
            if course.conflicts:
                selected_course = course
                selected_conflict = course.conflicts[0]
                break
        
        if not selected_course or not selected_conflict:
            pytest.skip("No conflicts found in sample config")
        
        original_id = selected_course.course_id
        new_course = None
        for course in sample_config.config.courses:
            if course.course_id != selected_course.course_id:
                new_course = course.course_id
                break
        
        if not new_course:
            pytest.skip("Not enough courses for test")
        
        # Act
        modifyConflict_JSON(
            selectedCourse=selected_course,
            selectedConflict=selected_conflict,
            newCourse=new_course,
            modifyMode=1,
            config=sample_config
        )
        
        # Assert
        assert selected_course.course_id == original_id
