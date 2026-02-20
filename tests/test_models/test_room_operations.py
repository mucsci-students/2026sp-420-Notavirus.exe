import scheduler
import room
import pytest
import shutil


#creates a temporary config file when called for the test
@pytest.fixture
def fresh_config(tmp_path, monkeypatch):
    temp_file = tmp_path / "test_config.json"
    shutil.copy("example.json", temp_file)

    room.loadedConfig = scheduler.load_config_from_file(
        scheduler.CombinedConfig,
        temp_file
    )

    # Override configFile used by saveRoomsToFile
    monkeypatch.setattr(room, "configFile", str(temp_file))

    return room.loadedConfig


#add a room with correct format

def test_addRoom(fresh_config):
    room.addRoom("Roddy 141")
    assert room.loadedConfig.config.rooms == ["Roddy 136", "Roddy 140", "Roddy 147", "Roddy 141"], f"failed addRoom test: result{fresh_config}"

#attempt to add a room already exists
def test_addExistingRoom(fresh_config):
    room.addRoom("Roddy 140")
    assert room.loadedConfig.config.rooms == ["Roddy 136", "Roddy 140", "Roddy 147"], f"test addExistingRoom failed: result{fresh_config}"
    

#tests for modifying a room test the function replaceRoom()
#replaceRoom() is where the actual modifying happens, modRoom() consists of prompts for info, then calls replaceRoom()

#modify a room you know has no conflicts, into a room that has no conflicts (testing replaceRoom)
def test_modRoomNoConflicts(fresh_config):
    room.addRoom("Roddy 141")
    room.replaceRoom("Roddy 141", "Roddy 150")
    assert room.loadedConfig.config.rooms == ["Roddy 136", "Roddy 140", "Roddy 147", "Roddy 150"], f"modRoomNoConflicts failed: result{fresh_config}"
#modify a room into something that creates config conflicts
def test_modRoomWithConflict(fresh_config):
    room.replaceRoom("Roddy 140", "Roddy 151")
    assert room.loadedConfig.config.rooms == ["Roddy 136", "Roddy 140", "Roddy 147"], f"modRoomWithConflict failed: result{fresh_config}"
#modify a room into an existing room
def test_modRoomIntoExistingRoom(fresh_config):
    room.replaceRoom("Roddy 150", "Roddy 140")
    assert room.loadedConfig.config.rooms == ["Roddy 136", "Roddy 140", "Roddy 147"], f"modRoomIntoExistingRoom failed: result{fresh_config}"
#modify a room into a blank string
def test_modRoomIntoBlankRoom(fresh_config):
    room.replaceRoom("Roddy 150", "" )
    assert room.loadedConfig.config.rooms == ["Roddy 136", "Roddy 140", "Roddy 147"], f"modRoomIntoBlankRoom failed: result{fresh_config}"