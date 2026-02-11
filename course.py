# menu_functions.py
from scheduler import load_config_from_file, Day, TimeRange
from scheduler.config import CombinedConfig

# Global Variables
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 3
MIN_DAYS = 1
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1



def listCourses(config_path: str):
    config = load_config_from_file(CombinedConfig, config_path)
    scheduler_config = config.config

    if not scheduler_config.courses:
        print("There are no courses in the configuration.")
        return

    print("\nCourses:")
    for i, course in enumerate(scheduler_config.courses, 1):
        print(f"\n{i}. {course.course_id} ({course.credits} credits)")
        print(f"   Rooms: {', '.join(course.room) if course.room else 'None'}")
        print(f"   Labs: {', '.join(course.lab) if course.lab else 'None'}")
        print(f"   Faculty: {', '.join(course.faculty) if course.faculty else 'None'}")
        print(f"   Conflicts: {', '.join(course.conflicts) if course.conflicts else 'None'}")

def deleteCourse(config_path: str):
    # Load the config 
    config = load_config_from_file(CombinedConfig, config_path)
    scheduler_config = config.config

    # Return if no courses are in config
    listCourses(config_path)

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

