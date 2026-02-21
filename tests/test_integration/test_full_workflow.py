import pytest
from controllers.app_controller import SchedulerController
from controllers.faculty_controller import ADJUNCT_MAX_CREDITS
import json
import os
from pathlib import Path
import sys

@pytest.fixture
def test_config(tmp_path):
    """Create a temporary config file for testing."""
    config_data = {
        "config": {
            "rooms": ["Room A", "Room B"],
            "labs": ["Lab X", "Lab Y"],
            "faculty": [],
            "courses": []
        },
        "time_slot_config": {
            "times": {
                "MON": [{"start": "08:00", "spacing": 60, "end": "19:00"}],
                "TUE": [{"start": "08:00", "spacing": 60, "end": "19:00"}],
                "WED": [{"start": "08:00", "spacing": 60, "end": "19:00"}],
                "THU": [{"start": "08:00", "spacing": 60, "end": "19:00"}],
                "FRI": [{"start": "08:00", "spacing": 60, "end": "19:00"}]
            },
            "classes": [
                {
                    "credits": 3,
                    "meetings": [
                        {"day": "MON", "duration": 50},
                        {"day": "WED", "duration": 50},
                        {"day": "FRI", "duration": 50}
                    ]
                }
            ]
        },
        "limit": 1
    }
    config_file = tmp_path / "test_config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
    return str(config_file)

def setup_mock_input(monkeypatch, inputs_list):
    inputs_iter = iter(inputs_list)
    def mock_input(prompt=""):
        try:
            val = next(inputs_iter)
            print(f"\n[INPUT_MOCK] Prompt: '{prompt.strip()}' -> Returning: '{val}'")
            return val
        except StopIteration:
            print(f"\n[INPUT_MOCK] Prompt: '{prompt.strip()}' -> ERROR: StopIteration (inputs exhausted)")
            raise
    monkeypatch.setattr('builtins.input', mock_input)

def test_faculty_crud_workflow(test_config, monkeypatch):
    controller = SchedulerController(test_config)
    setup_mock_input(monkeypatch, [
        '1', 'John Doe', 'y', 'MTWRF', '', 'y', # Add Faculty
        '2', 'John Doe', '1', 'n',               # Modify Position (Choice 1 -> 'n')
        '3', 'John Doe', 'y',                   # Delete Faculty
        '19'                                    # Exit
    ])
    controller.run()
    
    # Verify faculty addition/modification/deletion happened as expected
    # The delete happened last so it should be None
    assert controller.faculty_model.get_faculty_by_name("John Doe") is None

def test_course_crud_workflow(test_config, monkeypatch):
    controller = SchedulerController(test_config)
    setup_mock_input(monkeypatch, [
        '1', 'Jane Smith', 'y', 'MTWRF', '', 'y', # Faculty pre-req
        '4', 'CMSC 101', '3', 'Room A', '', 'Lab X', '', 'Jane Smith', '', '', 'y', # Add Course
        '5', 'CMSC 101', '4', 'Room B', 'Lab Y', '', '', 'y', # Modify Course (credits, room, lab, faculty="", conflict="", confirm="y")
        '6', 'CMSC 101.01', 'y', # Delete Course
        '19'
    ])
    controller.run()
    assert len(controller.course_model.get_all_courses()) == 0

def test_full_workflow_end_to_end(test_config, monkeypatch, tmp_path):
    controller = SchedulerController(test_config)
    output_file = tmp_path / "final_schedule.csv"
    
    setup_mock_input(monkeypatch, [
        '1', 'Dr. Smith', 'y', 'MTWRF', '', 'y', # Add Faculty
        '4', 'CMSC 301', '3', 'Room A', '', 'Lab X', '', 'Dr. Smith', '', '', 'y', # Add Course
        '17', '1', 'y', str(output_file), 'csv', # Run Scheduler
        '19' # Exit
    ])
    
    controller.run()
    
    output_path = Path(str(output_file))
    assert output_path.exists()
    
    with open(output_path, 'r') as f:
        content = f.read()
        assert "CMSC 301" in content
        assert "Dr. Smith" in content
