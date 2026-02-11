import scheduler
from scheduler import Day, TimeRange

#Global Variables
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 3
MIN_DAYS = 1
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1

#List of faculty
faculty_list = []




def main(): #Mainly part of display/run scheduler
# Main loop for faculty management menu
    while True:
        # Display menu options
        print("\nFaculty Scheduler Menu")
        print("1. Add Faculty")
        print("2. Delete Faculty")
        print("3. Exit")

        # Get user menu choice
        choice = input("Choose an option (number only): ").strip()

        try:
            if choice == '1':
                faculty = addFaculty()
                if faculty is not None:
                    faculty_list.append(faculty)
                    print("New faculty information saved.")

            elif choice == '2':
                deleteFaculty(faculty_list)

            elif choice == '3':
                print("Exiting faculty editor.")
                break

            else:
                # Handle invalid menu selections
                print("Invalid option. Please choose 1, 2, or 3.")

        except Exception as exc:
            # Catch and report unexpected errors
            print(f"Operation failed: {exc}")






# Add a new faculty to the scheduler.
# Preconditions: Preferred Courses Exist
# Postconditon: Returns FacultyConfig or Nothing
def addFaculty():
    while(True):
        name = input("Enter the new faculty's name: ")
        if name != "":
            break
    
    while(True):
        position = input("Does the new faculty have a full-time position? [y/n]: ")
        if position.lower() == 'y' or position.lower() == 'n':
            break

    #course limit is two or one depending on position
    if position.lower() == 'y':
        position = "Full-time"
        unique_course_limit = FULL_TIME_UNIQUE_COURSE_LIMIT
        max_credits = FULL_TIME_MAX_CREDITS
    else:
        position = "Adjunct"
        unique_course_limit = ADJUNCT_UNIQUE_COURSE_LIMIT
        max_credits = ADJUNCT_MAX_CREDITS

    # Add dates/Times to new faculty info
    while True:
        raw_dates = input("Enter available dates (MTWRF): ")
        dates = []
        for ch in raw_dates.upper():
            if ch in {"M", "T", "W", "R", "F"} and ch not in dates:
                dates.append(ch)
        if MIN_DAYS <= len(dates) <= MAX_DAYS:
            break
        print(f"Please enter between {MIN_DAYS} and {MAX_DAYS} valid days (MTWRF).")

    # match char dates to substitute for normal spelling, get availability for each day
    datesTimes = {}
    for day in dates:
        match day.upper():
            case 'M':
                day = "MON"
            case 'T':
                day = "TUE"
            case 'W':
                day = "WED"
            case 'R':
                day = "THU"
            case 'F':
                day = "FRI"
            case _: # any letters/characters not matched are skipped
                continue

        while(True): #Times should be in TimeRange format (i.e. using military time and assigning start/end times seperately)
            timerange = TimeRange(start='09:00', end='17:00')
            datesTimes[day] = [str(timerange)]
            if datesTimes[day] != "":
                break

    courses = input("Enter preferred courses, seperated with a semicolon (Ex. CMSC 161; CMSC 162): ")
    coursesPref = {}
    if courses != "":
        for course in str.split(courses, ";"):
            while True:
                try:
                    weight = int(input("Enter a weight for " + course.strip() + ". (0 - 10): "))
                except ValueError:
                    print("Please enter a whole number between 0 and 10.")
                    continue
                if 0 <= weight <= 10:
                    break
                print("Please enter a whole number between 0 and 10.")
            coursesPref[course.upper().strip()] = weight

    #output entered data
    print("\nNew Faculty Summary:")
    print("Name: " + name + "\nPosition Type: " + position + "\nAvailability: ")
    print(datesTimes)
    print("Preferred courses:")
    print(coursesPref)

    #Confirm entered data
    while(True):
        confirm = input("\nIs this information correct? [y/n]: ")
        if confirm.lower() == 'y' or confirm.lower() == 'n':
            break
    
    if confirm.lower() == 'y':
        return scheduler.FacultyConfig(name=name, maximum_credits=max_credits, minimum_credits=MIN_CREDITS, unique_course_limit=unique_course_limit, course_preferences=coursesPref, 
                                    maximum_days=5, times=datesTimes)
    else:
        while(True):
            confirm = input("\nWould you like to restart adding new faculty? [y/n]: ")
            if confirm.lower() == 'y' or confirm.lower() == 'n':
                break
        if confirm.lower() == 'y':
            return addFaculty()
        else:
            return None
        #Check if name and preferred courses are the same
    



# Delete an existing faculty member from the scheduler.
# Preconditions: Faculty list is initialized and may contain one or more faculty entries.
# Postconditions: Removes the faculty with the matching name (case-insensitive)
#                 from the faculty list if found; otherwise, no changes are made.
def deleteFaculty(faculty_list):
    # Check if there is any faculty to delete
    if not faculty_list:
        print("No faculty available to delete.")
        return
    
    # Display current faculty names
    print("\nCurrent Faculty:")
    for faculty in faculty_list:
        print(f"- {faculty.name}")

    # Prompt for faculty name
    while True:
        name = input("\nEnter the name of the faculty to delete: ").strip()
        if name:
            break

    # Search for matching faculty (case-insensitive)
    faculty_to_delete = None
    for faculty in faculty_list:
        if faculty.name.lower() == name.lower():
            faculty_to_delete = faculty
            break

    # Handle case where faculty is not found
    if faculty_to_delete is None:
        print(f"No faculty named '{name}' found.")
        return
    
    # Confirm deletion
    confirm = input(f"Are you sure you want to delete {faculty_to_delete.name}? [y/n]: ").lower()

    # Remove faculty if confirmed
    if confirm == 'y':
        faculty_list.remove(faculty_to_delete)
        print(f"{faculty_to_delete.name} has been deleted.")
    else:
        print ("Deletion canceled.")




if __name__ == "__main__":
    main()

