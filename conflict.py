from scheduler import *
def modifyConflict_getCourses(modifyNum: int, config: CombinedConfig):
    # Find the course index and conflict index for the selected conflict (USED AI)
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

def modifyConflict_JSON(selectedCourse: CourseConfig, selectedConflict: str, newCourse: str, modifyMode: int, config: CombinedConfig):
    """Modify only the conflict links (do NOT change course_id values).

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

    # ensure selectedConflict exists in the selectedCourse (if not, nothing to do)
    if selectedConflict not in selectedCourse.conflicts:
        return False

    if modifyMode == 1:
        # A-B -> C-B (replace left side)
        # remove B from A.conflicts
        selectedCourse.conflicts = [c for c in selectedCourse.conflicts if c != selectedConflict]

        # add B to C.conflicts
        for course in config.config.courses:
            if course.course_id == newCourse:
                if selectedConflict not in course.conflicts:
                    course.conflicts.append(selectedConflict)
                break

        # in B.conflicts replace A with C
        for course in config.config.courses:
            if course.course_id == selectedConflict:
                course.conflicts = [newCourse if c == old_course_id else c for c in course.conflicts]
                break

    else:
        # A-B -> A-C (replace right side)
        # in A.conflicts replace B with C
        selectedCourse.conflicts = [newCourse if c == selectedConflict else c for c in selectedCourse.conflicts]

        # remove reciprocal link from B.conflicts
        for course in config.config.courses:
            if course.course_id == selectedConflict:
                course.conflicts = [c for c in course.conflicts if c != old_course_id]
                break

        # add reciprocal link on C.conflicts
        for course in config.config.courses:
            if course.course_id == newCourse:
                if old_course_id not in course.conflicts:
                    course.conflicts.append(old_course_id)
                break

    return True
        
                

def modifyconflict_input(config: CombinedConfig):
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

    # Get the selected conflict
    (selectedCourse, selectedConflict) = modifyConflict_getCourses(modifyNum=int(modifyNum), config=config)
    
    print("\nCourses in Conflict:")
    print(f"1: {selectedCourse.course_id}")
    print(f"2: {selectedConflict}")
    
    while(True):
        modifyNum = input("Which course would you like to modify? [1/2]: ").strip()
        if modifyNum == "1" or modifyNum == "2":
            break


    modifyCourse = ""
    if modifyNum == "1":
        modifyCourse = input(f"Replace course {selectedCourse.course_id} with: ").strip()
    else:
        modifyCourse = input(f"Replace course {selectedConflict} with: ").strip()

    while(True):
        confirm = input("Are you sure you want to modify this conflict? [y/n]: ").strip()
        if confirm == 'y' or confirm == 'n':
            break

    if confirm.lower() == 'y':
        modified = modifyConflict_JSON(selectedCourse=selectedCourse, selectedConflict=selectedConflict, newCourse=modifyCourse, modifyMode=int(modifyNum), config=config)
        if modified:
            # Save via runtime import to avoid circular import at module import time
            try:
                import main as main_mod
                try:
                    main_mod.save_config_json(config=config, filename=main_mod.CONFIG_JSON)
                    print("Config saved.")
                except Exception:
                    # fallback
                    main_mod.save_config_json(config=config, filename="example.json")
                    print("Config saved to example.json.")
            except Exception:
                print("Modification applied, but failed to save config automatically.")
        else:
            print("No changes applied (validation failed or conflict not present).")
    else:
        print("Conflict Modification Cancelled.")
