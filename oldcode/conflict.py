# conflict.py
# Functions to add/delete/modify conflict
# Authors: Lauryn Gilbert, Hailey Haldeman, Luke Leopold, Brooks Stouffer, Ashton Kunkle, Phinehas Maina, Keller Emswiler.


from scheduler import load_config_from_file, Day, TimeRange
from scheduler.config import CombinedConfig, CourseConfig
from safe_save import safe_save

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

    conflictNum = int(0)
    coursesNum = int(0)
    print("Existing Conflicts:")
    for course in config.config.courses:
        coursesNum += 1
        for conflict in course.conflicts:
            conflictNum += 1
            print(str(conflictNum) + ": " + str(course.course_id) + " conflicts with " + conflict)  

    while True:
        # Prompt for the first course
        course_1 = input("\nEnter the first course ID: ").strip().upper()
        if not course_1:
            continue
            
        # Check if course exists
        exists = False
        for course in scheduler_config.courses:
            if course.course_id == course_1:
                exists = True
                break
        
        if exists:
            break
        print(f"Course '{course_1}' not found.")

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
            # Find ALL courses matching the IDs in the editable config
            c1_list = [c for c in editable.courses if c.course_id == course_1]
            c2_list = [c for c in editable.courses if c.course_id == course_2]

            for course in c1_list:
                if course_2 not in course.conflicts:
                    course.conflicts.append(course_2)

            for course in c2_list:
                if course_1 not in course.conflicts:
                    course.conflicts.append(course_1)

    except Exception as e:
        print(f"Error adding conflict: {e}")
        return

    # Save back to the config file
    with config.edit_mode() as editableConfig:
        editableConfig.config = scheduler_config

    if not safe_save(config, config_path):
        print("Conflict not saved.")
        return

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
def modifyConflict_JSON(selectedCourse: CourseConfig, targetConflictCourse: CourseConfig, targetNewCourse: CourseConfig, modifyMode: int, config: CombinedConfig):
    """
    modifyMode == 1: Replace the left side course in the pair (A-B -> C-B):
      - A is selectedCourse
      - B is targetConflictCourse (conflicting course we want to keep, but move to C)
      - C is targetNewCourse
      - remove B from A.conflicts
      - add B to C.conflicts (no duplicates)
      - in B.conflicts replace A with C

    modifyMode == 2: Replace the right side course in the pair (A-B -> A-C):
      - A is selectedCourse
      - B is targetConflictCourse (conflicting course we want to replace)
      - C is targetNewCourse    
      - in A.conflicts replace B with C
      - remove A from B.conflicts
      - add A to C.conflicts (no duplicates)
    """
    old_course_id = selectedCourse.course_id
    selectedConflict_id = targetConflictCourse.course_id
    newCourse_id = targetNewCourse.course_id

    # Defensive checks
    if modifyMode not in (1, 2):
        return False
    
    # Ensure selectedConflict exists in the selectedCourse
    if selectedConflict_id not in selectedCourse.conflicts:
        return False

    if modifyMode == 1:
        # A-B -> C-B
        # Remove B from A
        selectedCourse.conflicts = [c for c in selectedCourse.conflicts if c != selectedConflict_id]

        # Add B to C (targetNewCourse)
        if selectedConflict_id not in targetNewCourse.conflicts:
            targetNewCourse.conflicts.append(selectedConflict_id)

        # In B (targetConflictCourse), replace A with C
        updated = [newCourse_id if c == old_course_id else c for c in targetConflictCourse.conflicts]
        targetConflictCourse.conflicts = list(dict.fromkeys(updated))

    elif modifyMode == 2:
        # A-B -> A-C
        # In A (selectedCourse), replace B with C
        # Note: We must be careful if B appears multiple times (unlikely but possible in bad state)
        # We only want to replace ONE instance if we want to be truly instance specific, but since conflicts are strings,
        # we have to replace the string. 
        # However, selectedCourse now points to C instead of B.
        
        updated = [newCourse_id if c == selectedConflict_id else c for c in selectedCourse.conflicts]
        selectedCourse.conflicts = list(dict.fromkeys(updated))

        # Remove A from B (targetConflictCourse)
        targetConflictCourse.conflicts = [c for c in targetConflictCourse.conflicts if c != old_course_id]

        # Add A to C (targetNewCourse)
        if old_course_id not in targetNewCourse.conflicts:
            targetNewCourse.conflicts.append(old_course_id)

    return True

