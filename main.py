from scheduler import * 


"""
 Modifies an existing lab and updates all references.
 returns updated list. 
"""

def modifyLab(labs, courses, faculty):
    if not labs:
        print("No labs available")
        return labs, courses, faculty
    
    print("\n--- Modify Lab ---")
    print(f"Current labs: {','.join(labs)}")

    #Select lab to modify
    while True:
        old_name = input("Enter the name of the lab you would like to modify (or press Enter to cancel): ").strip()
        if old_name == "":
            print("Cancelled")
            return labs, courses, faculty
        if(old_name not in labs):
            print(f"Error: Lab '{old_name}' does not exist.")
            print(f"Available Labs: {','.join(labs)}")
            continue
        break

    #Select new name
    while True:
        new_name = input(f"Enter the new name of the lab '{old_name}': ").strip()
        if new_name == "":
            print("Lab name cannot be empty.")
            continue
        if new_name in labs:
            print(f"Error lab '{new_name}' already exists")
            continue
        break
    
    #Show updates

    affected_courses = [c for c in courses if old_name in c.lab]
    affected_faculty = [f for f in faculty if old_name in f.lab_preferences]

    print(f"\nThis will update")
    print(f"  -Lab name '{old_name}'  ->  '{new_name}'")

    if affected_courses:
        print(f"  -{len(affected_courses)} course(s): {','.join(c.course_id for c in affected_courses)}")
        print(f"  -{len(affected_faculty)} faculty: {','.join(f.name for f in affected_faculty)}")

    #Confirm changes

    while True:
        confirm = input(f"\nProceed with these changes [y/n]")
        if confirm.lower() in ('y', 'n'):
            break

        #Update name
    if confirm.lower() == 'y':
        index = labs.index(old_name)
        labs[index] = new_name

        for course in courses:
            if old_name in course.lab:
                course.lab = [new_name if lab == old_name else lab for lab in course.lab]

            #Update faculty preferences
        for f in faculty:
            if old_name in f.lab_preferences:
                f.lab_preferences[new_name] = f.lab_preferences.pop(old_name)

            print(f"Lab successfully updated to '{new_name}'")
        else:
            print(f"Cancelled, no changes made.")

        return labs, courses, faculty



def main():
    # Create some test data
    labs = ["LAB101", "LAB102"]
    
    courses = [
        CourseConfig(
            course_id="CMSC161",
            credits=3,
            room=["ROOM101"],
            lab=["LAB101"],  # references LAB101
            faculty=["Dr. Smith"],
            conflicts=[]
        ),
        CourseConfig(
            course_id="CMSC162",
            credits=3,
            room=["ROOM102"],
            lab=["LAB101"],  # also references LAB101
            faculty=["Dr. Jones"],
            conflicts=[]
        ),
        CourseConfig(
            course_id="CMSC200",
            credits=4,
            room=["ROOM103"],
            lab=[],  # no lab
            faculty=["Dr. Smith"],
            conflicts=[]
        )
    ]
    
    faculty = [
        FacultyConfig(
            name="Dr. Smith",
            maximum_credits=12,
            minimum_credits=3,
            unique_course_limit=2,
            maximum_days=5,
            times={
                "MON": [TimeRange(start="09:00", end="17:00")],
                "WED": [TimeRange(start="09:00", end="17:00")],
            },
            lab_preferences={"LAB101": 8}  # has preference for LAB101
        ),
        FacultyConfig(
            name="Dr. Jones",
            maximum_credits=12,
            minimum_credits=3,
            unique_course_limit=2,
            maximum_days=5,
            times={
                "TUE": [TimeRange(start="09:00", end="17:00")],
                "THU": [TimeRange(start="09:00", end="17:00")],
            },
            lab_preferences={}
        )
    ]
    
    # Show initial state
    print("=== Initial State ===")
    print(f"Labs: {labs}")
    print(f"\nCourses using LAB101:")
    for c in courses:
        if "LAB101" in c.lab:
            print(f"  - {c.course_id}")
    print(f"\nFaculty with LAB101 preference:")
    for f in faculty:
        if "LAB101" in f.lab_preferences:
            print(f"  - {f.name} (preference: {f.lab_preferences['LAB101']})")
    
    # Test modifyLab
    labs, courses, faculty = modifyLab(labs, courses, faculty)
    
    # Show final state
    print("\n=== Final State ===")
    print(f"Labs: {labs}")
    print(f"\nAll courses and their labs:")
    for c in courses:
        print(f"  - {c.course_id}: {c.lab if c.lab else 'No lab'}")
    print(f"\nAll faculty lab preferences:")
    for f in faculty:
        if f.lab_preferences:
            print(f"  - {f.name}: {f.lab_preferences}")


if __name__ == "__main__":
    main()
