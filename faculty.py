# faculty.py
# Functions to modify/delete/add a faculty member

from scheduler import load_config_from_file, Day, TimeRange
from scheduler.config import CombinedConfig
import scheduler

# Global Variables
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 3
MIN_DAYS = 1
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1



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


def modifyFaculty(config, config_path: str):
    # Load the config
    scheduler_config = config.config

    # Check if there are any faculty
    if not scheduler_config.faculty:
        print("There are no faculty in the configuration.")
        return

    # Display existing faculty
    print("\nExisting Faculty:")
    for i, faculty in enumerate(scheduler_config.faculty, 1):
        print(f"{i}. {faculty.name}")

    # Prompt for faculty to modify
    while True:
        faculty_name = input("\nEnter the faculty name to modify: ").strip()
        if faculty_name != "":
            break

    # Find the faculty
    faculty = None
    for f in scheduler_config.faculty:
        if f.name == faculty_name:
            faculty = f
            break

    if faculty is None:
        print(f"\nError: No faculty '{faculty_name}' found. No changes were made.")
        return

    # Determine position type
    if faculty.maximum_credits == FULL_TIME_MAX_CREDITS:
        position = "Full-time"
    else:
        position = "Adjunct"

    # Display current information
    print("\nCurrent Faculty Information:")
    print(f"Name: {faculty.name}")
    print(f"Position: {position}")
    print(f"Maximum Credits: {faculty.maximum_credits}")
    print(f"Minimum Credits: {faculty.minimum_credits}")
    print(f"Unique Course Limit: {faculty.unique_course_limit}")
    print(f"Maximum Days: {faculty.maximum_days}")
    print(f"Times: {faculty.times}")
    print(f"Course Preferences: {faculty.course_preferences}")
    print(f"Room Preferences: {faculty.room_preferences}")
    print(f"Lab Preferences: {faculty.lab_preferences}")

    # Menu for what to modify
    print("\nWhat would you like to modify?")
    print("1. Position (Full-time/Adjunct)")
    print("2. Maximum Credits")
    print("3. Minimum Credits")
    print("4. Unique Course Limit")
    print("5. Maximum Days")
    print("6. Availability Times")
    print("7. Course Preferences")
    print("8. Room Preferences")
    print("9. Lab Preferences")
    print("10. Cancel")

    while True:
        choice = input("Choose an option (1-10): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']:
            break
        print("Invalid option. Please choose 1-10.")

    if choice == '10':
        print("Modification canceled.")
        return

    # Make modifications based on choice
    try:
        with scheduler_config.edit_mode() as editable:
            # Find the faculty in the editable config
            editable_faculty = None
            for f in editable.faculty:
                if f.name == faculty_name:
                    editable_faculty = f
                    break

            if choice == '1':
                # Modify position type
                while True:
                    print("\nYour input will update the min/max credits, position, and unique course limit accordingly")
                    position = input("Is this faculty full-time? [y/n]: ").lower().strip()
                    if position in ('y', 'n'):
                        break
                    print("Please enter 'y' or 'n'.")
                
                if position == 'y':
                    editable_faculty.maximum_credits = FULL_TIME_MAX_CREDITS
                    editable_faculty.unique_course_limit = FULL_TIME_UNIQUE_COURSE_LIMIT
                    if editable_faculty.minimum_credits > FULL_TIME_MAX_CREDITS:
                        editable_faculty.minimum_credits = FULL_TIME_MAX_CREDITS
                    new_position = "Full-time"
                else:
                    if editable_faculty.minimum_credits > ADJUNCT_MAX_CREDITS:
                        editable_faculty.minimum_credits = ADJUNCT_MAX_CREDITS                    
                    editable_faculty.maximum_credits = ADJUNCT_MAX_CREDITS
                    editable_faculty.unique_course_limit = ADJUNCT_UNIQUE_COURSE_LIMIT

                    new_position = "Adjunct"
                
                print(f"Position changed to: {new_position}")
                print(f"Maximum credits set to: {editable_faculty.maximum_credits}")
                print(f"Minimum credits adjusted to: {editable_faculty.minimum_credits}")
                print(f"Unique course limit set to: {editable_faculty.unique_course_limit}")

            elif choice == '2':
                while True:
                    try:
                        new_max = int(input("Enter new maximum credits: "))
                        if new_max >= editable_faculty.minimum_credits:
                            editable_faculty.maximum_credits = new_max
                            break
                        print(f"Maximum credits must be >= minimum credits ({editable_faculty.minimum_credits}).")
                    except ValueError:
                        print("Please enter a valid number.")

            elif choice == '3':
                while True:
                    try:
                        new_min = int(input("Enter new minimum credits: "))
                        if 0 <= new_min <= editable_faculty.maximum_credits:
                            editable_faculty.minimum_credits = new_min
                            break
                        print(f"Minimum credits must be between 0 and maximum credits ({editable_faculty.maximum_credits}).")
                    except ValueError:
                        print("Please enter a valid number.")

            elif choice == '4':
                while True:
                    try:
                        new_limit = int(input("Enter new unique course limit: "))
                        if new_limit > 0:
                            editable_faculty.unique_course_limit = new_limit
                            break
                        print("Unique course limit must be at least 1.")
                    except ValueError:
                        print("Please enter a valid number.")

            elif choice == '5':
                while True:
                    try:
                        new_max_days = int(input("Enter new maximum days (0-5): "))
                        if 0 <= new_max_days <= 5:
                            editable_faculty.maximum_days = new_max_days
                            break
                        print("Maximum days must be between 0 and 5.")
                    except ValueError:
                        print("Please enter a valid number.")

            elif choice == '6':
                # Modify availability times
                while True:
                    raw_dates = input("Enter available dates with no spaces (MTWRF e.g. MWRF): ")
                    dates = []
                    for ch in raw_dates.upper():
                        if ch in {"M", "T", "W", "R", "F"} and ch not in dates:
                            dates.append(ch)
                    if MIN_DAYS <= len(dates) <= MAX_DAYS:
                        break
                    print(f"Please enter between {MIN_DAYS} and {MAX_DAYS} valid days (MTWRF).")

                datesTimes = {}
                for day in dates:
                    match day.upper():
                        case 'M':
                            day_name = "MON"
                        case 'T':
                            day_name = "TUE"
                        case 'W':
                            day_name = "WED"
                        case 'R':
                            day_name = "THU"
                        case 'F':
                            day_name = "FRI"
                        case _:
                            continue

                    while True:
                        start_time = input(f"Enter start time for {day_name} (HH:MM): ").strip()
                        end_time = input(f"Enter end time for {day_name} (HH:MM): ").strip()
                        try:
                            timerange = TimeRange(start=start_time, end=end_time)
                            datesTimes[day_name] = [timerange]
                            break
                        except Exception as e:
                            print(f"Invalid time format: {e}")

                editable_faculty.times = datesTimes

            elif choice == '7':
                # Modify course preferences
                courses = input("Enter preferred courses, separated with a semicolon (Ex. CMSC 161; CMSC 162): ")
                coursesPref = {}
                if courses != "":
                    for course in courses.split(";"):
                        while True:
                            try:
                                weight = int(input("Enter a weight for " + course.strip() + " (0-10): "))
                                if 0 <= weight <= 10:
                                    coursesPref[course.upper().strip()] = weight
                                    break
                                print("Please enter a whole number between 0 and 10.")
                            except ValueError:
                                print("Please enter a whole number between 0 and 10.")
                editable_faculty.course_preferences = coursesPref

            elif choice == '8':
                # Modify room preferences
                rooms = input("Enter preferred rooms, separated with a semicolon (Ex. Roddy 136; Roddy 140): ")
                roomsPref = {}
                if rooms != "":
                    for room in rooms.split(";"):
                        while True:
                            try:
                                weight = int(input("Enter a weight for " + room.strip() + " (0-10): "))
                                if 0 <= weight <= 10:
                                    roomsPref[room.strip()] = weight
                                    break
                                print("Please enter a whole number between 0 and 10.")
                            except ValueError:
                                print("Please enter a whole number between 0 and 10.")
                editable_faculty.room_preferences = roomsPref

            elif choice == '9':
                # Modify lab preferences
                labs = input("Enter preferred labs, separated with a semicolon (Ex. Linux; Mac): ")
                labsPref = {}
                if labs != "":
                    for lab in labs.split(";"):
                        while True:
                            try:
                                weight = int(input("Enter a weight for " + lab.strip() + " (0-10): "))
                                if 0 <= weight <= 10:
                                    labsPref[lab.strip()] = weight
                                    break
                                print("Please enter a whole number between 0 and 10.")
                            except ValueError:
                                print("Please enter a whole number between 0 and 10.")
                editable_faculty.lab_preferences = labsPref

    except Exception as e:
        print(f"\nError: Failed to modify faculty due to validation error: {e}")
        return

    # Save back to the config file
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))

    print(f"\nFaculty '{faculty_name}' has been successfully modified.")

    return config


