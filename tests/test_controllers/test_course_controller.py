import pytest
from unittest.mock import Mock
import shutil
from pathlib import Path

from models.config_model import ConfigModel
from models.course_model import CourseModel
from controllers.course_controller import CourseController

TESTING_CONFIG = "example.json"
TEST_COPY_CONFIG = "test_copy.json"

@pytest.fixture
def test_config():
    shutil.copy(TESTING_CONFIG, TEST_COPY_CONFIG)
    yield TEST_COPY_CONFIG
    Path(TEST_COPY_CONFIG).unlink(missing_ok=True)

@pytest.fixture
def config_model(test_config):
    return ConfigModel(test_config)

@pytest.fixture
def course_controller(config_model):
    course_model = CourseModel(config_model)
    return CourseController(course_model, config_model)


def test_modify_course_valid_rooms_labs(course_controller):
    # Setup a course first
    data = {"course_id": "TEST 101", "credits": 3, "room": [], "lab": [], "faculty": [], "conflicts": []}
    course_controller.add_course(data)
    
    # example.json has "Roddy 136" and "Linux"
    mods = {"room": ["Roddy 136"], "lab": ["Linux"], "faculty": []}
    success, msg = course_controller.modify_course("TEST 101", 0, mods)
    
    assert success is True
    assert "updated successfully" in msg


def test_modify_course_invalid_room(course_controller):
    data = {"course_id": "TEST 102", "credits": 3, "room": [], "lab": [], "faculty": [], "conflicts": []}
    course_controller.add_course(data)
    
    mods = {"room": ["InvalidRoom999"]}
    success, msg = course_controller.modify_course("TEST 102", 0, mods)
    
    assert success is False
    assert "Invalid room" in msg


def test_modify_course_invalid_lab(course_controller):
    data = {"course_id": "TEST 103", "credits": 3, "room": [], "lab": [], "faculty": [], "conflicts": []}
    course_controller.add_course(data)
    
    mods = {"lab": ["InvalidLab999"]}
    success, msg = course_controller.modify_course("TEST 103", 0, mods)
    
    assert success is False
    assert "Invalid lab" in msg


def test_modify_course_invalid_faculty(course_controller):
    data = {"course_id": "TEST 104", "credits": 3, "room": [], "lab": [], "faculty": [], "conflicts": []}
    course_controller.add_course(data)
    
    mods = {"faculty": ["InvalidFaculty999"]}
    success, msg = course_controller.modify_course("TEST 104", 0, mods)
    
    assert success is False
    assert "Invalid faculty" in msg
