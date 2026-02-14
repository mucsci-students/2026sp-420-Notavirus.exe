# Filename: main.py
# Description: Builds a command line interface for users to run, modify, and display the scheduler
# Authors: Lauryn Gilbert, Hailey, Luke Leopold, Brooks, Keller

import sys
from faculty import *
from course import *
from conflict import *
from lab import *
from scheduler import load_config_from_file
from scheduler.config import CombinedConfig

faculty_list = []

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_path>")
        return

    config_path = sys.argv[1]

    # load the config file
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
                faculty = addFaculty()
                if faculty is not None:
                    faculty_list.append(faculty)
                    print("New faculty information saved.")
            elif choice == '2':
                modifyFaculty(config, config_path)
            elif choice == '3':
                deleteFaculty(config_path)
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
                addConflict()
            elif choice == '8':
                modifyconflict_input(config=config, config_path=config_path)
            elif choice == '9':
                deleteConflict(config, config_path)
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
            elif choice == '19':
                print("Exiting scheduler.")
                break
            else:
                print("Invalid option. Please choose 1-19.")
        except Exception as exc:
            print(f"Operation failed: {exc}")

if __name__ == "__main__":
    main()
