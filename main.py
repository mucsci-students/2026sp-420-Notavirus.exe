import scheduler
from scheduler import Day, TimeRange
from scheduler.config import ClassPattern, Meeting, TimeBlock

#Global Variables
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 3
MIN_DAYS = 1
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1


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
            datesTimes[day] = [timerange]
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
 
def display_Schedule(schedule: list):
    if not schedule:
        print("No schedule to display.")
        return

    from collections import defaultdict

    DAYS_ORDER = ["MON", "TUE", "WED", "THU", "FRI"]

    # ------------------------------------------------------------------ #
    #  1. FULL TIMETABLE GRID  (rows = time slots, columns = days)        #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    print(" FULL TIMETABLE GRID")
    print("=" * 70)

    # Build a lookup: (day_name, time_slot) -> list of "COURSE_ID (ROOM)" strings
    grid = defaultdict(list)
    time_slot_labels = set()

    for ci in schedule:
        slot_label = str(ci.time).split(",")[0].split(" ", 1)[1]  # grabs "09:00-11:30" from "MON 09:00-11:30,WED 09:00-11:30"
        time_slot_labels.add(slot_label)
        for time_instance in ci.time.times:
            day_name = time_instance.day.name  # Day enum -> "MON", "TUE", etc.
            room_str = ci.room if ci.room else "No Room"
            grid[(day_name, slot_label)].append(f"{ci.course.course_id} ({room_str})")

    time_slots_sorted = sorted(time_slot_labels)

    col_w = 20
    print(f"{'Time':<12}" + "".join(f"{day:<{col_w}}" for day in DAYS_ORDER))
    print("-" * (12 + col_w * len(DAYS_ORDER)))

    for slot_label in time_slots_sorted:
        row = f"{slot_label:<12}"
        for day in DAYS_ORDER:
            entries = grid.get((day, slot_label), [])
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
    for ci in schedule:
        room_key = ci.room if ci.room else "No Room"
        by_room[room_key].append(ci)

    for room in sorted(by_room):
        print(f"\n  Room: {room}")
        print(f"  {'Course':<15} {'Section':<10} {'Faculty':<20} {'Days':<15} {'Time'}")
        print("  " + "-" * 65)
        for ci in sorted(by_room[room], key=lambda x: str(x.time)):
            days_str = "/".join(ti.day.name for ti in ci.time.times)
            print(f"  {ci.course.course_id:<15} {ci.course.section:<10} {ci.faculty:<20} {days_str:<15} {str(ci.time)}")

    # ------------------------------------------------------------------ #
    #  3. FACULTY ASSIGNMENTS  (who teaches what)                         #
    # ------------------------------------------------------------------ #
    print("\n" + "=" * 70)
    print(" FACULTY ASSIGNMENTS")
    print("=" * 70)

    by_faculty = defaultdict(list)
    for ci in schedule:
        by_faculty[ci.faculty].append(ci)

    for faculty_name in sorted(by_faculty):
        courses = by_faculty[faculty_name]
        total_credits = sum(ci.course.credits for ci in courses)
        print(f"\n  {faculty_name}  (Total Credits: {total_credits})")
        print(f"  {'Course':<15} {'Section':<10} {'Room':<15} {'Days':<15} {'Time':<20} {'Credits'}")
        print("  " + "-" * 75)
        for ci in sorted(courses, key=lambda x: str(x.time)):
            days_str = "/".join(ti.day.name for ti in ci.time.times)
            room_str = ci.room if ci.room else "No Room"
            print(f"  {ci.course.course_id:<15} {ci.course.section:<10} {room_str:<15} {days_str:<15} {str(ci.time):<20} {ci.course.credits}")

    print("\n" + "=" * 70)





def main():
    try:
        faculty = scheduler.FacultyConfig(
            name="Dr. Smith",
            maximum_credits=12,
            minimum_credits=3,
            unique_course_limit=2,
            maximum_days=5,
            times={
                "MON": [TimeRange(start="09:00", end="17:00")],
                "WED": [TimeRange(start="09:00", end="17:00")],
                "FRI": [TimeRange(start="09:00", end="17:00")],
            }
        )

        time_slot_config = scheduler.TimeSlotConfig(
            times={
                "MON": [TimeBlock(start="08:00", spacing=60, end="22:00")],
                "TUE": [TimeBlock(start="08:00", spacing=60, end="22:00")],
                "WED": [TimeBlock(start="08:00", spacing=60, end="22:00")],
                "THU": [TimeBlock(start="08:00", spacing=60, end="22:00")],
                "FRI": [TimeBlock(start="08:00", spacing=60, end="22:00")],
            },
            classes=[
                ClassPattern(
                    credits=3,
                    meetings=[
                        Meeting(day="MON", duration=150, lab=False),
                        Meeting(day="WED", duration=150, lab=False),
                    ]
                )
            ]
        )

        config = scheduler.CombinedConfig(
            config=scheduler.SchedulerConfig(
                rooms=["ROOM101"],
                labs=["LAB 101"],
                courses=[
                    scheduler.CourseConfig(
                        course_id="CMSC161",
                        credits=3,
                        room=["ROOM101"],
                        lab=[],
                        faculty=["Dr. Smith"],
                        conflicts=[]
                    )
                ],
                faculty=[faculty]
            ),
            time_slot_config=time_slot_config
        )

        s = scheduler.Scheduler(config)

        found = False
        for schedule in s.get_models():
            display_Schedule(schedule)
            found = True
            break

        if not found:
            print("No valid schedule could be generated.")

    except Exception as exc:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()