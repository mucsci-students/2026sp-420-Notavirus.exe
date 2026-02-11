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
def display_Schedule(schedule: list):
    if not schedule:
        print("No schedule to display.")
        return

    from collections import defaultdict

    DAYS_ORDER = ["MON", "TUE", "WED", "THU", "FRI"]

    # All widths calculated from col_w
    col_w = 20
    time_w = 12
    total_w = time_w + (col_w * len(DAYS_ORDER))
    eq_sep = "=" * total_w
    dash_sep = "-" * total_w
    inner_sep = "-" * (total_w - 2)

    # ------------------------------------------------------------------ #
    #  1. FULL TIMETABLE GRID  (rows = time slots, columns = days)        #
    # ------------------------------------------------------------------ #
    print("\n" + eq_sep)
    print(" FULL TIMETABLE GRID")
    print(eq_sep)

    grid = defaultdict(list)
    time_slot_labels = set()

    for ci in schedule:
        slot_label = str(ci.time).split(",")[0].split(" ", 1)[1]
        time_slot_labels.add(slot_label)
        for time_instance in ci.time.times:
            day_name = time_instance.day.name
            room_str = ci.room if ci.room else "No Room"
            grid[(day_name, slot_label)].append(f"{ci.course.course_id} ({room_str})")

    time_slots_sorted = sorted(time_slot_labels)

    print(f"{'Time':<{time_w}}" + "".join(f"{day:<{col_w}}" for day in DAYS_ORDER))
    print(dash_sep)

    for slot_label in time_slots_sorted:
        row = f"{slot_label:<{time_w}}"
        for day in DAYS_ORDER:
            entries = grid.get((day, slot_label), [])
            cell = ", ".join(entries) if entries else "-"
            row += f"{cell:<{col_w}}"
        print(row)

    # ------------------------------------------------------------------ #
    #  2. ROOM / TIME SLOT LAYOUT                                         #
    # ------------------------------------------------------------------ #
    print("\n" + eq_sep)
    print(" ROOM / TIME SLOT LAYOUT")
    print(eq_sep)

    by_room = defaultdict(list)
    for ci in schedule:
        room_key = ci.room if ci.room else "No Room"
        by_room[room_key].append(ci)

    for room in sorted(by_room):
        print(f"\n  Room: {room}")
        print(f"  {'Course':<15} {'Section':<10} {'Faculty':<20} {'Days':<15} {'Time'}")
        print("  " + inner_sep)
        for ci in sorted(by_room[room], key=lambda x: str(x.time)):
            days_str = "/".join(ti.day.name for ti in ci.time.times)
            time_str = str(ci.time).split(",")[0].split(" ", 1)[1]
            print(f"  {ci.course.course_id:<15} {ci.course.section:<10} {ci.faculty:<20} {days_str:<15} {time_str}")

    # ------------------------------------------------------------------ #
    #  3. FACULTY ASSIGNMENTS  (who teaches what)                         #
    # ------------------------------------------------------------------ #
    print("\n" + eq_sep)
    print(" FACULTY ASSIGNMENTS")
    print(eq_sep)

    by_faculty = defaultdict(list)
    for ci in schedule:
        by_faculty[ci.faculty].append(ci)

    for faculty_name in sorted(by_faculty):
        courses = by_faculty[faculty_name]
        total_credits = sum(ci.course.credits for ci in courses)
        print(f"\n  {faculty_name}  (Total Credits: {total_credits})")
        print(f"  {'Course':<15} {'Section':<10} {'Room':<15} {'Days':<15} {'Time':<20} {'Credits'}")
        print("  " + inner_sep)
        for ci in sorted(courses, key=lambda x: str(x.time)):
            days_str = "/".join(ti.day.name for ti in ci.time.times)
            room_str = ci.room if ci.room else "No Room"
            time_str = str(ci.time).split(",")[0].split(" ", 1)[1]
            print(f"  {ci.course.course_id:<15} {ci.course.section:<10} {room_str:<15} {days_str:<15} {time_str:<20} {ci.course.credits}")

    print("\n" + eq_sep)




def main():
    try:
        # Load config from JSON file
        config = scheduler.load_config_from_file(
            scheduler.CombinedConfig,
            "example.json"
        )

        # Create scheduler
        s = scheduler.Scheduler(config)

        # Generate and display schedule
        found = False
        for schedule in s.get_models():
            display_Schedule(schedule)
            found = True
            break

        if not found:
            print("No valid schedule could be generated.")

    except FileNotFoundError:
        print("Error: example.json not found.")
    except Exception as exc:
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()