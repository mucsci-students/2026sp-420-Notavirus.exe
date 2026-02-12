# lab.py
# Functions to add/modify/delete a lab

from scheduler import load_config_from_file, TimeRange
from scheduler.config import CombinedConfig
import scheduler


def add_lab():
    # Lab name
    while True:
        name = input("Enter the lab name: ").strip()
        if name != "":
            break

    # Associated course
    while True:
        course = input("Enter the course this lab is associated with (e.g. CMSC 161): ").strip()
        if course != "":
            break

    # Lab instructor
    instructor = input("Enter the instructor name for this lab: ").strip()
    if instructor == "":
        instructor = None

    # Lab meeting days
    while True:
        raw_days = input("Enter the days this lab meets (MTWRF): ")
        days = []
        for ch in raw_days.upper():
            if ch in {"M", "T", "W", "R", "F"} and ch not in days:
                days.append(ch)

        if len(days) > 0:
            break

        print("Please enter at least one valid day (MTWRF).")

    # Convert to scheduler day format
    daysTimes = {}
    for day in days:
        match day:
            case 'M': day_name = "MON"
            case 'T': day_name = "TUE"
            case 'W': day_name = "WED"
            case 'R': day_name = "THU"
            case 'F': day_name = "FRI"
            case _: continue

        while True:
            start_time = input(f"Enter start time for {day_name} (HH:MM): ").strip()
            end_time = input(f"Enter end time for {day_name} (HH:MM): ").strip()
            try:
                timerange = TimeRange(start=start_time, end=end_time)
                daysTimes[day_name] = [timerange]
                break
            except Exception as e:
                print(f"Invalid time format: {e}")

    # Display summary
    print("\nNew Lab Summary:")
    print(f"Name: {name}")
    print(f"Course: {course.upper()}")
    print(f"Instructor: {instructor}")
    print(f"Times: {daysTimes}")

    # Confirm
    while True:
        confirm = input("\nIs this information correct? [y/n]: ").lower().strip()
        if confirm in ('y', 'n'):
            break

    if confirm == 'y':
        return scheduler.LabConfig(
            name=name,
            course=course.upper(),
            instructor=instructor,
            times=daysTimes
        )
    else:
        while True:
            restart = input("Would you like to restart adding the lab? [y/n]: ").lower().strip()
            if restart in ('y', 'n'):
                break

        if restart == 'y':
            return add_lab()
        else:
            return None
