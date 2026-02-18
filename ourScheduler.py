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


def display_Configuration(config: scheduler.CombinedConfig):
    """Display the configuration file in a human-readable format"""
    
    print("\n" + "=" * 80)
    print(" CONFIGURATION FILE CONTENTS")
    print("=" * 80)
    
    # Display general settings
    print("\nGENERAL SETTINGS:")
    print(f"  Schedule Limit: {config.limit}")
    if hasattr(config, 'optimizer_flags') and config.optimizer_flags:
        print(f"  Optimizer Flags: {', '.join(config.optimizer_flags)}")
    
    # Display courses
    print("\nCOURSES:")
    if config.config.courses:
        print(f"  {'Course ID':<15} {'Credits':<10} {'Rooms':<30} {'Labs':<20} {'Conflicts'}")
        print("  " + "-" * 100)
        for course in config.config.courses:
            course_id = course.course_id if hasattr(course, 'course_id') else "N/A"
            credits = course.credits if hasattr(course, 'credits') else "N/A"
            
            # Handle rooms
            rooms = "N/A"
            if hasattr(course, 'room') and course.room:
                rooms = ", ".join(course.room) if isinstance(course.room, list) else str(course.room)
            
            # Handle labs
            labs = "N/A"
            if hasattr(course, 'lab') and course.lab:
                labs = ", ".join(course.lab) if isinstance(course.lab, list) else str(course.lab)
            
            # Handle conflicts
            conflicts = "None"
            if hasattr(course, 'conflicts') and course.conflicts:
                conflicts = ", ".join(course.conflicts) if isinstance(course.conflicts, list) else str(course.conflicts)
            
            # Truncate long strings for display
            rooms_display = rooms[:28] + ".." if len(rooms) > 30 else rooms
            labs_display = labs[:18] + ".." if len(labs) > 20 else labs
            conflicts_display = conflicts[:30] + ".." if len(conflicts) > 32 else conflicts
            
            print(f"  {course_id:<15} {credits:<10} {rooms_display:<30} {labs_display:<20} {conflicts_display}")
    else:
        print("  No courses configured.")
    
    # Display faculty
    print("\nFACULTY:")
    if config.config.faculty:
        print(f"  {'Name':<15} {'Max Credits':<12} {'Min Credits':<12} {'Unique Limit':<13} {'Max Days':<10} {'Mandatory Days'}")
        print("  " + "-" * 100)
        for faculty in config.config.faculty:
            name = faculty.name if hasattr(faculty, 'name') else "N/A"
            max_cred = faculty.maximum_credits if hasattr(faculty, 'maximum_credits') else "N/A"
            min_cred = faculty.minimum_credits if hasattr(faculty, 'minimum_credits') else "N/A"
            unique = faculty.unique_course_limit if hasattr(faculty, 'unique_course_limit') else "N/A"
            max_days = faculty.maximum_days if hasattr(faculty, 'maximum_days') else "N/A"
            
            # Handle mandatory days
            mandatory = "None"
            if hasattr(faculty, 'mandatory_days') and faculty.mandatory_days:
                mandatory = ", ".join(faculty.mandatory_days)
            
            print(f"  {name:<15} {str(max_cred):<12} {str(min_cred):<12} {str(unique):<13} {str(max_days):<10} {mandatory}")
        
        # Display faculty preferences summary
        print("\n  FACULTY PREFERENCES:")
        for faculty in config.config.faculty:
            name = faculty.name if hasattr(faculty, 'name') else "Unknown"
            print(f"\n    {name}:")
            
            # Course preferences
            if hasattr(faculty, 'course_preferences') and faculty.course_preferences:
                prefs = ", ".join([f"{k}({v})" for k, v in faculty.course_preferences.items()])
                print(f"      Courses: {prefs}")
            
            # Room preferences
            if hasattr(faculty, 'room_preferences') and faculty.room_preferences:
                prefs = ", ".join([f"{k}({v})" for k, v in faculty.room_preferences.items()])
                print(f"      Rooms: {prefs}")
            
            # Lab preferences
            if hasattr(faculty, 'lab_preferences') and faculty.lab_preferences:
                prefs = ", ".join([f"{k}({v})" for k, v in faculty.lab_preferences.items()])
                print(f"      Labs: {prefs}")
    else:
        print("  No faculty configured.")
    
    # Display rooms
    print("\nROOMS:")
    if config.config.rooms:
        for room in config.config.rooms:
            print(f"  - {room}")
    else:
        print("  No rooms configured.")
    
    # Display labs
    print("\nLABS:")
    if hasattr(config.config, 'labs') and config.config.labs:
        for lab in config.config.labs:
            print(f"  - {lab}")
    else:
        print("  No labs configured.")
    
    # Display time slot patterns
    print("\nTIME SLOT PATTERNS:")
    if hasattr(config, 'time_slot_config') and hasattr(config.time_slot_config, 'classes'):
        for i, pattern in enumerate(config.time_slot_config.classes, 1):
            credits = pattern.credits if hasattr(pattern, 'credits') else "N/A"
            disabled = " [DISABLED]" if hasattr(pattern, 'disabled') and pattern.disabled else ""
            print(f"  Pattern {i} ({credits} credits){disabled}:")
            
            if hasattr(pattern, 'meetings') and pattern.meetings:
                for meeting in pattern.meetings:
                    day = meeting.day if hasattr(meeting, 'day') else "N/A"
                    duration = meeting.duration if hasattr(meeting, 'duration') else "N/A"
                    lab = " [LAB]" if hasattr(meeting, 'lab') and meeting.lab else ""
                    print(f"    - {day}: {duration} min{lab}")
            
            if hasattr(pattern, 'start_time') and pattern.start_time:
                print(f"    Start Time: {pattern.start_time}")
    else:
        print("  No time slot patterns configured.")
    
    print("\n" + "=" * 80)


def display_Schedules_csv(config: scheduler.CombinedConfig, max_schedules: int = 1):
    """
    Print up to `max_schedules` schedules in CSV format to the terminal.

    Parameters:
        config: CombinedConfig containing scheduler configuration
        max_schedules: maximum number of schedules to print (default 1)
    """
    try:
        schedulerGen = scheduler.Scheduler(config)

        count = 0
        for model in schedulerGen.get_models():
            count += 1
            print(f"\nSchedule {count}")
            for course in model:
                try:
                    print(course.as_csv())
                except Exception:
                    # Fallback: print a JSON-ish representation if as_csv unavailable
                    try:
                        print(course.model_dump_json())
                    except Exception:
                        print(str(course))
            # blank line between schedules
            print()
            if count >= max_schedules:
                break

        if count == 0:
            print("No valid schedule could be generated.")

    except Exception as e:
        print(f"Error displaying schedules in CSV: {e}")


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