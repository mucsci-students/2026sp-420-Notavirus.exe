# Filename: course.py
# Description: Functions to add, delete, modify, and list courses
# Authors: Lauryn Gilbert, Hailey, Brooks

from scheduler.config import CombinedConfig
from scheduler import load_config_from_file, CourseConfig
from safe_save import safe_save

# Global Variables
FULL_TIME_MAX_CREDITS = 12
ADJUNCT_MAX_CREDITS = 4
MIN_CREDITS = 3
MIN_DAYS = 1
MAX_DAYS = 5
FULL_TIME_UNIQUE_COURSE_LIMIT = 2
ADJUNCT_UNIQUE_COURSE_LIMIT = 1


def addCourse(available_rooms, available_labs, available_faculty):
    # Course ID
    while True:
        course_id = input("Enter the course ID (Ex. CMSC161): ").strip().upper()
        if course_id != "":
            break

    # Credits
    while True:
        try:
            credits = int(input("Enter the number of credits (1-4): "))
        except ValueError:
            print("Please enter a whole number.")
            continue
        if 1 <= credits <= 4:
            break
        print("Please enter a number between 1 and 4.")

    # Rooms
    print(f"Available rooms: {', '.join(available_rooms)}")
    rooms = []
    while True:
        room = input("Enter a room for this course (or press Enter to finish): ").strip()
        if room == "":
            if len(rooms) == 0:
                print("Please enter at least one room.")
                continue
            break
        if room not in available_rooms:
            print(f"Invalid room. Choose from: {', '.join(available_rooms)}")
            continue
        if room not in rooms:
            rooms.append(room)

    # Labs
    print(f"Available labs: {', '.join(available_labs)}")
    labs = []
    while True:
        lab = input("Enter a lab for this course (or press Enter to skip/finish): ").strip()
        if lab == "":
            break
        if lab not in available_labs:
            print(f"Invalid lab. Choose from: {', '.join(available_labs)}")
            continue
        if lab not in labs:
            labs.append(lab)

    # Faculty
    print(f"Available faculty: {', '.join(available_faculty)}")
    faculty = []
    while True:
        f = input("Enter a faculty member for this course (or press Enter to finish): ").strip()
        if f == "":
            if len(faculty) == 0:
                print("Please enter at least one faculty member.")
                continue
            break
        if f not in available_faculty:
            print(f"Invalid faculty. Choose from: {', '.join(available_faculty)}")
            continue
        if f not in faculty:
            faculty.append(f)

    # Conflicts
    conflicts = []
    while True:
        conflict = input("Enter a conflicting course ID (or press Enter to finish): ").strip().upper()
        if conflict == "":
            break
        if conflict == course_id:
            print("A course cannot conflict with itself.")
            continue
        if conflict not in conflicts:
            conflicts.append(conflict)

    # Summary
    print("\nNew Course Summary:")
    print(f"Course ID: {course_id}")
    print(f"Credits:   {credits}")
    print(f"Rooms:     {rooms}")
    print(f"Labs:      {labs}")
    print(f"Faculty:   {faculty}")
    print(f"Conflicts: {conflicts}")

    # Confirm
    while True:
        confirm = input("\nIs this information correct? [y/n]: ")
        if confirm.lower() in ('y', 'n'):
            break

    if confirm.lower() == 'y':
        return CourseConfig(
            course_id=course_id,
            credits=credits,
            room=rooms,
            lab=labs,
            faculty=faculty,
            conflicts=conflicts
        )
    else:
        while True:
            confirm = input("\nWould you like to restart adding a new course? [y/n]: ")
            if confirm.lower() in ('y', 'n'):
                break
        if confirm.lower() == 'y':
            return addCourse(available_rooms, available_labs, available_faculty)
        else:
            return None

          

