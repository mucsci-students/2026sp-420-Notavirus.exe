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


# Add a conflict between two courses
# Preconditions: User knows the course IDs involved.
# Postconditions: Conflict information is collected.
def addConflict(config_path: str):
    config = load_config_from_file(CombinedConfig, config_path)
    scheduler_config = config.config

    if not scheduler_config.courses:
        print("There are no courses in the configuration.")
        return

    print("\nExisting Courses:")
    for course in scheduler_config.courses:
        print(f"- {course.course_id}")

    while True:
        # Prompt for the first course
        course_1 = input("\nEnter the first course ID: ").strip().upper()
        if course_1:
            break

    while True:
        # Prompt for the conflicting course
        course_2 = input("Enter the conflicting course ID: ").strip().upper()
        if course_2:
            break

    if course_1 == course_2:
        print("A course cannot conflict with itself.")
        return

    matching_1 = [c for c in scheduler_config.courses if c.course_id == course_1]
    matching_2 = [c for c in scheduler_config.courses if c.course_id == course_2]

    # If course ID is not found, exit
    if not matching_1 or not matching_2:
        print("One or both course IDs not found.")
        return

    print("\nConflict Summary:")
    print(f"- {course_1} conflicts with {course_2}")

    # Confirm conflict
    while True:
        confirm = input("Add this conflict? [y/n]: ").lower()
        if confirm in ('y', 'n'):
            break

    if confirm == 'n':
        print("Conflict addition canceled.")
        return

    # Add conflict to each course (c1 conflicts with c2, c2 conflicts with c1)
    try:
        with scheduler_config.edit_mode() as editable:
            c1 = next(c for c in editable.courses if c.course_id == course_1)
            c2 = next(c for c in editable.courses if c.course_id == course_2)

            if course_2 not in c1.conflicts:
                c1.conflicts.append(course_2)

            if course_1 not in c2.conflicts:
                c2.conflicts.append(course_1)

    except Exception as e:
        print(f"Error adding conflict: {e}")
        return

    # Save back to the config file
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))

    print("Conflict added successfully.")

# For testing add conflict file
def addConflict_config(course_list, course_id_1, course_id_2):
    #Adds a mutual conflict between two courses.
    #Returns True if successful, False otherwise.

    if course_id_1 == course_id_2:
        return False

    c1 = next((c for c in course_list if c.course_id == course_id_1), None)
    c2 = next((c for c in course_list if c.course_id == course_id_2), None)

    if c1 is None or c2 is None:
        return False

    if course_id_2 not in c1.conflicts:
        c1.conflicts.append(course_id_2)

    if course_id_1 not in c2.conflicts:
        c2.conflicts.append(course_id_1)

    return True


# function deleteConflict
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

