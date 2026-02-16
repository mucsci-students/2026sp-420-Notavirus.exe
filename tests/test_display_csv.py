import sys
import pytest
from unittest.mock import MagicMock
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent.parent))
import ourScheduler


class DummyScheduler:
    def __init__(self, models):
        self._models = models
    def get_models(self):
        return self._models


class MockCourse:
    def __init__(self, csv=None, json=None, raise_csv=False):
        self._csv = csv
        self._json = json
        self._raise = raise_csv
    def as_csv(self):
        if self._raise:
            raise Exception("no csv")
        return self._csv
    def model_dump_json(self):
        return self._json


def test_display_csv_single_schedule(monkeypatch, capsys):
    """Should print schedule header and CSV lines when as_csv exists."""
    course = MockCourse(csv='CMSC161,Section1,Dr. Smith,Roddy 147,MON 09:00-09:50', json='{}')
    model = [course]

    # Patch scheduler.Scheduler to return our DummyScheduler
    monkeypatch.setattr(ourScheduler, 'scheduler', ourScheduler.scheduler)
    monkeypatch.setattr(ourScheduler.scheduler, 'Scheduler', lambda cfg: DummyScheduler([model]))

    ourScheduler.display_Schedules_csv(MagicMock(), max_schedules=1)
    captured = capsys.readouterr()
    assert 'Schedule 1' in captured.out
    assert 'CMSC161,Section1,Dr. Smith,Roddy 147,MON 09:00-09:50' in captured.out


def test_display_csv_fallback_to_json(monkeypatch, capsys):
    """If as_csv raises, should print JSON fallback."""
    course = MockCourse(csv=None, json='{"id":"CMSC200"}', raise_csv=True)
    model = [course]

    monkeypatch.setattr(ourScheduler.scheduler, 'Scheduler', lambda cfg: DummyScheduler([model]))

    ourScheduler.display_Schedules_csv(MagicMock(), max_schedules=1)
    captured = capsys.readouterr()
    assert 'Schedule 1' in captured.out
    assert '{"id":"CMSC200"}' in captured.out


def test_display_csv_no_schedules(monkeypatch, capsys):
    """No models -> prints no valid schedule message."""
    monkeypatch.setattr(ourScheduler.scheduler, 'Scheduler', lambda cfg: DummyScheduler([]))

    ourScheduler.display_Schedules_csv(MagicMock(), max_schedules=1)
    captured = capsys.readouterr()
    assert 'No valid schedule could be generated.' in captured.out


def test_display_csv_respects_max_schedules(monkeypatch, capsys):
    """Should limit the number of schedules printed according to max_schedules."""
    c1 = MockCourse(csv='A')
    c2 = MockCourse(csv='B')
    model1 = [c1]
    model2 = [c2]

    monkeypatch.setattr(ourScheduler.scheduler, 'Scheduler', lambda cfg: DummyScheduler([model1, model2]))

    ourScheduler.display_Schedules_csv(MagicMock(), max_schedules=1)
    captured = capsys.readouterr()
    assert 'Schedule 1' in captured.out
    assert 'Schedule 2' not in captured.out
    assert 'A' in captured.out
    assert 'B' not in captured.out
