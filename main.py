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

s = scheduler()

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
 
def display_Schedule(scheduler):
    if scheduler is None:
        print("No schedule to display")
        return
    DAYS_ORDER = ["MON", "TUE", "WED", "THUR", "FRI"]

    try:
        assignments = scheduler.get_assignments()
    except AttributeError:
        print("Schedule could not be read.")
        return
    
    if not assignments:
        print("no assignments")

    # ------------------------------------------------------------------ #
    #  1. FULL TIMETABLE GRID  (rows = time slots, columns = days)        #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    print(" FULL TIMEABLE GRID")
    print("=" * 70)

    # Collect all unique time slots and sort them
    time_slots = sorted(set(a.time_range for a in assignments))

    # Build a lookup: (day, time_range) -> list of entries
    from collections import defaultdict
    grid = defaultdict(list)
    for a in assignments:
        for day in a.days:
            grid[(day, a.time_range)].append(f"{a.course_id} ({a.room})")

    #print header row
    col_w = 20
    print(f"{'Time':<12}" + "".join(f"{day:<{col_w}}" for day in DAYS_ORDER))
    print("-" * (12 + col_w * len(DAYS_ORDER)))

    for slot in time_slots:
        row = f"{slot < 12}"
        for day in DAYS_ORDER:
            entries = grid.get((day, slot), [])
            cell = ", ".join(entries) if entries else "-"
            row += f"{cell:<{col_w}}"
        print(row)

    # ------------------------------------------------------------------ #
    #  2. ROOM / TIME SLOT LAYOUT                                         #
    # ------------------------------------------------------------------ #

    print("\n" + "=" * 70)
    print(" ROOM / TIME SLOT LAYOUT")
    print("=" * 70)

    by_room = defaultdict(list)
    for a in assignments:
        by_room[a.room].append(a)

    for room in sorted(by_room):
        print(f"\n  Room: {room}")
        print(f"  {'Course':<15} {'Faculty':<20} {'Days':<15} {'Time'}")
        print("  " + "-" * 60)
        for a in sorted(by_room[room], key=lambda x: x.time_range):
            days_str = "/".join(a.days)
            print(f"  {a.course_id:<15} {a.faculty_name:<20} {days_str:<15} {a.time_range}")

    # ------------------------------------------------------------------ #
    #  3. FACULTY ASSIGNMENTS  (who teaches what)                         #
    # ------------------------------------------------------------------ #

    print("\n" + "=" * 70)
    print(" FACULTY ASSIGNMENTS")
    print("=" * 70)

    by_faculty = defaultdict(list)
    for a in assignments:
        by_faculty[a.faculty_name].append(a)

    for faculty_name in sorted(by_faculty):
        courses = by_faculty[faculty_name]
        total_credits = sum(a.credits for a in courses)
        print(f"\n  {faculty_name}  (Total Credits: {total_credits})")
        print(f"  {'Course':<15} {'Room':<10} {'Days':<15} {'Time':<20} {'Credits'}")
        print("  " + "-" * 65)
        for a in sorted(courses, key=lambda x: x.time_range):
            days_str = "/".join(a.days)
            print(f"  {a.course_id:<15} {a.room:<10} {days_str:<15} {a.time_range:<20} {a.credits}")

    print("\n" + "=" * 70)





def main(): #Mainly part of display/run scheduler
    try:
        faculty = addFaculty()
        if faculty is None:
            print("No faculty information saved.")
            return
        scheduler.SchedulerConfig(rooms=[], labs=[], courses=[], faculty=[faculty])
        print("New faculty information saved!")
        
    
    except Exception as exc:
        print(f"Failed to save faculty: {exc}")


if __name__ == "__main__":
    main()