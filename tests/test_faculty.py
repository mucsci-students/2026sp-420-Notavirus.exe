from scheduler import *
from main import *

# Test full time faculty no cource preferences FacultyConfig setup
def test_add_fac():
    assert addFaculty_config(name="test", isFullTime="y", dates=['M', 'W', 'F'], courses={}) == scheduler.FacultyConfig(
        name="test", unique_course_limit=FULL_TIME_UNIQUE_COURSE_LIMIT,
        maximum_credits=FULL_TIME_MAX_CREDITS, minimum_credits=MIN_CREDITS, course_preferences={}, maximum_days=MAX_DAYS,
        times={'MON': [TimeRange(start='09:00', end='17:00')], 'WED': [TimeRange(start='09:00', end='17:00')], 'FRI': [TimeRange(start='09:00', end='17:00')]})