def select_course_instance(course_id: str, config: CombinedConfig, prompt_msg: str) -> CourseConfig:
    """Helper to select a specific course instance if duplicates exist."""
    candidates = [c for c in config.config.courses if c.course_id == course_id]
    
    if not candidates:
        return None
        
    if len(candidates) == 1:
        return candidates[0]
        
    print(f"\nMultiple sections found for {course_id}. Please select specific instance:")
    for i, c in enumerate(candidates, 1):
        # Try to show distinguishing info if available, otherwise just show index
        info = f"Credits: {c.credits}"
        if hasattr(c, 'faculty') and c.faculty:
             info += f", Faculty: {c.faculty}"
        print(f"{i}: {c.course_id} ({info})")
        
    while True:
        try:
            selection = int(input(f"{prompt_msg} [1-{len(candidates)}]: ").strip())
            if 1 <= selection <= len(candidates):
                return candidates[selection - 1]
        except ValueError:
            pass
        print("Invalid selection. Please try again.")

        
# Collect input for modifying conflicts.
def modifyconflict_input(config: CombinedConfig, config_path: str):
    #reloads config, so it is updated
    config = load_config_from_file(CombinedConfig, config_path)
    
    conflictNum = int(0)
    print("Existing Conflicts:")
    
    # Flatten conflicts for selection: (CourseObject, ConflictStringIndex, ConflictString)
    # We need to track the specific course object and which conflict in its list.
    all_conflicts = [] 
    
    for course in config.config.courses:
        for conflict in course.conflicts:
            conflictNum += 1
            all_conflicts.append((course, conflict))
            print(f"{conflictNum}: {course.course_id} conflicts with {conflict}")            

    if conflictNum == 0:
        print("There are no conflicts to modify.")
        return

    while(True):
        modifyNum_str = input("Which conflict would you like to modify? [1 - " + str(conflictNum) + "]: ").strip()
        if str.isnumeric(modifyNum_str) and 1 <= int(modifyNum_str) <= conflictNum:
            break

    # Get selected conflict info
    selection_idx = int(modifyNum_str) - 1
    selectedCourse, selectedConflict_str = all_conflicts[selection_idx]
    
    # Resolve the conflict string to a specific course object (targetConflictCourse)
    # Since selectedConflict_str is just a name, we might have multiple courses with that name.
    # We need to ask the user which one is the OTHER SIDE of this conflict.
    # However, for simply Modifying, we are replacing it.
    
    # But wait, modifyConflict_JSON needs the OBJECT of the conflict partner to update its back-reference.
    # So we MUST identify which specific course object corresponds to 'selectedConflict_str'.
    # Because the conflicts list only stores strings, we don't know WHICH of the duplicates it refers to.
    # We have to ask the user "Which 'CMSC 162' is this conflict with?" if duplicates exist.
    
    targetConflictCourse = select_course_instance(selectedConflict_str, config, f"Select the specific instance of {selectedConflict_str} involved in this conflict")
    if not targetConflictCourse:
         print(f"Error: Course {selectedConflict_str} not found in configuration.")
         return

    print("\nCourses in Conflict:")
    print(f"1: {selectedCourse.course_id}")
    print(f"2: {targetConflictCourse.course_id}")
    
    #Select which course is modified
    while(True):
        modifyNum = input("Which course would you like to modify? [1/2]: ").strip()
        if modifyNum == "1" or modifyNum == "2":
            break


    targetNewCourse = None
    newCourse_name = ""
    
    if modifyNum == "1":
        # Replacing selectedCourse (A) with NewCourse (C). A-B -> C-B
        newCourse_name = input(f"Replace course {selectedCourse.course_id} with (Enter Course ID): ").strip().upper()
    else:
        # Replacing targetConflictCourse (B) with NewCourse (C). A-B -> A-C
        newCourse_name = input(f"Replace course {targetConflictCourse.course_id} with (Enter Course ID): ").strip().upper()

    # Now we need the object for NewCourse
    targetNewCourse = select_course_instance(newCourse_name, config, f"Select the specific instance of {newCourse_name}")
    if not targetNewCourse:
        print(f"Course {newCourse_name} does not exist.")
        return

    #Modification confirmation
    while(True):
        confirm = input("Are you sure you want to modify this conflict? [y/n]: ").strip()
        if confirm == 'y' or confirm == 'n':
            break

    #Update json and check for errors with try/catch
    if confirm.lower() == 'y':
        modified = modifyConflict_JSON(selectedCourse=selectedCourse, 
                                       targetConflictCourse=targetConflictCourse, 
                                       targetNewCourse=targetNewCourse, 
                                       modifyMode=int(modifyNum), 
                                       config=config)
        if modified:
            # Save via runtime import to avoid circular import at module import time
            try:
                if not safe_save(config, config_path):
                    print("Conflict not saved.")
                    return
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

    # Build section counters so duplicate course IDs get .01, .02, etc.
    section_counter = {}
    course_section_labels = []  # parallel list to scheduler_config.courses
    for course in scheduler_config.courses:
        cid = course.course_id
        section_counter[cid] = section_counter.get(cid, 0) + 1
        course_section_labels.append(f"{cid}.{section_counter[cid]:02d}")

    # Build list of unique conflict pairs using section labels
    existing_conflicts = []
    for i, course in enumerate(scheduler_config.courses):
        for conflict_id in course.conflicts:
            # Find the first section label for the conflicting course ID
            conflict_label = next(
                (course_section_labels[j] for j, c in enumerate(scheduler_config.courses)
                 if c.course_id == conflict_id),
                conflict_id
            )
            pair = tuple(sorted([course_section_labels[i], conflict_label]))
            if pair not in existing_conflicts:
                existing_conflicts.append(pair)

    if not existing_conflicts:
        print("There are no conflicts currently in the configuration.")
        return

    valid_courses = {course.course_id for course in scheduler_config.courses}

    # Display with section labels
    print("\nExisting Conflicts:")
    for i, (a, b) in enumerate(existing_conflicts, 1):
        print(f"{i}. {a} <-> {b}")

    # Prompt for first course (still accepts plain ID like CMSC 340)
    while True:
        course_1 = input("\nEnter the first course ID (e.g. 'CMSC 340'): ").strip().upper()
        if course_1 == "":
            print("Course ID cannot be empty.")
        elif course_1 not in valid_courses:
            print(f"Error: '{course_1}' is not a valid course. Valid courses are: {', '.join(sorted(valid_courses))}")
        else:
            break

    # Prompt for second course
    while True:
        course_2 = input("Enter the conflicting course ID (e.g. 'CMSC 340'): ").strip().upper()
        if course_2 == "":
            print("Course ID cannot be empty.")
        elif course_2 not in valid_courses:
            print(f"Error: '{course_2}' is not a valid course. Valid courses are: {', '.join(sorted(valid_courses))}")
        elif course_2 == course_1:
            print("Error: A course cannot conflict with itself.")
        elif tuple(sorted([course_1, course_2])) not in [(a.rsplit('.', 1)[0], b.rsplit('.', 1)[0]) for a, b in existing_conflicts]:
            print(f"Error: No conflict exists between '{course_1}' and '{course_2}'.")
        else:
            break

    print("\nConflict Summary:")
    print(f"- {course_1} <-> {course_2}")

    while True:
        confirm = input("Delete this conflict? [y/n]: ").lower().strip()
        if confirm in ('y', 'n'):
            break

    if confirm == 'n':
        print("Conflict deletion canceled.")
        return

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

    if not safe_save(config, config_path):
        print("No changes were written to the file.")
        return
    print(f"\nConflict between '{course_1}' and '{course_2}' has been permanently deleted.")