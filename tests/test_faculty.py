from scheduler import *
from main import *

#Note: Unit tests written using example.json

# Test adding a full time faculty with no course preferences FacultyConfig setup
# addFaculty_config should match with the given Faculty config
def test_addFaculty_config_noPref():
    assert addFaculty_config(name="testnoPref", isFullTime="y", dates=['M', 'W', 'F'], courses={}) == scheduler.FacultyConfig(
        name="testnoPref", unique_course_limit=FULL_TIME_UNIQUE_COURSE_LIMIT,
        maximum_credits=FULL_TIME_MAX_CREDITS, minimum_credits=MIN_CREDITS, course_preferences={}, maximum_days=MAX_DAYS,
        times={'MON': [TimeRange(start='09:00', end='17:00')], 'WED': [TimeRange(start='09:00', end='17:00')], 'FRI': [TimeRange(start='09:00', end='17:00')]})
    
def test_addFaculty_config():
    assert addFaculty_config(name="test", isFullTime="y", dates=['M', 'W', 'F'], courses={'CMSC 161': 0}) == scheduler.FacultyConfig(
        name="test", unique_course_limit=FULL_TIME_UNIQUE_COURSE_LIMIT,
        maximum_credits=FULL_TIME_MAX_CREDITS, minimum_credits=MIN_CREDITS, course_preferences={'CMSC 161': 0}, maximum_days=MAX_DAYS,
        times={'MON': [TimeRange(start='09:00', end='17:00')], 'WED': [TimeRange(start='09:00', end='17:00')], 'FRI': [TimeRange(start='09:00', end='17:00')]})

# Check if adding a duplicate name will be handled correctly.
# faculty_check_duplicate should return True.
def test_faculty_check_duplicate_name():
    (config, scheduler) = initConfig()
    faculty = addFaculty_config(name="Luke", isFullTime="y", dates=['M', 'W', 'F'], courses={"CMSC example" : 0})
    assert faculty_check_duplicate(config=config, new_faculty=faculty) == True

# Check if adding a duplicate availability and course preferences will be handled correctly.
# faculty_check_duplicate should return True.
def test_faculty_check_duplicate_datesPref():
    (config, scheduler) = initConfig()
    faculty = addFaculty_config(name="distinctName", isFullTime="y", dates=['M', 'W', 'F'], courses={})
    assert faculty_check_duplicate(config=config, new_faculty=faculty) == True

# Check if adding a distinct faculty will be handled correctly.
# faculty_check_duplicate should return False.
def test_faculty_check_distinct():
    (config, scheduler) = initConfig()
    faculty = addFaculty_config(name="distinctName", isFullTime="y", dates=['M', 'W', 'F'], courses={"distinctCourse" : 0})
    assert faculty_check_duplicate(config=config, new_faculty=faculty) == False