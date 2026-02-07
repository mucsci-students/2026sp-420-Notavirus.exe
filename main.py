import scheduler

#Global Variables
MAX_CREDITS = 12
MIN_CREDITS = 3
MIN_DAYS = 1
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COUSE_LIMIT = 1

# Add a new faculty to the scheduler.
def addFaculty():
    while(True):
        name = input("Enter the new faculty's name: ")
        if name != "":
            break
    
    while(True):
        position = input("Does the new faculty have a full-time position? [y/n]: ")
        if position.lower() == "y" or position.lower() == 'n':
            break

    #course limit is two or one depending on position
    if position.lower == 'y':
        position = "Full-time"
        unique_course_limit = FULL_TIME_UNIQUE_COURSE_LIMIT
    else:
        position = "Adjunct"
        unique_course_limit = ADJUNCT_UNIQUE_COUSE_LIMIT

    # Add dates/Times to new faculty info
    while(True):
        dates = input("Enter available dates (MTWRF): ")
        if len(dates) >= MIN_DAYS and len(dates) <= MAX_DAYS:
            break

    # match char dates to substitute for normal spelling, get availability for each day
    for day in dates:
        match day:
            case 'M':
                day = "Monday"
            case 'T':
                day = "Tuesday"
            case 'W':
                day = "Wednesday"
            case 'R':
                day = "Thursday"
            case 'F':
                day = "Friday"
            case _: # any letters not matched are skipped
                continue
        
        while(True):
            datesTimes = { day : input("Enter available time(s) for " + day + ": ")}
            if datesTimes[day] != "":
                break

    #Get preferred courses and their weights
    courses = input("Enter preferred courses, seperated with a semicolon (Ex. CMSC 161; CMSC 162): ")
    for course in str.split(courses, "; "):
        coursesPref = {course : input("Enter a weight for " + course + ". (Higher integer = Higher preference): ")}

    print("Name: " + name + "\nPosition Type:" + position + "\nAvailability: ")
    print(datesTimes)
    print("Preferred courses:")
    print(coursesPref)
    return scheduler.FacultyConfig(name=name, maximum_credits=MAX_DAYS, minimum_credits=MIN_CREDITS, unique_course_limit=unique_course_limit, mandatory_days=1, maximum_days=5)
    

def main():
    print("Hello from 2026sp-420-notavirus-exe!") #debug
    scheduler.SchedulerConfig(faculty=addFaculty) 

if __name__ == "__main__":
    main()

