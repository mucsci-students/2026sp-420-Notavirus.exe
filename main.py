import sys
import scheduler
from scheduler import Day, TimeRange
from scheduler import load_config_from_file
from scheduler.config import CombinedConfig

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
    if len(sys.argv) < 2:
        print("Usage: python main.py <config_path>")
        return
    
    config_path = sys.argv[1]
    
    while True:
        # Display menu options
        print("\nScheduler Menu")
        print("1. Add Faculty")
        print("2. Add Conflict")
        print("3. Delete Conflict")
        print("4. Delete Course")
        print("5. Modify Faculty")
        print("6. Exit")

        # Get user choice
        choice = input("Choose an option (number only): ").strip()

        try:
            if choice == '1':
                # Add new faculty
                faculty = addFaculty()
                if faculty is not None:
                    faculty_list.append(faculty)
                    print("New faculty information saved.")

            elif choice == '2':
                # Add conflict
                addConflict()

            elif choice == '3':
                # Delete conflict
                deleteConflict(config_path)

            elif choice == '4':
                # Delete course
                deleteCourse(config_path)
           
            elif choice == '5':
                # Delete course
                modifyFaculty(config_path)

            elif choice == '6':
                # Exit program
                print("Exiting scheduler.")
                break

            else:
                # Handle invalid menu input
                print("Invalid option. Please choose 1-5.")

        except Exception as exc:
            # Catch unexpected runtime errors
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
    



# Add a conflict between two courses
# Preconditions: User knows the course IDs involved.
# Postconditions: Conflict information is collected.
def addConflict():
    # Prompt for the first course
    while True:
        course_1 = input("Enter the first course ID: ").strip()
        if course_1 != "":
            break

    # Prompt for the conflicting course
    while True:
        course_2 = input("Enter the conflicting course ID: ").strip()
        if course_2 != "":
            break

    # Display summary of the conflict being added
    print("\nConflict Summary:")
    print(f"- {course_1} conflicts with {course_2}")

    # Confirm conflict addition
    while True:
        confirm = input("Add this conflict? [y/n]: ").lower().strip()
        if confirm in ('y', 'n'):
            break
    if confirm == 'y':
        # Note: Actual conflict storage will occur once courses exist
        print("Conflict recorded.")
    else:
        print("Conflict addition canceled.")


# Delete a conflict from the scheduler
def deleteConflict(config_path: str):
    # Load the config
    config = load_config_from_file(CombinedConfig, config_path)
    scheduler_config = config.config

    # Build list of existing conflicts
    existing_conflicts = []
    for course in scheduler_config.courses:
        for conflict in course.conflicts:
            pair = tuple(sorted([course.course_id, conflict]))
            if pair not in existing_conflicts:
                existing_conflicts.append(pair)

    # Check if there are any conflicts
    if not existing_conflicts:
        print("There are no conflicts currently in the configuration.")
        return

    # Display existing conflicts
    print("\nExisting Conflicts:")
    for i, (a, b) in enumerate(existing_conflicts, 1):
        print(f"{i}. {a} <-> {b}")

    # Prompt for the first course
    while True:
        course_1 = input("\nEnter the first course ID: ").strip().upper()
        if course_1 != "":
            break

    # Prompt for the second course
    while True:
        course_2 = input("Enter the conflicting course ID: ").strip().upper()
        if course_2 != "":
            break

    # Check if the conflict exists
    pair = tuple(sorted([course_1, course_2]))
    if pair not in existing_conflicts:
        print(f"\nError: No conflict exists between '{course_1}' and '{course_2}'. No changes were made.")
        return

    # Display summary
    print("\nConflict Summary:")
    print(f"- {course_1} <-> {course_2}")

    # Confirm deletion
    while True:
        confirm = input("Delete this conflict? [y/n]: ").lower().strip()
        if confirm in ('y', 'n'):
            break

    if confirm == 'n':
        print("Conflict deletion canceled.")
        return

    # Remove the conflict from both courses
    try:
        with scheduler_config.edit_mode() as editable:
            for course in editable.courses:
                if course.course_id == course_1 and course_2 in course.conflicts:
                    course.conflicts.remove(course_2)
                elif course.course_id == course_2 and course_1 in course.conflicts:
                    course.conflicts.remove(course_1)
    except Exception as e:
        print(f"\nError: Failed to remove conflict due to validation error: {e}")
        return

    # Save back to the config file
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))

    print(f"\nConflict between '{course_1}' and '{course_2}' has been permanently deleted.")    

