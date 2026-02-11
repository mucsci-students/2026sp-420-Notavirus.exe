import scheduler
from scheduler import load_config_from_file, CombinedConfig

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
    try:
        # Load config from JSON file
        config_file = "example.json"
        config = scheduler.load_config_from_file(
            scheduler.CombinedConfig,
            config_file
        )

        # Extract the data we need
        labs = config.config.labs
        courses = config.config.courses
        faculty = config.config.faculty

        # Show initial state
        print("=== Initial State ===")
        print(f"Labs: {labs}")
        print(f"\nCourses and their labs:")
        for c in courses:
            print(f"  - {c.course_id}: {c.lab if c.lab else 'No lab'}")
        print(f"\nFaculty lab preferences:")
        for f in faculty:
            if f.lab_preferences:
                print(f"  - {f.name}: {f.lab_preferences}")

        # Call modifyLab
        labs, courses, faculty = modifyLab(labs, courses, faculty)

        # Show final state
        print("\n=== Final State ===")
        print(f"Labs: {labs}")
        print(f"\nCourses and their labs:")
        for c in courses:
            print(f"  - {c.course_id}: {c.lab if c.lab else 'No lab'}")
        print(f"\nFaculty lab preferences:")
        for f in faculty:
            if f.lab_preferences:
                print(f"  - {f.name}: {f.lab_preferences}")

        # OPTIONAL: Save changes back to JSON
        save_choice = input("\nSave changes to config file? [y/n]: ")
        if save_choice.lower() == 'y':
            # Update the config object with modified data
            config.config.labs = labs
            config.config.courses = courses
            config.config.faculty = faculty
            
            # Save to file
            import json
            with open(config_file, 'w') as f:
                json.dump(config.model_dump(mode='json'), f, indent=2)
            print(f"Changes saved to {config_file}")
        else:
            print("Changes not saved.")

    except FileNotFoundError:
        print(f"Error: {config_file} not found.")
    except Exception as exc:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
