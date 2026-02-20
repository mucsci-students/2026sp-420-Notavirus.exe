# test_room.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to Python path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from room import deleteRoom

class TestDeleteRoom(unittest.TestCase):
    @patch("room.load_config_from_file")
    @patch("builtins.print")
    def test_no_rooms_exist(self, mock_print, mock_load):
        """Test behavior when there are no rooms."""
        mock_config = MagicMock()
        mock_config.config.rooms = []
        mock_load.return_value = mock_config

        deleteRoom("fake_path.json")

        mock_print.assert_any_call("There are no rooms in the configuration.")

    @patch("room.load_config_from_file")
    @patch("builtins.input", side_effect=["NonExistentRoom"])
    @patch("builtins.print")
    def test_room_not_found(self, mock_print, mock_input, mock_load):
        """Test when room does not exist."""
        mock_config = MagicMock()
        mock_config.config.rooms = ["RoomA", "RoomB"]
        mock_config.config.courses = []
        mock_config.config.faculty = []
        mock_load.return_value = mock_config

        deleteRoom("fake_path.json")

        mock_print.assert_any_call(
            "\nError: No room 'NonExistentRoom' found. No changes were made."
        )

    @patch("room.load_config_from_file")
    @patch("builtins.input", side_effect=["RoomA", "n"])
    @patch("builtins.print")
    def test_user_cancels_deletion(self, mock_print, mock_input, mock_load):
        """Test cancellation flow."""
        mock_config = MagicMock()
        mock_config.config.rooms = ["RoomA"]
        mock_config.config.courses = []
        mock_config.config.faculty = []
        mock_load.return_value = mock_config

        deleteRoom("fake_path.json")

        mock_print.assert_any_call("Deletion canceled.")

    @patch("room.load_config_from_file")
    @patch("builtins.input", side_effect=["RoomA", "y"])
    @patch("builtins.print")
    @patch("json.dump")
    def test_successful_room_deletion(
        self, mock_json_dump, mock_print, mock_input, mock_load
    ):
        """Test full successful deletion including cleanup."""
        # Mock course with room reference
        mock_course = MagicMock()
        mock_course.room = ["RoomA", "RoomB"]

        # Mock faculty with room preference
        mock_faculty = MagicMock()
        mock_faculty.room_preferences = {"RoomA": 5, "RoomC": 3}

        mock_config = MagicMock()
        mock_config.config.rooms = ["RoomA", "RoomB"]
        mock_config.config.courses = [mock_course]
        mock_config.config.faculty = [mock_faculty]
        mock_config.model_dump.return_value = {}
        mock_load.return_value = mock_config

        deleteRoom("fake_path.json")

        # Room removed from rooms list
        self.assertNotIn("RoomA", mock_config.config.rooms)

        # Room removed from course
        self.assertNotIn("RoomA", mock_course.room)

        # Room removed from faculty preferences
        self.assertNotIn("RoomA", mock_faculty.room_preferences)

        mock_print.assert_any_call("\nRoom 'RoomA' has been successfully deleted.")

    @patch("room.load_config_from_file")
    @patch("builtins.input", side_effect=["RoomA", "maybe", "Y"])
    @patch("builtins.print")
    @patch("json.dump")
    def test_invalid_confirmation_input(
        self, mock_json_dump, mock_print, mock_input, mock_load
    ):
        """Test that invalid confirmation input is retried until valid."""
        mock_course = MagicMock()
        mock_course.room = ["RoomA"]
        mock_faculty = MagicMock()
        mock_faculty.room_preferences = {"RoomA": 1}

        mock_config = MagicMock()
        mock_config.config.rooms = ["RoomA"]
        mock_config.config.courses = [mock_course]
        mock_config.config.faculty = [mock_faculty]
        mock_config.model_dump.return_value = {}
        mock_load.return_value = mock_config

        deleteRoom("fake_path.json")

        # Room removed properly
        self.assertNotIn("RoomA", mock_config.config.rooms)
        self.assertNotIn("RoomA", mock_course.room)
        self.assertNotIn("RoomA", mock_faculty.room_preferences)

        # Success message printed
        mock_print.assert_any_call("\nRoom 'RoomA' has been successfully deleted.")


if __name__ == "__main__":
    unittest.main()