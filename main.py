# Filename: main.py
# Description: Builds a command line interface for users to run, modify, and display the scheduler
# Authors: Lauryn Gilbert, Hailey, Luke Leopold, Brooks, Keller

import sys
from faculty import *
from course import *
from conflict import *
from lab import *
from room import *
from scheduler import load_config_from_file
from scheduler.config import CombinedConfig
from ourScheduler import *

faculty_list = []

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_path>")
        return

    config_path = sys.argv[1]

    # Load the config file
    config = load_config_from_file(CombinedConfig, config_path)
    
    # Validate and fix any invalid faculty references on startup
    validate_and_fix_faculty_references(config_path)
    config = load_config_from_file(CombinedConfig, config_path)

    while True:
        print("\nScheduler Menu")
        print("1.  Add Faculty")
        print("2.  Modify Faculty")
        print("3.  Delete Faculty")
        print("4.  Add Course")
        print("5.  Modify Course")
        print("6.  Delete Course")
        print("7.  Add Conflict")
        print("8.  Modify Conflict")
        print("9.  Delete Conflict")
        print("10. Add Lab")
        print("11. Modify Lab")
        print("12. Delete Lab")
        print("13. Add Room")
        print("14. Modify Room")
        print("15. Delete Room")
        print("16. Print the Configuration File")
        print("17. Run the Scheduler")
        print("18. Display Schedules in CSV")
        print("19. Exit")
        
        choice = input("Choose an option (number only): ").strip()
        
        try:
            if choice == '1':
                faculty = addFaculty(config=config, config_path=config_path)
                if faculty is not None:
                    faculty_list.append(faculty)
                    print("New faculty information saved.")
            elif choice == '2':
                modifyFaculty(config, config_path)
            elif choice == '3':
                deleteFaculty(config_path)
                validate_and_fix_faculty_references(config_path)
                config = load_config_from_file(CombinedConfig, config_path)
            elif choice == '4':
                available_rooms = config.config.rooms
                available_labs = config.config.labs
                available_faculty = [f.name for f in config.config.faculty]
                course = addCourse(available_rooms, available_labs, available_faculty)
                if course is not None:
                    config.config.courses.append(course)
                    print("Course added successfully.")

                    import json
                    with open(config_path, 'w') as f:
                        json.dump(config.model_dump(mode='json'), f, indent = 2)
                    print(f"Changes saved to {config_path}")
            elif choice == '5':
                modifyCourse(config_path)  
            elif choice == '6':
                deleteCourse(config, config_path)
            elif choice == '7':
                addConflict(config_path=config_path)
            elif choice == '8':
                modifyconflict_input(config=config, config_path=config_path)
            elif choice == '9':
                deleteConflict(config, config_path)
            elif choice == '10':
                new_lab = add_lab()
                if new_lab:
                    # Check if lab already exists
                    if new_lab in config.config.labs:
                        print(f"\nWarning: Lab '{new_lab}' already exists.")
                    else:
                        # Add lab name to labs list
                        config.config.labs.append(new_lab)

                        # Save to JSON
                        with open(config_path, "w", encoding="utf-8") as f:
                            json.dump(config.model_dump(mode="json"), f, indent=2)

                        print(f"\nLab '{new_lab}' added successfully.")
            elif choice == '11':
                labs = config.config.labs
                courses = config.config.courses
                faculty = config.config.faculty
                labs, courses, faculty = modifyLab(labs, courses, faculty)

                import json
                with open(config_path, 'w') as f:
                    json.dump(config.model_dump(mode='json'), f, indent=2)
                print(f"Changes saved to {config_path}")
            elif choice == "12":
                deleteLab_input(config=config, config_path=config_path)
            elif choice == '13':
                addRoom()
            elif choice == '14':
                modRoom()
            elif choice == '15':
              deleteRoom(config_path)
              config = load_config_from_file(CombinedConfig, config_path)

            elif choice == '16':
                try:
                    config = load_config_from_file(CombinedConfig, config_path)
                    s = Scheduler(config)
                    found = False
                    for schedule in s.get_models():
                        display_Schedule(schedule)
                        found = True
                        break
                    if not found:
                        print("No valid schedule could be generated.")
                except Exception as exc:
                    print(f"Failed to display schedule: {exc}")
            elif choice == '17':
                runScheduler(config)
            elif choice == '18':
                try:
                    num_input = input("How many schedules to display? (enter 0 for all): ").strip()
                    num = int(num_input)
                    if num < 0:
                        print("Please enter 0 or a positive integer.")
                    else:
                        max_schedules = 10**9 if num == 0 else num
                        display_Schedules_csv(config, max_schedules=max_schedules)
                except ValueError:
                    print("Invalid number. Please enter an integer.")
                except Exception as exc:
                    print(f"Failed to display CSV schedules: {exc}")
            elif choice == '19':
                print("Exiting scheduler.")
                break
            else:
                print("Invalid option. Please choose 10, 11, 15, or 19 for now.")
        
        except Exception as exc:
            print(f"Operation failed: {exc}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
