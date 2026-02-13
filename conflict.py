
# Filename: conflict.py
# Description: Functions to add, delete, modify conflicts
# Authors: Lauryn Gilbert, Luke Leopold

from scheduler import CourseConfig
from scheduler.config import CombinedConfig

#Find courses and return their course_id's.
#Returns a courseConfig and a Course tuple.
def modifyConflict_getCourses(modifyNum: int, config: CombinedConfig):
    conflictCounter = 0
    courseIndex = 0
    conflictIndex = 0
    
    for courseIdx, course in enumerate(config.config.courses):
        for conflictIdx, conflict in enumerate(course.conflicts):
            conflictCounter += 1
            if conflictCounter == modifyNum:
                courseIndex = courseIdx
                conflictIndex = conflictIdx
                break
        if conflictCounter == modifyNum:
            break
    return (config.config.courses[courseIndex], config.config.courses[courseIndex].conflicts[conflictIndex])

# Modify JSON file to reflect modified conflict
# Modification handled differently depending on if the modified course is the course_id
# Returns True on successful modification, False otherwise 
def modifyConflict_JSON(selectedCourse: CourseConfig, selectedConflict: str, newCourse: str, modifyMode: int, config: CombinedConfig):
    """
    modifyMode == 1: Replace the left side course in the pair (A-B -> C-B):
      - remove B from A.conflicts
      - add B to C.conflicts (no duplicates)
      - in B.conflicts replace A with C

    modifyMode == 2: Replace the right side course in the pair (A-B -> A-C):
      - in A.conflicts replace B with C
      - remove A from B.conflicts
      - add A to C.conflicts (no duplicates)
    """
    old_course_id = selectedCourse.course_id

    # Defensive checks
    if not isinstance(selectedConflict, str) or not isinstance(newCourse, str):
        return False

    # ensure selectedConflict exists in the selectedCourse
    if selectedConflict not in selectedCourse.conflicts:
        return False

    if modifyMode == 1:
        selectedCourse.conflicts = [c for c in selectedCourse.conflicts if c != selectedConflict]

        for course in config.config.courses:
            if course.course_id == newCourse:
                if selectedConflict not in course.conflicts:
                    course.conflicts.append(selectedConflict)
                break

        for course in config.config.courses:
            if course.course_id == selectedConflict:
                course.conflicts = [newCourse if c == old_course_id else c for c in course.conflicts]
                break

    else:
        selectedCourse.conflicts = [newCourse if c == selectedConflict else c for c in selectedCourse.conflicts]

        for course in config.config.courses:
            if course.course_id == selectedConflict:
                course.conflicts = [c for c in course.conflicts if c != old_course_id]
                break

        for course in config.config.courses:
            if course.course_id == newCourse:
                if old_course_id not in course.conflicts:
                    course.conflicts.append(old_course_id)
                break

    return True
        
# Collect input for modifying conflicts.
def modifyconflict_input(config: CombinedConfig, config_path: str):
    conflictNum = int(0)
    coursesNum = int(0)
    print("Existing Conflicts:")
    for course in config.config.courses:
        coursesNum += 1
        for conflict in course.conflicts:
            conflictNum += 1
            print(str(conflictNum) + ": " + str(course.course_id) + " conflicts with " + conflict)            

    while(True):
        modifyNum = input("Which conflict would you like to modify? [1 - " + str(conflictNum) + "]: ").strip()
        if str.isnumeric(modifyNum) and int(modifyNum) >= 1 and int(modifyNum) <= conflictNum:
            break

    # Get selected conflict
    (selectedCourse, selectedConflict) = modifyConflict_getCourses(modifyNum=int(modifyNum), config=config)
    
    print("\nCourses in Conflict:")
    print(f"1: {selectedCourse.course_id}")
    print(f"2: {selectedConflict}")
    
    #Select which course is modified
    while(True):
        modifyNum = input("Which course would you like to modify? [1/2]: ").strip()
        if modifyNum == "1" or modifyNum == "2":
            break


    modifyCourse = ""
    if modifyNum == "1":
        modifyCourse = input(f"Replace course {selectedCourse.course_id} with: ").strip()
    else:
        modifyCourse = input(f"Replace course {selectedConflict} with: ").strip()

    #Modification confirmation
    while(True):
        confirm = input("Are you sure you want to modify this conflict? [y/n]: ").strip()
        if confirm == 'y' or confirm == 'n':
            break

    #Update json and check for errors with try/catch
    if confirm.lower() == 'y':
        modified = modifyConflict_JSON(selectedCourse=selectedCourse, selectedConflict=selectedConflict, newCourse=modifyCourse, modifyMode=int(modifyNum), config=config)
        if modified:
            # Save via runtime import to avoid circular import at module import time
            try:
                with open(config_path, 'w') as file:
                    file.write(config.model_dump_json(indent=2))
                print("Config saved.")
            except Exception:
                print("Modification applied, but failed to save config automatically.")
        else:
            print("No changes applied (validation failed or conflict not present).")
    else:
        print("Conflict Modification Cancelled.")

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
