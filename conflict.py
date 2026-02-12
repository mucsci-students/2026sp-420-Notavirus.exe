# Filename: conflict.py
# Description: Functions to add, delete, modify conflicts
# Authors: Lauryn Gilbert

from scheduler.config import CombinedConfig

# Global Variables
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 3
MIN_DAYS = 1
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1

# deleteConflict takes an existing conflict and removes it from the 
#  config file specified by the user
#
# Parameters: 
#   config - calls load_config_from_file on config_path to load the config file
#   config_path str - the file to load that is input by the user
# Preconditions: 
#   - The config must contain at least one conflict.  
#   - The conflict intended to delete must already exist in the config_path file.
# Postconditions: 
#   - The conflict will no longer exist in the config_path file. 
#   - If no conflicts exists, a message would be in the Command-Line and no 
#      changes to the config will occur 
#   - If the conflict entered does not exist, a message will exist in the 
#      Command-Line letting the user know and no changes will be made to the 
#      config file
# Return: none
def deleteConflict(config: CombinedConfig, config_path: str):
    scheduler_config = config.config

    # Build list of existing conflicts
    existing_conflicts = []
    for course in scheduler_config.courses:
        for conflict in course.conflicts:
            pair = tuple(sorted([course.course_id, conflict]))
            if pair not in existing_conflicts:
                existing_conflicts.append(pair)

    if not existing_conflicts:
        print("There are no conflicts currently in the configuration.")
        return

    # Get all valid course IDs
    valid_courses = {course.course_id for course in scheduler_config.courses}

    # Display existing conflicts
    print("\nExisting Conflicts:")
    for i, (a, b) in enumerate(existing_conflicts, 1):
        print(f"{i}. {a} <-> {b}")

    # Prompt for the first course and validate it exists
    while True:
        course_1 = input("\nEnter the first course ID (e.g. 'CMSC 100'): ").strip().upper()
        if course_1 == "":
            print("Course ID cannot be empty.")
        elif course_1 not in valid_courses:
            print(f"Error: '{course_1}' is not a valid course. Valid courses are: {', '.join(sorted(valid_courses))}")
        else:
            break

    # Prompt for the second course and validate it exists AND conflicts with course_1
    while True:
        course_2 = input("Enter the conflicting course ID (e.g. 'CMSC 100'): ").strip().upper()
        if course_2 == "":
            print("Course ID cannot be empty.")
        elif course_2 not in valid_courses:
            print(f"Error: '{course_2}' is not a valid course. Valid courses are: {', '.join(sorted(valid_courses))}")
        elif course_2 == course_1:
            print("Error: A course cannot conflict with itself.")
        elif tuple(sorted([course_1, course_2])) not in existing_conflicts:
            print(f"Error: No conflict exists between '{course_1}' and '{course_2}'.")
        else:
            break

    # Display summary
    print("\nConflict Summary:")
    print(f"- {course_1} <-> {course_2}")

    # Confirm deletion
    while True:
        confirm = input("Delete this conflict? [y/n]: ").lower().strip()
        if confirm in ('y', 'n'):
            break

    if confirm == 'n':
        print("Conflict deletion canceled.")
        return

    # Remove the conflict from both courses
    try:
        with scheduler_config.edit_mode() as editable:
            for course in editable.courses:
                if course.course_id == course_1 and course_2 in course.conflicts:
                    course.conflicts.remove(course_2)
                elif course.course_id == course_2 and course_1 in course.conflicts:
                    course.conflicts.remove(course_1)
    except Exception as e:
        print(f"\nError: Failed to remove conflict due to validation error: {e}")
        return

    # Save back to the config file
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))

    print(f"\nConflict between '{course_1}' and '{course_2}' has been permanently deleted.")




# Add a conflict between two courses
# Preconditions: User knows the course IDs involved.
# Postconditions: Conflict information is collected.
def addConflict():
    # Prompt for the first course
    while True:
        course_1 = input("Enter the first course ID: ").strip()
        if course_1 != "":
            break

    # Prompt for the conflicting course
    while True:
        course_2 = input("Enter the conflicting course ID: ").strip()
        if course_2 != "":
            break

    # Display summary of the conflict being added
    print("\nConflict Summary:")
    print(f"- {course_1} conflicts with {course_2}")

    # Confirm conflict addition
    while True:
        confirm = input("Add this conflict? [y/n]: ").lower().strip()
        if confirm in ('y', 'n'):
            break
    if confirm == 'y':
        # Note: Actual conflict storage will occur once courses exist
        print("Conflict recorded.")
    else:
        print("Conflict addition canceled.")