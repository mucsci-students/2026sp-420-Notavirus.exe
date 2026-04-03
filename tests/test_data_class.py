import pytest

from time_config_data_class import time_config_data


# ----------------------
# MOCK CLASSES
# ----------------------


class MockMeeting:
    def __init__(self, name="TestMeeting"):
        self.name = name


class MockClassPattern:
    def __init__(self):
        self.meetings = []


class MockTimeSlotConfig:
    def __init__(self):
        self.times = {}
        self.classes = []
        self.max_time_gap = 0
        self.min_time_overlap = 0


# ----------------------
# FIXTURES
# ----------------------


@pytest.fixture
def config():
    return MockTimeSlotConfig()


@pytest.fixture
def data(config):
    return time_config_data(config)


@pytest.fixture
def class_pattern():
    return MockClassPattern()


# ----------------------
# BASIC ACCESS
# ----------------------


def test_get_set_config(data, config):
    new_config = MockTimeSlotConfig()
    data.set_config(new_config)
    assert data.get_config() == new_config


# ----------------------
# TIME SLOT TESTS
# ----------------------


def test_add_and_get_day(data):
    data.add_day("Monday")
    assert "Monday" in data.get_days()


def test_remove_day(data):
    data.add_day("Tuesday")
    data.remove_day("Tuesday")
    assert "Tuesday" not in data.get_days()


def test_clear_day(data):
    data.add_time_block("Wednesday", "9AM")
    data.clear_day("Wednesday")
    assert data.get_time_blocks_for_day("Wednesday") == []


def test_add_time_block(data):
    data.add_time_block("Thursday", "10AM")
    assert data.get_time_blocks_for_day("Thursday") == ["10AM"]


def test_get_time_block_valid(data):
    data.add_time_block("Friday", "11AM")
    assert data.get_time_block("Friday", 0) == "11AM"


def test_get_time_block_invalid(data):
    assert data.get_time_block("Friday", 0) is None


def test_update_time_block(data):
    data.add_time_block("Monday", "9AM")
    data.update_time_block("Monday", 0, "10AM")
    assert data.get_time_block("Monday", 0) == "10AM"


def test_remove_time_block(data):
    data.add_time_block("Monday", "9AM")
    data.remove_time_block("Monday", 0)
    assert data.get_time_blocks_for_day("Monday") == []


# ----------------------
# CLASS PATTERN TESTS
# ----------------------


def test_add_class(data):
    cp = MockClassPattern()
    data.add_class(cp)
    assert cp in data.get_classes()


def test_remove_class(data):
    cp = MockClassPattern()
    data.add_class(cp)
    data.remove_class(0)
    assert data.get_classes() == []


def test_update_class(data):
    cp1 = MockClassPattern()
    cp2 = MockClassPattern()
    data.add_class(cp1)
    data.update_class(0, cp2)
    assert data.get_classes()[0] == cp2


def test_set_classes(data):
    cp_list = [MockClassPattern(), MockClassPattern()]
    data.set_classes(cp_list)
    assert data.get_classes() == cp_list


# ----------------------
# MEETING TESTS
# ----------------------


def test_add_meeting(data, class_pattern):
    meeting = MockMeeting()
    data.add_meeting(class_pattern, meeting)
    assert meeting in class_pattern.meetings


def test_set_meeting(data, class_pattern):
    m1 = MockMeeting("A")
    m2 = MockMeeting("B")
    class_pattern.meetings = [m1]

    data.set_meeting(class_pattern, 0, m2)
    assert class_pattern.meetings[0] == m2


def test_set_meeting_invalid_index(data, class_pattern):
    class_pattern.meetings = []
    with pytest.raises(IndexError):
        data.set_meeting(class_pattern, 0, MockMeeting())


def test_set_meeting_no_meetings(data, class_pattern):
    class_pattern.meetings = None
    with pytest.raises(ValueError):
        data.set_meeting(class_pattern, 0, MockMeeting())


def test_remove_meeting(data, class_pattern):
    m = MockMeeting()
    class_pattern.meetings = [m]

    data.remove_meeting(class_pattern, 0)
    assert class_pattern.meetings == []


def test_remove_meeting_invalid_index(data, class_pattern):
    class_pattern.meetings = []
    with pytest.raises(IndexError):
        data.remove_meeting(class_pattern, 0)


def test_remove_meeting_no_meetings(data, class_pattern):
    class_pattern.meetings = None
    with pytest.raises(ValueError):
        data.remove_meeting(class_pattern, 0)


# ----------------------
# CONFIG VALUE TESTS
# ----------------------


def test_max_time_gap(data):
    data.set_max_time_gap(15)
    assert data.get_max_time_gap() == 15


def test_min_time_overlap(data):
    data.set_min_time_overlap(5)
    assert data.get_min_time_overlap() == 5
