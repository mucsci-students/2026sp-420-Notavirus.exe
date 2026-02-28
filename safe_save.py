# Filename: safe_save.py
# Description: Safe config saving with validation before writing to the original file
import shutil
import tempfile
import os


def safe_save(config, config_path: str) -> bool:
    """
    Writes config to a temporary file and only overwrites the original if
    the write succeeds.

    Strips faculty course preferences that reference courses not present in
    the configuration before writing, since hypothetical course preferences
    are allowed in-memory but must be valid on disk.

    Returns True if saved successfully, False otherwise.
    """
    try:
        # Get valid course IDs
        valid_courses = {c.course_id for c in config.config.courses}

        # Strip invalid course preferences before writing
        for faculty in config.config.faculty:
            faculty.course_preferences = {
                k: v for k, v in faculty.course_preferences.items()
                if k in valid_courses
            }

        dir_name = os.path.dirname(os.path.abspath(config_path))
        with tempfile.NamedTemporaryFile(mode='w', dir=dir_name, delete=False, suffix='.tmp') as tmp:
            tmp_path = tmp.name
            tmp.write(config.model_dump_json(indent=2))

        shutil.move(tmp_path, config_path)
        print("Changes saved successfully.")
        return True

    except Exception as e:
        print(f"Error during save: {e}")
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False