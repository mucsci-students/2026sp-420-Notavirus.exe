# main.py
import sys
from faculty import *
from course import *
from conflict import *

faculty_list = []

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_path>")
        return
    
    config_path = sys.argv[1]

    while True:
        print("\nScheduler Menu")
        print("1. Add Faculty")
        print("2. Add Conflict")
        print("3. Delete Conflict")
        print("4. List Courses")
        print("5. Delete Course")
        print("6. Modify Faculty")
        print("7. Exit")

        choice = input("Choose an option (number only): ").strip()

        try:
            if choice == '1':
                faculty = addFaculty()
                if faculty is not None:
                    faculty_list.append(faculty)
                    print("New faculty information saved.")
            elif choice == '2':
                addConflict()
            elif choice == '3':
                deleteConflict(config_path)
            elif choice == '4':
                listCourses(config_path)
            elif choice == '5':
                deleteCourse(config_path)
            elif choice == '6':
                modifyFaculty(config_path)
            elif choice == '7':
                print("Exiting scheduler.")
                break
            else:
                print("Invalid option. Please choose 1-7.")
        except Exception as exc:
            print(f"Operation failed: {exc}")

if __name__ == "__main__":
    main()