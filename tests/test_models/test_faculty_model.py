# ================================================================
# TESTS: delete_faculty removes faculty references from courses
# ================================================================


def test_delete_faculty_removes_course_references(faculty_model):
    """
    Test that deleting a faculty also removes their name from any courses
    that reference them (covers the inner branch at line 79).
    """
    from scheduler import CourseConfig

    # Add a faculty to delete
    faculty = build_faculty_config(
        name="ToDelete Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    # Add a course that references this faculty
    test_course = CourseConfig(
        course_id="TEST_DEL_101",
        credits=3,
        faculty=["ToDelete Faculty"],
        room=[],
        lab=[],
        conflicts=[],
    )
    faculty_model.config_model.config.config.courses.append(test_course)

    # Delete the faculty
    result = faculty_model.delete_faculty("ToDelete Faculty")

    assert result
    assert not faculty_model.faculty_exists("ToDelete Faculty")
    assert "ToDelete Faculty" not in test_course.faculty


# ================================================================
# TESTS: get_faculty_by_name returns None for missing faculty
# ================================================================


def test_get_faculty_by_name_not_found(faculty_model):
    """
    Test that get_faculty_by_name returns None when faculty does not exist
    (covers the return None at line 143).
    """
    result = faculty_model.get_faculty_by_name("Nonexistent Person")
    assert result is None


# ================================================================
# TESTS: set_position_type
# ================================================================


def test_set_position_type_fulltime(faculty_model):
    """
    Test setting a faculty to full-time updates credits and course limit.
    """
    faculty = build_faculty_config(
        name="Position Faculty", isFullTime="n", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    result = faculty_model.set_position_type("Position Faculty", is_fulltime=True)

    updated = faculty_model.get_faculty_by_name("Position Faculty")
    assert result
    assert updated.maximum_credits == FULL_TIME_MAX_CREDITS
    assert updated.unique_course_limit == FULL_TIME_UNIQUE_COURSE_LIMIT


def test_set_position_type_adjunct(faculty_model):
    """
    Test setting a faculty to adjunct updates credits and course limit.
    """
    faculty = build_faculty_config(
        name="Adjunct Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    result = faculty_model.set_position_type("Adjunct Faculty", is_fulltime=False)

    updated = faculty_model.get_faculty_by_name("Adjunct Faculty")
    assert result
    assert updated.maximum_credits == ADJUNCT_MAX_CREDITS
    assert updated.unique_course_limit == ADJUNCT_UNIQUE_COURSE_LIMIT


def test_set_position_type_adjunct_clamps_min_credits(faculty_model):
    """
    Test that switching to adjunct clamps minimum_credits when it exceeds ADJUNCT_MAX_CREDITS.
    """
    faculty = build_faculty_config(
        name="AdjClamp Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)
    faculty_model.modify_faculty("AdjClamp Faculty", "minimum_credits", 10)

    result = faculty_model.set_position_type("AdjClamp Faculty", is_fulltime=False)

    updated = faculty_model.get_faculty_by_name("AdjClamp Faculty")
    assert result
    assert updated.minimum_credits <= ADJUNCT_MAX_CREDITS


def test_set_position_type_not_found(faculty_model):
    """
    Test set_position_type returns False when faculty does not exist.
    """
    result = faculty_model.set_position_type("Ghost Faculty", is_fulltime=True)
    assert not result


# ================================================================
# TESTS: set_maximum_credits
# ================================================================


def test_set_maximum_credits_success(faculty_model):
    """
    Test setting maximum credits updates the faculty.
    """
    faculty = build_faculty_config(
        name="MaxCred Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    result = faculty_model.set_maximum_credits("MaxCred Faculty", 10)

    updated = faculty_model.get_faculty_by_name("MaxCred Faculty")
    assert result
    assert updated.maximum_credits == 10


def test_set_maximum_credits_clamps_minimum(faculty_model):
    """
    Test that lowering max below current minimum clamps minimum_credits.
    """
    faculty = build_faculty_config(
        name="ClampMin Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)
    faculty_model.modify_faculty("ClampMin Faculty", "minimum_credits", 8)

    result = faculty_model.set_maximum_credits("ClampMin Faculty", 5)

    updated = faculty_model.get_faculty_by_name("ClampMin Faculty")
    assert result
    assert updated.minimum_credits <= 5


def test_set_maximum_credits_adjunct_limit(faculty_model):
    """
    Test that setting max <= ADJUNCT_MAX_CREDITS sets adjunct course limit.
    """
    faculty = build_faculty_config(
        name="AdjMax Faculty", isFullTime="y", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    result = faculty_model.set_maximum_credits("AdjMax Faculty", ADJUNCT_MAX_CREDITS)

    updated = faculty_model.get_faculty_by_name("AdjMax Faculty")
    assert result
    assert updated.unique_course_limit == ADJUNCT_UNIQUE_COURSE_LIMIT


def test_set_maximum_credits_fulltime_limit(faculty_model):
    """
    Test that setting max above ADJUNCT_MAX_CREDITS upgrades course limit to full-time
    when it was previously at the adjunct limit.
    """
    faculty = build_faculty_config(
        name="FTMax Faculty", isFullTime="n", dates=["M"], courses={}
    )
    faculty_model.add_faculty(faculty)

    result = faculty_model.set_maximum_credits("FTMax Faculty", 10)

    updated = faculty_model.get_faculty_by_name("FTMax Faculty")
    assert result
    assert updated.unique_course_limit == FULL_TIME_UNIQUE_COURSE_LIMIT


def test_set_maximum_credits_not_found(faculty_model):
    """
    Test set_maximum_credits returns False when faculty does not exist.
    """
    result = faculty_model.set_maximum_credits("Ghost Faculty", 10)
    assert not result


# ================================================================
# TESTS: build_faculty_config branches
# ================================================================


def test_build_faculty_config_adjunct(faculty_model):
    """
    Test build_faculty_config sets adjunct defaults when is_full_time is False.
    """
    data = {
        "name": "Adjunct Builder",
        "is_full_time": False,
        "times": {
            "Monday": [{"start": "09:00", "end": "12:00"}],
        },
        "course_preferences": {},
        "lab_preferences": {},
    }
    result = faculty_model.build_faculty_config(data)

    assert result.maximum_credits == ADJUNCT_MAX_CREDITS
    assert result.unique_course_limit == ADJUNCT_UNIQUE_COURSE_LIMIT


def test_build_faculty_config_fulltime(faculty_model):
    """Test build_faculty_config for fulltime with times, lab_preferences, and unknown day."""
    data = {
        "name": "Jane Doe",
        "is_full_time": True,
        "times": {
            "M": [{"start": "08:00", "end": "10:00"}],
            "UnknownDay": [{"start": "08:00", "end": "12:00"}],
        },
        "course_preferences": {"CS101": 1},
        "lab_preferences": {"CS101L": 2},
    }
    config = faculty_model.build_faculty_config(data)
    assert config.name == "Jane Doe"
    assert config.maximum_credits == FULL_TIME_MAX_CREDITS
    assert config.unique_course_limit == FULL_TIME_UNIQUE_COURSE_LIMIT
    assert "MON" in config.times
    assert config.course_preferences == {"CS101": 1}
    assert config.lab_preferences == {"CS101L": 2}


def test_build_faculty_config_days_branch(faculty_model):
    """
    Test build_faculty_config using the 'days' key (else branch).
    """
    data = {
        "name": "Days Builder",
        "is_full_time": True,
        "days": ["M", "W", "F"],
        "course_preferences": {},
        "lab_preferences": {},
    }
    result = faculty_model.build_faculty_config(data)

    assert "MON" in result.times
    assert "WED" in result.times
    assert "FRI" in result.times
    assert result.times["MON"][0].start == "08:00"
    assert result.times["MON"][0].end == "20:00"


def test_build_faculty_config_adjunct_days_else(faculty_model):
    """Test build_faculty_config for adjunct using the days else branch."""
    data = {
        "name": "John Adjunct",
        "is_full_time": False,
        "days": ["M", "W", "F"],
    }
    config = faculty_model.build_faculty_config(data)
    assert config.name == "John Adjunct"
    assert config.maximum_credits == ADJUNCT_MAX_CREDITS
    assert config.unique_course_limit == ADJUNCT_UNIQUE_COURSE_LIMIT
    assert "MON" in config.times
    assert config.times["MON"][0].start == "08:00"
    assert config.times["MON"][0].end == "20:00"
    assert "WED" in config.times
    assert "FRI" in config.times
