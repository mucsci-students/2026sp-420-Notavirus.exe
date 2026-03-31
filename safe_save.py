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

    This is a backward-compatible wrapper that simply calls save_configuration
    for an 'all' feature save to the main config.

    Returns True if saved successfully, False otherwise.
    """
    return save_configuration(config, config_path, save_type="config", feature="all")


def save_configuration(
    config, config_path: str, save_type: str, feature: str = "all"
) -> bool:
    """
    Saves configuration data safely, supporting progressive temporary saves.

    Args:
        config: The CombinedConfig model containing current in-memory data.
        config_path: Path to the main configuration JSON file.
        save_type: 'temp' (saves to a .temp file) or 'config' (commits .temp to main config file).
        feature: The specific feature section to save (e.g., 'faculty', 'courses', 'rooms', 'labs', 'all').

    Returns:
        bool: True if saved successfully, False otherwise.
    """
    try:
        temp_path = config_path + ".temp"
        valid_courses = {c.course_id for c in config.config.courses}

        # Build the updated data from Pydantic but only for sections we manage
        updated = json.loads(config.model_dump_json(exclude_unset=True))

        # Determine the target file to read as our baseline
        target_read_path = config_path
        if save_type == "temp" and os.path.exists(temp_path):
            target_read_path = temp_path

        # Load baseline data
        if os.path.exists(target_read_path):
            with open(target_read_path, "r") as f:
                target_data = json.load(f)
        else:
            # If no file exists yet (imported config), use in-memory config
            target_data = json.loads(config.model_dump_json())

        # Helper to apply a specific feature update to the dictionary
        def update_feature(feat_name):
            if feat_name in ["rooms", "labs", "courses"]:
                target_data["config"][feat_name] = updated["config"][feat_name]
            elif feat_name == "faculty":
                existing_raw_list = target_data["config"].get("faculty", [])
                existing_raw_by_name = {fac["name"]: fac for fac in existing_raw_list}
                in_memory_faculty = updated["config"]["faculty"]
                in_memory_by_name = {fac["name"]: fac for fac in in_memory_faculty}

                result = []

                # Process existing faculty in their original order.
                # Merge in-memory changes but preserve the original 'times' format
                # (e.g. "11:00-16:00" strings) so saves don't reformat existing entries.
                # Faculty not in memory anymore were deleted -- they are skipped.
                for raw_fac in existing_raw_list:
                    name = raw_fac["name"]
                    if name not in in_memory_by_name:
                        continue  # deleted
                    mem_fac = in_memory_by_name[name]
                    merged = raw_fac.copy()
                    for key, val in mem_fac.items():
                        if key == "times":
                            merged[key] = val
                        elif key == "course_preferences":
                            merged[key] = {
                                k: v for k, v in val.items() if k in valid_courses
                            }
                        else:
                            merged[key] = val
                    result.append(merged)

                # Append new faculty (in memory but not in the original JSON)
                for fac in in_memory_faculty:
                    if fac["name"] not in existing_raw_by_name:
                        prefs = fac.get("course_preferences", {})
                        fac["course_preferences"] = {
                            k: v for k, v in prefs.items() if k in valid_courses
                        }
                        result.append(fac)

                target_data["config"]["faculty"] = result

        # Apply updates based on feature argument
        if feature == "all":
            for feat in ["rooms", "labs", "courses", "faculty"]:
                update_feature(feat)
        else:
            update_feature(feature)

        dir_name = os.path.dirname(os.path.abspath(config_path))

        # Write to a proper safe temporary file first
        with tempfile.NamedTemporaryFile(
            mode="w", dir=dir_name, delete=False, suffix=".tmp"
        ) as tmp:
            safe_tmp_path = tmp.name
            json.dump(target_data, tmp, indent=2)

        if save_type == "temp":
            # Move our safe tmp file to the .temp accumulator file
            shutil.copy(safe_tmp_path, temp_path)
            os.remove(safe_tmp_path)
            print(f"Temporary changes for '{feature}' saved successfully.")

        elif save_type == "config":
            # This is a master commit save.
            # Move our fully updated accumulator (safe_tmp_path) to the actual config file
            shutil.copy(safe_tmp_path, config_path)
            os.remove(safe_tmp_path)

            # Clean up the .temp file since we've committed to main
            if os.path.exists(temp_path):
                os.remove(temp_path)

            print("Configuration committed successfully.")

        return True

    except Exception as e:
        print(f"Error during save: {e}")
        if "safe_tmp_path" in locals() and os.path.exists(safe_tmp_path):
            os.remove(safe_tmp_path)
        return False
