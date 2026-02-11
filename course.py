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


# listCourses lists all the courses
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


# deleteCourse function
def deleteCourse(config_path: str):
    # Load the config 
    config = load_config_from_file(CombinedConfig, config_path)
    scheduler_config = config.config
    
    # Check if there are any courses
    if not scheduler_config.courses:
        print("There are no courses in the configuration.")
        return
    
    # Display existing courses
    print("\nExisting Courses:")
    for i, course in enumerate(scheduler_config.courses, 1):
        print(f"{i}. {course.course_id} ({course.credits} credits)")
    
    # Prompt for the course to delete
    while True:
        course_id = input("\nEnter the full course ID to delete (including spaces e.g. CMSC 100): ").strip().upper()
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
    
    # Remove the course and all references to it
    try:
        with scheduler_config.edit_mode() as editable:
            # First, clean up references in OTHER courses
            for course in editable.courses:
                if course.course_id != course_id:  # Don't process the course we're deleting
                    # Remove course_id from conflicts using list methods
                    while course_id in course.conflicts:
                        course.conflicts.remove(course_id)
            
            # Clean up faculty preferences
            for faculty in editable.faculty:
                if course_id in faculty.course_preferences:
                    del faculty.course_preferences[course_id]
            
            # Finally, remove the actual course (do this LAST)
            editable.courses = [c for c in editable.courses if c.course_id != course_id]
                    
    except Exception as e:
        print(f"\nError: Failed to delete course due to validation error: {e}")
        print(f"Debug - Course ID being deleted: {course_id}")
        return
    
    # Save back to the config file
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(config.model_dump_json(indent=2))
    
    print(f"\nCourse '{course_id}' has been permanently deleted.")