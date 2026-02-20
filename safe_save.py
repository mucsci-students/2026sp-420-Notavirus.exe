# Filename: safe_save.py
# Description: Safe config saving with validation before writing to the original file
import shutil
import tempfile
import os
from scheduler import load_config_from_file
from scheduler.config import CombinedConfig


def safe_save(config: CombinedConfig, config_path: str) -> bool:
    """
    Writes config to a temporary file, validates it, and only overwrites
    the original if validation passes.

    Returns True if saved successfully, False if validation failed.
    """
    try:
        # Write to a temp file in the same directory as the original
        dir_name = os.path.dirname(config_path)
        with tempfile.NamedTemporaryFile(mode='w', dir=dir_name, delete=False, suffix='.tmp') as tmp:
            tmp_path = tmp.name
            tmp.write(config.model_dump_json(indent=2))

        # Validate by reloading from the temp file
        try:
            load_config_from_file(CombinedConfig, tmp_path)
        except Exception as e:
            print(f"Validation failed, changes not saved: {e}")
            os.remove(tmp_path)
            return False

        # Validation passed — replace the original
        shutil.move(tmp_path, config_path)
        print("Changes saved successfully.")
        return True

    except Exception as e:
        print(f"Error during save: {e}")
        # Clean up temp file if it exists
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)
        return False