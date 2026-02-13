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


# Basic Single Field Modifications

def test_modify_credits():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course, credits=4)

    assert course.credits == 4
    assert course.room == "SCI 100"  # Unchanged
    assert course.lab is None  # Unchanged


def test_modify_room():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course, room="SCI 200")

    assert course.credits == 3  # Unchanged
    assert course.room == "SCI 200"
    assert course.lab is None  # Unchanged


def test_modify_lab():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course, lab="LAB 1")

    assert course.credits == 3  # Unchanged
    assert course.room == "SCI 100"  # Unchanged
    assert course.lab == "LAB 1"


# Multiple Field Modifications

def test_modify_multiple_fields():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course, credits=4, room="SCI 200")

    assert course.credits == 4
    assert course.room == "SCI 200"
    assert course.lab is None  # Unchanged


def test_modify_all_fields():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)
    
    modifyCourse_config(course, credits=4, room="SCI 200", lab="LAB 1")
    
    assert course.credits == 4
    assert course.room == "SCI 200"
    assert course.lab == "LAB 1"


# No Modification

def test_modify_nothing():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course)

    assert course.credits == 3
    assert course.room == "SCI 100"
    assert course.lab is None


# Edge Cases - Zero and Empty Values

def test_modify_credits_zero():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course, credits=0)

    assert course.credits == 0


def test_modify_room_empty():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course, room="")

    assert course.room == ""


def test_modify_lab_empty():
    course = DummyCourse("CMSC 140", 3, "SCI 100", "LAB A")

    modifyCourse_config(course, lab="")

    assert course.lab == ""


# Negative Values

def test_modify_credits_negative():

    course = DummyCourse("CMSC 140", 3, "SCI 100", None)
    modifyCourse_config(course, credits=-5)
    
    assert course.credits == 3


# Large Values

def test_modify_credits_large_value():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)

    modifyCourse_config(course, credits=999)

    assert course.credits == 999


# Immutability Tests 

def test_course_id_unchanged():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)
    
    modifyCourse_config(course, credits=4, room="SCI 200", lab="LAB 1")
    
    assert course.course_id == "CMSC 140"


# Sequential Modifications

def test_multiple_calls_cumulative():
    course = DummyCourse("CMSC 140", 3, "SCI 100", None)
    
    modifyCourse_config(course, credits=4)
    modifyCourse_config(course, room="SCI 200")
    modifyCourse_config(course, lab="LAB 1")
    
    assert course.credits == 4
    assert course.room == "SCI 200"
    assert course.lab == "LAB 1"

