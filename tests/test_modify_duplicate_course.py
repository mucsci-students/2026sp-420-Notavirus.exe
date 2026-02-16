import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from course import modifyCourse
# Only import what we know exists
from scheduler.config import CombinedConfig, CourseConfig

class TestModifyDuplicateCourse(unittest.TestCase):
    @patch('course.load_config_from_file')
    @patch('builtins.input')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('course.CombinedConfig')
    def test_modify_multiple_instances(self, mock_combined_config, mock_open, mock_input, mock_load):
        # Setup mock config with duplicates
        course1 = CourseConfig(course_id="CS101", credits=3, conflicts=[], room=[], lab=[], faculty=[])
        course2 = CourseConfig(course_id="CS101", credits=3, conflicts=[], room=[], lab=[], faculty=[])
        
        # Create a mock SchedulerConfig
        mock_scheduler_config = MagicMock()
        mock_scheduler_config.courses = [course1, course2]
        
        # Create a mock CombinedConfig
        mock_config = MagicMock(spec=CombinedConfig)
        mock_config.config = mock_scheduler_config
        
        # Setup edit_mode
        mock_editable = MagicMock()
        mock_editable.courses = [course1, course2]
        mock_scheduler_config.edit_mode.return_value.__enter__.return_value = mock_editable
        
        mock_load.return_value = mock_config
        
        # Scenario: Change credits to 4 for CS101
        # Logic: 
        # 1. Course ID input: "CS101"
        # 2. Credits: "4"
        # 3. Room: "" (unchanged)
        # 4. Lab: "" (unchanged)
        # 5. Faculty: "" (unchanged)
        # 6. Confirm: "y"
        mock_input.side_effect = ["CS101", "4", "", "", "", "y"] 
        
        # Run modification
        modifyCourse("dummy_path.json")
        
        # Verify BOTH instances have 4 credits
        print(f"Course 1 credits: {course1.credits}")
        print(f"Course 2 credits: {course2.credits}")
        
        self.assertEqual(course1.credits, 4, "Course 1 should have 4 credits")
        self.assertEqual(course2.credits, 4, "Course 2 should have 4 credits")

if __name__ == '__main__':
    unittest.main()
