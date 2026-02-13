from scheduler import *
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