# Delete an existing faculty member from the scheduler.
# Preconditions: Faculty list is initialized and may contain one or more faculty entries.
# Postconditions: Removes the faculty with the matching name (case-insensitive)
#                 from the faculty list if found; otherwise, no changes are made.
def deleteFaculty(config_path: str):
    config = load_config_from_file(CombinedConfig, config_path)
    scheduler_config = config.config

    # Check if there is any faculty to delete
    if not scheduler_config.faculty:
        print("No faculty available to delete.")
        return

    # Display current faculty
    print("\nCurrent Faculty:")
    for faculty in scheduler_config.faculty:
        print(f"- {faculty.name}")

    while True:
        name = input("\nEnter the name of the faculty to delete: ").strip()
        if name:
            break

    # Search for matching faculty (case-insensitive)
    matching = [f for f in scheduler_config.faculty if f.name.lower() == name.lower()]
    if not matching:
        print(f"No faculty named '{name}' found.")
        return

    faculty_to_delete = matching[0]

    confirm = input(f"Delete {faculty_to_delete.name}? [y/n]: ").lower()
    if confirm != 'y':
        print("Deletion canceled.")
        return

    try:
        with scheduler_config.edit_mode() as editable:
            editable.faculty = [
                f for f in editable.faculty
                if f.name.lower() != name.lower()
            ]

            # Remove faculty references from courses
            for course in editable.courses:
                while faculty_to_delete.name in course.faculty:
                    course.faculty.remove(faculty_to_delete.name)

    except Exception as e:
        print(f"Error deleting faculty: {e}")
        return

    # Save back to the config file
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))

    print(f"{faculty_to_delete.name} deleted successfully.")

# For Testing File:

def deleteFaculty_config(faculty_list, name):
    # Removes a faculty member by name (case-insensitive).
    # Returns True if removed, False if not found.
    for faculty in faculty_list:
        if faculty.name.lower() == name.lower():
            faculty_list.remove(faculty)
            return True
    return False

