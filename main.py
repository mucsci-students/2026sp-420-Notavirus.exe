import scheduler
from scheduler import Day, TimeRange, load_config_from_file, CombinedConfig, Scheduler
import json

#Global Variables
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 0
MIN_DAYS = 1
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1
CONFIG_JSON = "example.json"

# Displays entered information for new faculty for validation
# Returns a FacultyConfig or Nothing
def addFaculty_confirm(new_faculty: scheduler.FacultyConfig):
    if new_faculty.unique_course_limit == FULL_TIME_UNIQUE_COURSE_LIMIT:
        position = "Full Time"
    else:
        position = "Adjunct"

#output entered data
    print("\nNew Faculty Summary:")
    print("Name: " + new_faculty.name + "\nPosition Type: " + position + "\nAvailability: ")
    print(new_faculty.times)
    print("Preferred courses:")
    print(new_faculty.course_preferences)

    #Confirm entered data
    while(True):
        confirm = input("\nIs this information correct? [y/n]: ")
        if confirm.lower() == 'y' or confirm.lower() == 'n':
            break
    
    if confirm.lower() == 'y':
        return True
    else:
        """ while(True):
            confirm = input("\nWould you like to restart adding new faculty? [y/n]: ")
            if confirm.lower() == 'y' or confirm.lower() == 'n':
                break
        if confirm.lower() == 'y':
            return addFaculty_input()
        else: """
        return False

# Set up FacultyConfig to add a new faculty to the JSON file
# Returns a FacultyConfig.
def addFaculty_config(name: str, isFullTime: str, dates: list, courses: dict):
    #name
    #course limit is two or one depending on position
    if isFullTime.lower() == 'y':
        unique_course_limit = FULL_TIME_UNIQUE_COURSE_LIMIT
        max_credits = FULL_TIME_MAX_CREDITS
    else:
        unique_course_limit = ADJUNCT_UNIQUE_COURSE_LIMIT
        max_credits = ADJUNCT_MAX_CREDITS

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

        while(True):
            timerange = TimeRange(start='09:00', end='17:00')
            datesTimes[day] = [str(timerange)]
            if datesTimes[day] != "":
                break

    return scheduler.FacultyConfig(name=name, maximum_credits=max_credits, minimum_credits=MIN_CREDITS, unique_course_limit=unique_course_limit, course_preferences=courses, 
                                    maximum_days=MAX_DAYS, times=datesTimes)

# Get input for adding new faculty
# Returns a FacultyConfig
def addFaculty_input():
    while(True):
        name = input("Enter the new faculty's name: ").strip()
        if name != "":
            break
    
    while(True):
        isFullTime = input("Does the new faculty have a full-time position? [y/n]: ")
        if isFullTime.lower() == 'y' or isFullTime.lower() == 'n':
            break

    # Add dates/Times to new faculty info
    while True:
        raw_dates = input("Enter available dates (MTWRF): ")
        dates = []
        for char in raw_dates.upper():
            if char in {"M", "T", "W", "R", "F"} and char not in dates:
                dates.append(char)
        if MIN_DAYS <= len(dates) <= MAX_DAYS:
            break
        print(f"Please enter between {MIN_DAYS} and {MAX_DAYS} valid days (MTWRF).")
  
    #Get preferred courses and weights
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

    return addFaculty_config(name=name, isFullTime=isFullTime, dates=dates, courses=coursesPref)

# Check to see if adding new faculty will add duplicate information
# Returns True if duplicate info would be added, otherwise returns false.
def faculty_check_duplicate(config: CombinedConfig, new_faculty: scheduler.FacultyConfig):
    for current_faculty in config.config.faculty:
        if current_faculty.name == new_faculty.name or (current_faculty.course_preferences == new_faculty.course_preferences and current_faculty.times == new_faculty.times): # TODO Decide on how strict to be with checking for duplicates
            return True
    return False

# Append new faculty to the CombinedConfig
def addFaculty_JSON(config: CombinedConfig, faculty: scheduler.FacultyConfig):
    # Update config with new faculty
    with config.edit_mode() as edit_config:
        edit_config.config.faculty.append(faculty)
        
    # Save updated config to JSON
    save_config_json(config, CONFIG_JSON)
    print("New faculty information saved!")

# Wrapper function to contain addFaculty method calls
def addFaculty(config: CombinedConfig):
    try:
        faculty = addFaculty_input()
        if faculty is None or not addFaculty_confirm(faculty):
            print("No faculty information saved.")
            return #should be replaced with continue later for running the CLI
        
        if faculty_check_duplicate(config, faculty):
            print("This faculty already exists! Maybe you meant to modify their information?")
            print("New faculty not added.")
            return #should be replaced with continue later for running the CLI

        addFaculty_JSON(config=config, faculty=faculty)
    
    except Exception as exc:
        print(f"Failed to save faculty: {exc}")

# Save data to a config.json file
def save_config_json(config: CombinedConfig, filename: str) -> None:
    with open(filename, 'w') as file:
        file.write(config.model_dump_json(indent=2))

# Load the config file and create a scheduler object.
# Returns a tuple with a CombinedConfig and scheduler object variables.
def initConfig():
    # Load configuration from JSON file
    config = load_config_from_file(CombinedConfig, CONFIG_JSON)
    # Create scheduler obj
    scheduler_obj = Scheduler(config)
    return (config, scheduler_obj)

def main(): #Mainly part of display/run scheduler
    (config, scheduler) = initConfig()
    addFaculty(config)


if __name__ == "__main__":
    main()

