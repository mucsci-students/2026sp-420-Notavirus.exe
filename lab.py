# lab.py
# Authors: Lauryn Gilbert, Hailey, Luke Leopold, Brooks, ...
# Description: Functions relate to add/modify/delete lab.
from scheduler import CombinedConfig, TimeRange
import scheduler
from safe_save import safe_save


def add_lab(existing_labs=None):
    # Show current labs
    if existing_labs:
        print(f"Current labs: {', '.join(existing_labs)}")
    else:
        print("No labs currently exist.")

    # Lab name
    while True:
        name = input("Enter the lab name: ").strip()
        if name != "":
            break

    while True:
        confirm = input("Is this information correct? [y/n]: ").lower()
        if confirm in ("y", "n"):
            break

    if confirm == 'y':
        return name
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

# Delete a lab from the config file.
# Returns True if the lab was deleted, false otherwise.
def deleteLab_json(lab: str, config: CombinedConfig, config_path: str):
    try:
        with config.config.edit_mode() as editable:
            for course in editable.courses:
                 if lab in course.lab:
                    course.lab.remove(lab)
            for faculty in editable.faculty:
                if lab in faculty.lab_preferences:
                    del faculty.lab_preferences[lab]
            
            editable.labs.remove(lab)
                    
    except Exception as e:
        print(f"\nError: Failed to delete lab due to validation error: {e}")
        return False
    
    # Save back to the config file
    if not safe_save(config, config_path):
        print("Lab not saved.")
        return False

    return True

# Get input and confirmation to delete a lab.
# If there are no labs, print an error message.
def deleteLab_input(config: CombinedConfig, config_path: str):
    num = int(1)

    if len(config.config.labs) == 0:
        print("No labs exist. Cannot delete a lab.")
        return

    print("Which lab would you like to delete?")
    for lab in config.config.labs:
        print(str(num) + ": " + lab)
        num += 1
    
    while (True):
        labnum = input("\nEnter the number of the lab you would like to delete (-1 to quit): ")
        if str.isnumeric(labnum) and int(labnum) >= 1 and int(labnum) <= num:
            break
        elif int(labnum) == -1:
            print("Quitting deleting a lab.")
            return
    
    while(True):
        confirm = input("Are you sure you want to delete " + config.config.labs[int(labnum) - 1] + "? [y/n]: ").strip()
        if confirm == 'y':
            if deleteLab_json(config.config.labs[int(labnum) - 1], config=config, config_path=config_path):
                print("Lab deleted.")
            return
        if confirm == 'n':
            print("Quitting deleting a lab.")
            return