# Modify an existing course.
# Preconditions: User knows the course ID.
# Postconditions: Updated course data is collected.
def modifyCourse(config_path: str):
    config = load_config_from_file(CombinedConfig, config_path)
    scheduler_config = config.config

    if not scheduler_config.courses:
        print("There are no courses in the configuration.")
        return

    # Display existing courses
    print("\nExisting Courses:")
    for i, course in enumerate(scheduler_config.courses, 1):
        print(f"{i}. {course.course_id} ({course.credits} credits)")

    # Prompt for course
    while True:
        course_id = input("\nEnter the full course ID to modify: ").strip().upper()
        if course_id:
            break

    matching = [c for c in scheduler_config.courses if c.course_id == course_id]
    if not matching:
        print(f"No course '{course_id}' found.")
        return

    course = matching[0]

    # Ask for updated values
    print("\nEnter new values or press Enter to keep existing ones.")

    credits = input("New credit value: ").strip()
    room = input("New room (comma separated): ").strip()
    lab = input("New lab (comma separated): ").strip()
    faculty = input("New faculty value: ").strip()

    # Summary of modification
    print("\nModification Summary:")
    print(f"Course: {course_id}")
    print(f"Credits: {credits if credits else '[unchanged]'}")
    print(f"Room: {room if room else '[unchanged]'}")
    print(f"Lab: {lab if lab else '[unchanged]'}")
    print(f"Faculty: {faculty if faculty else '[unchanged]'}")

    # Apply or do not apply changes
    while True:
        confirm = input("Apply these changes? [y/n]: ").lower()
        if confirm in ('y', 'n'):
            break
        print("Please enter 'y' or 'n'")

    if confirm == 'n':
        print("Course modification canceled.")
        return

    try:
        with scheduler_config.edit_mode() as editable:
            # Find all matching courses
            matching_courses = [c for c in editable.courses if c.course_id == course_id]

            for editable_course in matching_courses:
                if credits:
                    try:
                        credits_int = int(credits)
                        if credits_int < 0:
                            print(f"Error: Credits cannot be negative.")
                            return
                        editable_course.credits = credits_int
                    except ValueError:
                        print(f"Error: '{credits}' is not a valid number.")
                        return
                if room:
                    room_list = [r.strip() for r in room.split(",") if r.strip()]
                    editable_course.room = room_list

                if lab:
                    editable_course.lab = [l.strip() for l in lab.split(",")]

                if faculty:
                    # Parse faculty input: supports adding (Name) and removing (-Name)
                    # Split by comma
                    changes = [f.strip() for f in faculty.split(",") if f.strip()]
                    
                    current_faculty = editable_course.faculty if editable_course.faculty else []
                    
                    for change in changes:
                        if change.startswith("-"):
                            # Removal
                            name_to_remove = change[1:].strip()
                            if name_to_remove in current_faculty:
                                current_faculty.remove(name_to_remove)
                        else:
                            # Addition
                            if change not in current_faculty:
                                current_faculty.append(change)
                    
                    editable_course.faculty = current_faculty
    except Exception as e:
        print(f"Error modifying course: {e}")
        return

    # Save back to the config file
    if not safe_save(config, config_path):
        print("No changes were written to the file.")
        return

    print(f"Course '{course_id}' updated successfully.")

# Testing function
def modifyCourse_config(course, credits=None, room=None, lab=None, faculty=None):

    if credits is not None:
        if credits < 0:
            course.credits = course.credits
        else:
            course.credits = credits

    if room is not None:
        course.room = room

    if lab is not None:
        course.lab = lab

    if faculty is not None:
        course.faculty = [faculty]

    return course
  


# deleteCourse takes an existing course and removes it from the config_path
#  file through a command line interface. 
#
# Parameters: 
#   config - calls load_config_from_file on config_path to load the config file
#   config_path str - the file to load that is input by the user
# Preconditions: 
#   - The config must contain at least one course.  
#   - The course intended to delete must already exist in the config_path file.
# Postconditions: 
#   - The course will no longer exist in the config_path file. 
#   - If no faculty exists, a message would be in the Command-Line and no 
#      changes to the config will occur 
#   - If the faculty entered does not exist, a message will exist in the 
#      Command-Line letting the user know and no changes will be made to the 
#      config file
# Return: none
def deleteCourse(config, config_path: str):
    scheduler_config = config.config

    if not scheduler_config.courses:
        print("There are no courses in the configuration.")
        return

    # Build section labels
    section_counter = {}
    course_section_labels = []
    for course in scheduler_config.courses:
        cid = course.course_id
        section_counter[cid] = section_counter.get(cid, 0) + 1
        course_section_labels.append(f"{cid}.{section_counter[cid]:02d}")

    # Display with section labels
    print("\nExisting Courses:")
    for i, label in enumerate(course_section_labels, 1):
        course = scheduler_config.courses[i - 1]
        print(f"{i}. {label} ({course.credits} credits)")

    # Prompt for section label (e.g. CMSC 340.01)
    valid_labels = {label: i for i, label in enumerate(course_section_labels)}
    while True:
        course_input = input("\nEnter the course section to delete (e.g. CMSC 340.01): ").strip().upper()
        if course_input in valid_labels:
            break
        print(f"Invalid section. Please enter a section exactly as shown above.")

    target_index = valid_labels[course_input]
    target_course = scheduler_config.courses[target_index]
    course_id = target_course.course_id

    print("\nCourse Summary:")
    print(f"- {course_input} ({target_course.credits} credits)")

    while True:
        confirm = input("Delete this course section? [y/n]: ").lower().strip()
        if confirm in ('y', 'n'):
            break

    if confirm == 'n':
        print("Course deletion canceled.")
        return

    try:
        with scheduler_config.edit_mode() as editable:
            # Clean up conflict references in other courses
            for course in editable.courses:
                if course.course_id != course_id:
                    while course_id in course.conflicts:
                        course.conflicts.remove(course_id)

            # Clean up faculty preferences
            for faculty in editable.faculty:
                if course_id in faculty.course_preferences:
                    del faculty.course_preferences[course_id]

            # Remove only the specific section by index
            editable.courses = [c for i, c in enumerate(editable.courses) if i != target_index]

    except Exception as e:
        print(f"\nError: Failed to delete course due to validation error: {e}")
        return

    if not safe_save(config, config_path):
        print("No changes were written to the file.")
        return
    print(f"\nCourse section '{course_input}' has been permanently deleted.")