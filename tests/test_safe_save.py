import os
import json
from safe_save import save_configuration


def test_safe_save_temp(tmp_path):
    # Setup initial config file
    config_file = tmp_path / "config.json"
    initial_data = {
        "config": {"rooms": ["Room1"], "labs": ["Lab1"], "courses": [], "faculty": []}
    }
    with open(config_file, "w") as f:
        json.dump(initial_data, f)

    # Create CombinedConfig equivalent to Pydantic Model output
    class MockConfig:
        class ConfigSection:
            rooms = ["Room1", "Room2"]
            labs = ["Lab1"]
            courses = []
            faculty = []

        config = ConfigSection()

        def model_dump_json(self, exclude_unset=True):
            return json.dumps(
                {
                    "config": {
                        "rooms": ["Room1", "Room2"],
                        "labs": ["Lab1"],
                        "courses": [],
                        "faculty": [],
                    }
                }
            )

    mock_config = MockConfig()

    # Perform 'temp' save for rooms
    success = save_configuration(mock_config, str(config_file), "temp", "rooms")
    assert success is True

    # Check that temp file exists and has new rooms
    temp_file = str(config_file) + ".temp"
    assert os.path.exists(temp_file)
    with open(temp_file, "r") as f:
        temp_data = json.load(f)
    assert temp_data["config"]["rooms"] == ["Room1", "Room2"]

    # Check that original file was not mutated
    with open(config_file, "r") as f:
        original_data = json.load(f)
    assert original_data["config"]["rooms"] == ["Room1"]

    # Perform 'config' save to merge
    success = save_configuration(mock_config, str(config_file), "config", "rooms")
    assert success is True

    # Check that original file has new rooms
    with open(config_file, "r") as f:
        original_data = json.load(f)
    assert original_data["config"]["rooms"] == ["Room1", "Room2"]

    # Check that temp file is deleted
    assert not os.path.exists(temp_file)
