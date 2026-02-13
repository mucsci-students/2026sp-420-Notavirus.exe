# add_lab.py
from scheduler import TimeRange

def add_lab():
    # Lab name
    while True:
        name = input("Enter the lab name: ").strip()
        if name != "":
            break

    # Associated course
    while True:
        course = input("Enter the course this lab is associated with (e.g., CMSC 161): ").strip()
        if course != "":
            break

    # Lab instructor
    instructor = input("Enter the instructor name for this lab: ").strip()
    if instructor == "":
        instructor = None

    # Lab meeting days
    while True:
        raw_days = input("Enter the days this lab meets (MTWRF): ").upper()
        days = [ch for ch in raw_days if ch in "MTWRF"]
        if days:
            break
        print("Please enter at least one valid day (MTWRF).")

    # Convert to scheduler day format
    times = {}
    for day in days:
        match day:
            case "M": day_name = "MON"
            case "T": day_name = "TUE"
            case "W": day_name = "WED"
            case "R": day_name = "THU"
            case "F": day_name = "FRI"
            case _: continue

        while True:
            start_time = input(f"Enter start time for {day_name} (HH:MM): ").strip()
            end_time = input(f"Enter end time for {day_name} (HH:MM): ").strip()
            try:
                times[day_name] = [TimeRange(start=start_time, end=end_time)]
                break
            except Exception as e:
                print(f"Invalid time format: {e}")

    # Display summary
    print("\nNew Lab Summary:")
    print(f"Name: {name}")
    print(f"Course: {course.upper()}")
    print(f"Instructor: {instructor}")
    print(f"Times: {times}")

    while True:
        confirm = input("Is this information correct? [y/n]: ").lower()
        if confirm in ("y", "n"):
            break

    if confirm == "y":
        return {
            "name": name,
            "course": course.upper(),
            "instructor": instructor,
            "times": times
        }
    return None
