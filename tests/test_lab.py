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
    """Unit tests for the add_lab function."""
    
    @patch('builtins.input')
    def test_add_lab_successful_with_instructor(self, mock_input):
        """Test successfully adding a lab with an instructor."""
        # Mock user inputs
        mock_input.side_effect = [
            "Computer Lab 1",           # Lab name
            "CMSC 161",                  # Course
            "Dr. Smith",                 # Instructor
            "MW",                        # Days (Monday, Wednesday)
            "10:00",                     # MON start time
            "12:00",                     # MON end time
            "14:00",                     # WED start time
            "16:00",                     # WED end time
            "y"                          # Confirmation
        ]
        
        result = add_lab()
        
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Computer Lab 1")
        self.assertEqual(result["course"], "CMSC 161")
        self.assertEqual(result["instructor"], "Dr. Smith")
        self.assertIn("MON", result["times"])
        self.assertIn("WED", result["times"])
        self.assertEqual(len(result["times"]["MON"]), 1)
        self.assertIsInstance(result["times"]["MON"][0], TimeRange)
    
    @patch('builtins.input')
    def test_add_lab_successful_without_instructor(self, mock_input):
        """Test successfully adding a lab without an instructor."""
        mock_input.side_effect = [
            "Computer Lab 2",           # Lab name
            "CMSC 140",                  # Course
            "",                          # No instructor (empty string)
            "TR",                        # Days (Tuesday, Thursday)
            "09:00",                     # TUE start time
            "11:00",                     # TUE end time
            "09:00",                     # THU start time
            "11:00",                     # THU end time
            "y"                          # Confirmation
        ]
        
        result = add_lab()
        
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Computer Lab 2")
        self.assertEqual(result["course"], "CMSC 140")
        self.assertIsNone(result["instructor"])
        self.assertIn("TUE", result["times"])
        self.assertIn("THU", result["times"])
    
    @patch('builtins.input')
    def test_add_lab_cancelled_by_user(self, mock_input):
        """Test cancelling lab creation."""
        mock_input.side_effect = [
            "Computer Lab 3",           # Lab name
            "CMSC 330",                  # Course
            "Dr. Jones",                 # Instructor
            "F",                         # Days (Friday)
            "13:00",                     # FRI start time
            "15:00",                     # FRI end time
            "n"                          # Decline confirmation
        ]
        
        result = add_lab()
        
        self.assertIsNone(result)
    
    @patch('builtins.input')
    def test_add_lab_with_all_days(self, mock_input):
        """Test adding a lab that meets every day."""
        mock_input.side_effect = [
            "Daily Lab",                # Lab name
            "CMSC 152",                  # Course
            "Prof. Daily",               # Instructor
            "MTWRF",                     # All days
            "08:00", "09:00",            # MON
            "08:00", "09:00",            # TUE
            "08:00", "09:00",            # WED
            "08:00", "09:00",            # THU
            "08:00", "09:00",            # FRI
            "y"                          # Confirmation
        ]
        
        result = add_lab()
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result["times"]), 5)
        self.assertIn("MON", result["times"])
        self.assertIn("TUE", result["times"])
        self.assertIn("WED", result["times"])
        self.assertIn("THU", result["times"])
        self.assertIn("FRI", result["times"])
    
    @patch('builtins.input')
    def test_add_lab_retries_empty_name(self, mock_input):
        """Test that empty lab name prompts retry."""
        mock_input.side_effect = [
            "",                          # Empty name (should retry)
            "   ",                       # Whitespace only (should retry)
            "Valid Lab",                 # Valid name
            "CMSC 420",                  # Course
            "",                          # No instructor
            "M",                         # Monday only
            "10:00",                     # Start time
            "12:00",                     # End time
            "y"                          # Confirmation
        ]
        
        result = add_lab()
        
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Valid Lab")
    
    @patch('builtins.input')
    def test_add_lab_retries_empty_course(self, mock_input):
        """Test that empty course prompts retry."""
        mock_input.side_effect = [
            "Lab Name",                  # Lab name
            "",                          # Empty course (should retry)
            "   ",                       # Whitespace only (should retry)
            "CMSC 476",                  # Valid course
            "Dr. Test",                  # Instructor
            "W",                         # Wednesday
            "14:00",                     # Start time
            "16:00",                     # End time
            "y"                          # Confirmation
        ]
        
        result = add_lab()
        
        self.assertIsNotNone(result)
        self.assertEqual(result["course"], "CMSC 476")
    
    @patch('builtins.input')
    def test_add_lab_retries_invalid_days(self, mock_input):
        """Test that invalid day input prompts retry."""
        mock_input.side_effect = [
            "Lab X",                     # Lab name
            "CMSC 362",                  # Course
            "",                          # No instructor
            "XYZ",                       # Invalid days (should retry)
            "123",                       # Invalid days (should retry)
            "M",                         # Valid day
            "11:00",                     # Start time
            "13:00",                     # End time
            "y"                          # Confirmation
        ]
        
        result = add_lab()
        
        self.assertIsNotNone(result)
        self.assertIn("MON", result["times"])
    
    @patch('builtins.input')
    @patch('builtins.print')
    def test_add_lab_retries_invalid_time_format(self, mock_print, mock_input):
        """Test that invalid time format prompts retry."""
        # Create a mock TimeRange that raises exception on bad format
        with patch('lab.TimeRange') as mock_timerange:
            mock_timerange.side_effect = [
                ValueError("Invalid time format"),  # First attempt fails
                TimeRange(start="10:00", end="12:00")  # Second attempt succeeds
            ]
            
            mock_input.side_effect = [
                "Lab Y",                 # Lab name
                "CMSC 340",              # Course
                "Dr. Time",              # Instructor
                "T",                     # Tuesday
                "25:00",                 # Invalid start time (first try)
                "99:99",                 # Invalid end time (first try)
                "10:00",                 # Valid start time (second try)
                "12:00",                 # Valid end time (second try)
                "y"                      # Confirmation
            ]
            
            result = add_lab()
            
            self.assertIsNotNone(result)
    
    @patch('builtins.input')
    def test_add_lab_lowercase_course_converted_to_uppercase(self, mock_input):
        """Test that course ID is converted to uppercase."""
        mock_input.side_effect = [
            "Lab Z",                     # Lab name
            "cmsc 161",                  # Lowercase course
            "",                          # No instructor
            "R",                         # Thursday
            "15:00",                     # Start time
            "17:00",                     # End time
            "y"                          # Confirmation
        ]
        
        result = add_lab()
        
        self.assertIsNotNone(result)
        self.assertEqual(result["course"], "CMSC 161")
    
    @patch('builtins.input')
    def test_add_lab_mixed_case_days(self, mock_input):
        """Test that mixed case days are handled correctly."""
        mock_input.side_effect = [
            "Mixed Lab",                 # Lab name
            "CMSC 453",                  # Course
            "Prof. Mix",                 # Instructor
            "mWf",                       # Mixed case days
            "09:00", "10:00",            # MON
            "09:00", "10:00",            # WED
            "09:00", "10:00",            # FRI
            "y"                          # Confirmation
        ]
        
        result = add_lab()
        
        self.assertIsNotNone(result)
        self.assertEqual(len(result["times"]), 3)
        self.assertIn("MON", result["times"])
        self.assertIn("WED", result["times"])
        self.assertIn("FRI", result["times"])
    
    @patch('builtins.input')
    def test_add_lab_confirmation_retry(self, mock_input):
        """Test that invalid confirmation prompts retry."""
        mock_input.side_effect = [
            "Confirm Lab",               # Lab name
            "CMSC 366",                  # Course
            "",                          # No instructor
            "F",                         # Friday
            "13:00",                     # Start time
            "15:00",                     # End time
            "maybe",                     # Invalid confirmation (should retry)
            "yes",                       # Invalid confirmation (should retry)
            "y"                          # Valid confirmation
        ]
        
        result = add_lab()
        
        self.assertIsNotNone(result)


class TestAddLabIntegration(unittest.TestCase):
    """Integration tests for add_lab with actual TimeRange objects."""
    
    @patch('builtins.input')
    def test_add_lab_creates_valid_timerange_objects(self, mock_input):
        """Test that TimeRange objects are created correctly."""
        mock_input.side_effect = [
            "Integration Lab",
            "CMSC 380",
            "Dr. Integration",
            "MW",
            "10:30",
            "12:30",
            "14:00",
            "16:00",
            "y"
        ]
        
        result = add_lab()
        
        # Verify TimeRange objects exist and have correct attributes
        mon_time = result["times"]["MON"][0]
        wed_time = result["times"]["WED"][0]
        
        self.assertIsInstance(mon_time, TimeRange)
        self.assertIsInstance(wed_time, TimeRange)
        self.assertEqual(mon_time.start, "10:30")
        self.assertEqual(mon_time.end, "12:30")
        self.assertEqual(wed_time.start, "14:00")
        self.assertEqual(wed_time.end, "16:00")


if __name__ == '__main__':
    unittest.main()
