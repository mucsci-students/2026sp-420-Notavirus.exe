# Filename: safe_save.py
# Description: Safe config saving with validation before writing to the original file

import shutil
import tempfile
import os
import json


def safe_save(config, config_path: str) -> bool:
    """
    Saves config by merging changes onto the original raw JSON dict.
    This preserves the original file's formatting and field representations
    (e.g. compact time strings) for any fields that weren't modified.

    Returns True if saved successfully, False otherwise.
    """
    try:
        valid_courses = {c.course_id for c in config.config.courses}

        # Load the original file as a raw dict to preserve formatting
        with open(config_path, 'r') as f:
            original = json.load(f)

        # Build the updated data from Pydantic but only for sections we manage
        updated = json.loads(config.model_dump_json(exclude_unset=True))

        # Selectively merge only the config section (rooms, labs, courses, faculty)
        # Leave time_slot_config, limit, optimizer_flags untouched from original
        original['config']['rooms'] = updated['config']['rooms']
        original['config']['labs'] = updated['config']['labs']
        original['config']['courses'] = updated['config']['courses']

        # For faculty, strip invalid course preferences
        updated_faculty = updated['config']['faculty']
        for faculty in updated_faculty:
            prefs = faculty.get('course_preferences', {})
            faculty['course_preferences'] = {
                k: v for k, v in prefs.items()
                if k in valid_courses
            }
        original['config']['faculty'] = updated_faculty

        dir_name = os.path.dirname(os.path.abspath(config_path))
        with tempfile.NamedTemporaryFile(mode='w', dir=dir_name, delete=False, suffix='.tmp') as tmp:
            tmp_path = tmp.name
            json.dump(original, tmp, indent=2)

        shutil.move(tmp_path, config_path)
        print("Changes saved successfully.")
        return True

    except Exception as e:
        print(f"Error during save: {e}")
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False