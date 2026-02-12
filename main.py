# main.py
import sys
from course import *

faculty_list = []

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_path>")
        return
    
    config_path = sys.argv[1]

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
            if choice == '5':
                modifyCourse(config_path)
            elif choice == '6':
                deleteCourse(config_path)
            elif choice == '19':
                print("Exiting scheduler.")
                break
            else:
                print("Invalid option. Please choose 1-19.")
        except Exception as exc:
            print(f"Operation failed: {exc}")

if __name__ == "__main__":
    main()