# Delete a course from the scheduler
def deleteCourse(config_path):
    # Load the config 
    config = load_config_from_file(CombinedConfig, config_path)
    scheduler_config = config.config

    # Return if no courses are in config
    if not scheduler_config.courses:
        print("There are no courses in the configuration.")
        return

    # Print existing courses
    print("\nExisting Courses:")
    for i, course in enumerate(scheduler_config.courses, 1):
        print(f"{i}. {course.course_id} ({course.credits} credits)")

    # Prompt for the first course
    while True:
        course_id = input("\nEnter the full course ID: ").strip().upper()
        if course_id != "":
            break

    # Check if the course exists
    matching = [c for c in scheduler_config.courses if c.course_id == course_id]
    if not matching:
        print(f"\nError: No course '{course_id}' found. No changes were made.")
        return
    
    # Print summary
    print("\nCourse Summary:")
    for course in matching:
        print(f"- {course.course_id} ({course.credits} credits)")

    # Confirm deletion
    while True:
        confirm = input("Delete this course everywhere? [y/n]: ").lower().strip()
        if confirm in ('y', 'n'):
            break
    if confirm == 'n':
        print("Course deletion canceled.")
        return
    
    # Removes the course and references to it in conflicts that has the course in it
    try:
        with scheduler_config.edit_mode() as editable:
            editable.courses = [c for c in editable.courses if c.course_id != course_id]
            for course in editable.courses:
                if course_id in course.conflicts:
                    course.conflicts.remove(course_id)
    except Exception as e:
        print(f"\nError: Failed to delete course due to validation error: {e}")
        return
    
    # Save back to the config file
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))

    print(f"\nCourse '{course_id}' has been permanently deleted.")

# Allows user to modify existing faculty
def modifyFaculty(config_path):
    # Load the config 
    config = load_config_from_file(CombinedConfig, config_path)
    scheduler_config = config.config

    if not scheduler_config.faculty:
        print("There are no faculty currently existing in the configuration.")
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
        print(f"\nError: No faculty by '{faculty_name}' was found. No changes were made.")
        return

    # Display current information
    print("\nCurrent Faculty Information:")
    print(f"Name: {faculty.name}")
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
    print("1. Maximum Credits")
    print("2. Minimum Credits")
    print("3. Availability Times")
    print("4. Course Preferences")
    print("5. Room Preferences")
    print("6. Lab Preferences")
    print("7. Cancel")

    while True:
        choice = input("Choose an option (1-7): ").strip()
        if choice in ['1', '2', '3', '4', '5', '6', '7']:
            break
        print("Invalid option. Please choose 1-7.")


    if choice == '7':
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
                while True:
                    try:
                        new_max = int(input("Enter new maximum credits: "))
                        if new_max >= 0:
                            editable_faculty.maximum_credits = new_max
                            break
                        print("Please enter a non-negative number.")
                    except ValueError:
                        print("Please enter a valid number.")

            elif choice == '2':
                while True:
                    try:
                        new_min = int(input("Enter new minimum credits: "))
                        if new_min >= 0:
                            editable_faculty.minimum_credits = new_min
                            break
                        print("Please enter a non-negative number.")
                    except ValueError:
                        print("Please enter a valid number.")

            elif choice == '3':
                # Modify availability times
                while True:
                    raw_dates = input("Enter available days of the week (MTWRF e.g. MWRF): ")
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

            elif choice == '4':
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

            elif choice == '5':
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

            elif choice == '6':
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

if __name__ == "__main__":
    main()