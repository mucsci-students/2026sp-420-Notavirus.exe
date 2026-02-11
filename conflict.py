# conflict.py
# Functions to add/delete/modify conflict

from scheduler import load_config_from_file, Day, TimeRange
from scheduler.config import CombinedConfig

# Global Variables
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 3
MIN_DAYS = 1
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1

def deleteConflict(config_path: str):
    # Load the config
    config = load_config_from_file(CombinedConfig, config_path)
    scheduler_config = config.config

    # Build list of existing conflicts
    existing_conflicts = []
    for course in scheduler_config.courses:
        for conflict in course.conflicts:
            pair = tuple(sorted([course.course_id, conflict]))
            if pair not in existing_conflicts:
                existing_conflicts.append(pair)

    # Check if there are any conflicts
    if not existing_conflicts:
        print("There are no conflicts currently in the configuration.")
        return

    # Display existing conflicts
    print("\nExisting Conflicts:")
    for i, (a, b) in enumerate(existing_conflicts, 1):
        print(f"{i}. {a} <-> {b}")

    # Prompt for the first course
    while True:
        course_1 = input("\nEnter the first course ID: ").strip().upper()
        if course_1 != "":
            break

    # Prompt for the second course
    while True:
        course_2 = input("Enter the conflicting course ID: ").strip().upper()
        if course_2 != "":
            break

    # Check if the conflict exists
    pair = tuple(sorted([course_1, course_2]))
    if pair not in existing_conflicts:
        print(f"\nError: No conflict exists between '{course_1}' and '{course_2}'. No changes were made.")
        return

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