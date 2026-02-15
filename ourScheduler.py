# In ourScheduler.py, make sure you have:
import scheduler
from scheduler import Day, TimeRange, Scheduler
from scheduler.config import ClassPattern, Meeting, TimeBlock
import os
from pathlib import Path

#Global Variables
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 3
MIN_DAYS = 1
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1
# More variables
formatChoice = False
outputFile = ""
scheduleLimit = 0
configFileName = ""
saveToFile = True


# Display the schedule in a human readable format
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
        slot_label = str(ci.time).split(",")[0].split(" ", 1)[1].replace("^", "")
        time_slot_labels.add(slot_label)
        for time_instance in ci.time.times:
            day_name = time_instance.day.name
            room_str = ci.room if ci.room else "No Room"
            grid[(day_name, slot_label)].append((ci.course.course_id, room_str))

    time_slots_sorted = sorted(time_slot_labels)

    print(f"{'Time':<{time_w}}" + "".join(f"{day:<{col_w}}" for day in DAYS_ORDER))
    print(dash_sep)

    for slot_label in time_slots_sorted:
        max_entries = max(
            len(grid.get((day, slot_label), [])) for day in DAYS_ORDER
        )

        for i in range(max(1, max_entries)):
            # Course ID line
            if i == 0:
                row = f"{slot_label:<{time_w}}"
            else:
                row = f"{'':<{time_w}}"
            for day in DAYS_ORDER:
                entries = grid.get((day, slot_label), [])
                if i < len(entries):
                    cell = entries[i][0]  # course_id
                elif i == 0:
                    cell = "-"
                else:
                    cell = ""
                row += f"{cell:<{col_w}}"
            print(row)

            # Room line (directly under course)
            row = f"{'':<{time_w}}"
            for day in DAYS_ORDER:
                entries = grid.get((day, slot_label), [])
                if i < len(entries):
                    cell = f"({entries[i][1]})"  # room
                else:
                    cell = ""
                row += f"{cell:<{col_w}}"
            print(row)

        # Dash separator between time slots
        print(f"{'':<{time_w}}" + "".join(f"{'─' * (col_w - 1):<{col_w}}" for _ in DAYS_ORDER))
        print()

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


# For running the scheduler
def main():
    """Main entry point for the scheduler application"""
    global configFileName
    try:
        promptConfigFile()
        print(f"Using config file: {configFileName}")
        config = scheduler.load_config_from_file(scheduler.CombinedConfig, configFileName)
        runScheduler(config)
    except FileNotFoundError as e:
        print(f"Error: Config file not found - {e}")
    except Exception as e:
        print(f"Error loading config: {e}")


def runScheduler(config: scheduler.CombinedConfig):
    """Run the scheduler with user-specified parameters"""
    specifyLimit()
    promptSaveToFile()
    
    if saveToFile:
        promptOutputFileName()
    
    config.limit = scheduleLimit
    generateSchedule(config, outputFile if saveToFile else None)


def generateSchedule(config: scheduler.CombinedConfig, outputFile: str = None):
    """
    Generate schedules and output to file and/or console
    
    Parameters:
        config: CombinedConfig containing scheduler configuration
        outputFile: Path to output file (None if not saving to file)
    """
    try:
        schedulerGen = scheduler.Scheduler(config)
        
        if outputFile:
            # Save to file
            with open(outputFile, "w") as f:
                if formatChoice:
                    # CSV format - output to both file and console
                    for model in schedulerGen.get_models():
                        for course in model:
                            line = course.as_csv()
                            f.write(line + "\n")
                            print(line)
                        f.write("\n")
                        print()
                else:
                    # JSON format - output to file only, CSV to console
                    for model in schedulerGen.get_models():
                        for course in model:
                            json_data = course.model_dump_json()
                            f.write(json_data + "\n")
                            # Always show CSV in terminal
                            print(course.as_csv())
                        f.write("\n")
                        print()
            
            print(f"\nSchedules successfully written to {outputFile}")
        else:
            # Console output only - always use CSV format
            for model in schedulerGen.get_models():
                for course in model:
                    print(course.as_csv())
                print()
            
            print("\nSchedules displayed in terminal only (not saved to file)")
        
    except IOError as e:
        print(f"Error writing to file {outputFile}: {e}")
    except Exception as e:
        print(f"Error generating schedule: {e}")


def promptSaveToFile():
    """Prompt whether to save output to a file"""
    global saveToFile
    
    while True:
        save_input = input("Do you want to save the schedule to a file? (yes/no): ").strip().lower()
        if save_input in ['yes', 'y']:
            saveToFile = True
            return
        elif save_input in ['no', 'n']:
            saveToFile = False
            return
        else:
            print("Invalid input. Please enter 'yes' or 'no'")


def promptFormat():
    """
    Prompt for output format with validation
    Returns True for CSV, False for JSON
    """
    while True:
        formatInput = input("What output file format do you prefer? (csv/json): ").strip().lower()
        if formatInput in ['csv', 'json']:
            return formatInput == 'csv'
        print("Invalid input. Please enter 'csv' or 'json'")


def promptOutputFileName():
    """Prompt for output filename and format"""
    global formatChoice, outputFile
    
    while True:
        fileName = input("What do you want to call the output file? (without extension): ").strip()
        if fileName:
            # Remove any extension if user added one
            fileName = Path(fileName).stem
            break
        print("Filename cannot be empty. Please try again.")
    
    formatChoice = promptFormat()
    extension = ".csv" if formatChoice else ".json"
    outputFile = fileName + extension
    
    # Warn if file exists
    if os.path.exists(outputFile):
        while True:
            overwrite = input(f"File '{outputFile}' already exists. Overwrite? (yes/no): ").strip().lower()
            if overwrite in ['yes', 'y']:
                break
            elif overwrite in ['no', 'n']:
                print("Please choose a different filename.")
                promptOutputFileName()
                return
            else:
                print("Please enter 'yes' or 'no'")


def specifyLimit():
    """Prompt for schedule limit with validation"""
    global scheduleLimit
    
    while True:
        try:
            limit_input = input("What is the max number of schedules you want generated? ").strip()
            scheduleLimit = int(limit_input)
            
            if scheduleLimit <= 0:
                print("Please enter a positive number.")
                continue
            
            return
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def promptConfigFile():
    """Prompt for config filename with validation"""
    global configFileName
    
    while True:
        fileName = input("Which config file do you want to use? (Must be a CombinedConfig): ").strip()
        
        if not fileName:
            print("Filename cannot be empty. Please try again.")
            continue
        
        # Check if file exists
        if not os.path.exists(fileName):
            print(f"Error: File '{fileName}' not found.")
            retry = input("Would you like to try again? (yes/no): ").strip().lower()
            if retry not in ['yes', 'y']:
                raise FileNotFoundError(f"Config file '{fileName}' not found")
            continue
        
        configFileName = fileName
        return


if __name__ == "__main__":
    main()