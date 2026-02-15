# lab.py
# Functions to add/modify/delete a lab

from scheduler import load_config_from_file, TimeRange
from scheduler.config import CombinedConfig
import scheduler


def add_lab():
    # Lab name
    while True:
        name = input("Enter the lab name: ").strip()
        if name != "":
            break

    # Associated course
    while True:
        course = input("Enter the course this lab is associated with (e.g. CMSC 161): ").strip()
        if course != "":
            break

    # Lab instructor
    instructor = input("Enter the instructor name for this lab: ").strip()
    if instructor == "":
        instructor = None

    # Lab meeting days
    while True:
        raw_days = input("Enter the days this lab meets (MTWRF): ")
        days = []
        for ch in raw_days.upper():
            if ch in {"M", "T", "W", "R", "F"} and ch not in days:
                days.append(ch)

        if len(days) > 0:
            break

        print("Please enter at least one valid day (MTWRF).")

    # Convert to scheduler day format
    daysTimes = {}
    for day in days:
        match day:
            case 'M': day_name = "MON"
            case 'T': day_name = "TUE"
            case 'W': day_name = "WED"
            case 'R': day_name = "THU"
            case 'F': day_name = "FRI"
            case _: continue

        while True:
            start_time = input(f"Enter start time for {day_name} (HH:MM): ").strip()
            end_time = input(f"Enter end time for {day_name} (HH:MM): ").strip()
            try:
                timerange = TimeRange(start=start_time, end=end_time)
                daysTimes[day_name] = [timerange]
                break
            except Exception as e:
                print(f"Invalid time format: {e}")

    # Display summary
    print("\nNew Lab Summary:")
    print(f"Name: {name}")
    print(f"Course: {course.upper()}")
    print(f"Instructor: {instructor}")
    print(f"Times: {daysTimes}")

    # Confirm
    while True:
        confirm = input("\nIs this information correct? [y/n]: ").lower().strip()
        if confirm in ('y', 'n'):
            break

    if confirm == 'y':
        return scheduler.LabConfig(
            name=name,
            course=course.upper(),
            instructor=instructor,
            times=daysTimes
        )
    else:
        while True:
            restart = input("Would you like to restart adding the lab? [y/n]: ").lower().strip()
            if restart in ('y', 'n'):
                break

        if restart == 'y':
            return add_lab()
        else:
            return None


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
        old_name = input("Enter the name of the lab you would like to modify, must be entered how it is shown above. (or press Enter to cancel): ").strip()
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
    if affected_faculty:
        print(f"  -{len(affected_faculty)} faculty: {','.join(f.name for f in affected_faculty)}")

    #Confirm changes
    while True:
        confirm = input(f"\nProceed with these changes [y/n]: ")
        if confirm.lower() in ('y', 'n'):
            break

    # Update name
    if confirm.lower() == 'y':
        index = labs.index(old_name)
        labs[index] = new_name

        for course in courses:
            if old_name in course.lab:
                course.lab = [new_name if lab == old_name else lab for lab in course.lab]

        # Update faculty preferences
        for f in faculty:
            if old_name in f.lab_preferences:
                f.lab_preferences[new_name] = f.lab_preferences.pop(old_name)

        print(f"Lab successfully updated to '{new_name}'")
    else:
        print(f"Cancelled, no changes made.")

    return labs, courses, faculty