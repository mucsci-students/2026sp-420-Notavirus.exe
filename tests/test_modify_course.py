import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from course import modifyCourse_config

class DummyCourse:
    def __init__(self, course_id, credits, room, lab):
        self.course_id = course_id
        self.credits = credits
        self.room = room
        self.lab = lab


def test_modify_credits():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course, credits=4)

    assert course.credits == 4


def test_modify_room():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course, room="SCI 200")

    assert course.room == "SCI 200"


def test_modify_lab():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course, lab="LAB 1")

    assert course.lab == "LAB 1"


def test_modify_multiple_fields():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course, credits=4, room="SCI 200")

    assert course.credits == 4
    assert course.room == "SCI 200"


def test_modify_nothing():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course)

    assert course.credits == 3
    assert course.room == "SCI 100"
    assert course.lab is None
