import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from course import modifyCourse
# Only import what we know exists
from scheduler.config import CombinedConfig, CourseConfig

class TestModifyFaculty(unittest.TestCase):
    @patch('course.load_config_from_file')
    @patch('builtins.input')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    @patch('course.CombinedConfig')
    def test_modify_faculty_add_remove(self, mock_combined_config, mock_open, mock_input, mock_load):
        # Setup mock config
        course = CourseConfig(course_id="CS101", credits=3, conflicts=[], room=[], lab=[], faculty=["Prof A"])
        
        # Create a mock SchedulerConfig
        mock_scheduler_config = MagicMock()
        mock_scheduler_config.courses = [course]
        
        # Create a mock CombinedConfig
        mock_config = MagicMock(spec=CombinedConfig)
        mock_config.config = mock_scheduler_config
        
        # Setup edit_mode
        mock_editable = MagicMock()
        mock_editable.courses = [course]
        mock_scheduler_config.edit_mode.return_value.__enter__.return_value = mock_editable
        
        mock_load.return_value = mock_config
        
        # Scenario 1: Add "Prof B"
        # Logic: 
        # 1. Course ID input: "CS101"
        # 2. Credits: "" (unchanged)
        # 3. Room: "" (unchanged)
        # 4. Lab: "" (unchanged)
        # 5. Faculty: "Prof B" (Add)
        # 6. Confirm: "y"
        mock_input.side_effect = ["CS101", "", "", "", "Prof B", "y"] 
        
        # Run modification
        modifyCourse("dummy_path.json")
        
        # Verify "Prof B" added, "Prof A" kept
        print(f"Faculty after Add: {course.faculty}")
        self.assertIn("Prof A", course.faculty)
        self.assertIn("Prof B", course.faculty)
        
        # Reset side_effect for next run
        # Scenario 2: Remove "Prof A"
        # 1. Course ID input: "CS101"
        # 2. Credits: ""
        # 3. Room: ""
        # 4. Lab: ""
        # 5. Faculty: "-Prof A" (Remove)
        # 6. Confirm: "y"
        mock_input.side_effect = ["CS101", "", "", "", "-Prof A", "y"]
        
        modifyCourse("dummy_path.json")
        
        # Verify "Prof A" removed
        print(f"Faculty after Remove: {course.faculty}")
        self.assertNotIn("Prof A", course.faculty)
        self.assertIn("Prof B", course.faculty)

if __name__ == '__main__':
    unittest.main()
