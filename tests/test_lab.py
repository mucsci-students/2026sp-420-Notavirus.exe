# test_lab.py
import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to Python path so imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from lab import add_lab
from scheduler import TimeRange


class TestAddLab(unittest.TestCase):
    """Tests for the add_lab function (returns str lab name)."""

    @patch('builtins.input')
    def test_add_lab_valid_name(self, mock_input):
        """Test adding a lab with a valid name."""
        mock_input.side_effect = [
            "Python Lab",  # Lab name
            "y"            # Confirm
        ]

        result = add_lab()
        
        self.assertEqual(result, "Python Lab")

    @patch('builtins.input')
    def test_add_lab_empty_name_retry(self, mock_input):
        """Test retrying after entering an empty lab name."""
        mock_input.side_effect = [
            "",              # Empty name (invalid)
            "Valid Lab",     # Valid name
            "y"              # Confirm
        ]

        result = add_lab()
        
        self.assertEqual(result, "Valid Lab")

    @patch('builtins.input')
    def test_add_lab_confirm_yes(self, mock_input):
        """Test confirming lab addition with 'yes'."""
        mock_input.side_effect = [
            "Data Structures Lab",
            "y"
        ]

        result = add_lab()
        
        self.assertIsNotNone(result)
        self.assertEqual(result, "Data Structures Lab")

    @patch('builtins.input')
    def test_add_lab_cancel(self, mock_input):
        """Test canceling the lab addition (restart with 'n')."""
        mock_input.side_effect = [
            "Test Lab",
            "n",  # Confirm: no
            "n"   # Restart: no
        ]

        result = add_lab()
        
        self.assertIsNone(result)

    @patch('builtins.input')
    def test_add_lab_restart_and_confirm(self, mock_input):
        """Test restarting lab entry and then confirming."""
        mock_input.side_effect = [
            # First attempt (will cancel and restart)
            "Bad Lab",
            "n",    # Confirm: no
            "y",    # Restart: yes
            # Second attempt (will succeed)
            "Good Lab",
            "y"     # Confirm: yes
        ]

        result = add_lab()
        
        self.assertEqual(result, "Good Lab")

    @patch('builtins.input')
    def test_add_lab_restart_cancel(self, mock_input):
        """Test canceling and choosing not to restart."""
        mock_input.side_effect = [
            "Lab to Discard",
            "n",  # Confirm: no
            "n"   # Restart: no (cancel completely)
        ]

        result = add_lab()
        
        self.assertIsNone(result)

    @patch('builtins.input')
    def test_add_lab_with_spaces(self, mock_input):
        """Test that lab name with spaces is preserved."""
        mock_input.side_effect = [
            "  Advanced Algorithms Lab  ",  # Name with leading/trailing spaces
            "y"
        ]

        result = add_lab()
        
        # .strip() is called in add_lab, so spaces should be removed
        self.assertEqual(result, "Advanced Algorithms Lab")

    @patch('builtins.input')
    def test_add_lab_special_characters(self, mock_input):
        """Test lab name with special characters."""
        mock_input.side_effect = [
            "Lab-C++ (Intro)",
            "y"
        ]

        result = add_lab()
        
        self.assertEqual(result, "Lab-C++ (Intro)")

    @patch('builtins.input')
    def test_add_lab_numeric_name(self, mock_input):
        """Test lab with a numeric name."""
        mock_input.side_effect = [
            "CS101",
            "y"
        ]

        result = add_lab()
        
        self.assertEqual(result, "CS101")

    @patch('builtins.input')
    def test_add_lab_long_name(self, mock_input):
        """Test lab with a long name."""
        long_name = "Advanced Object-Oriented Programming and Design Patterns Laboratory"
        mock_input.side_effect = [
            long_name,
            "y"
        ]

        result = add_lab()
        
        self.assertEqual(result, long_name)


if __name__ == '__main__':
    unittest.main()
