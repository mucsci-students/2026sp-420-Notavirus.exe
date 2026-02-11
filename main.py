from scheduler import *
from scheduler.config import ClassPattern, Meeting, TimeBlock

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

def main():
    available_rooms = ["ROOM101", "ROOM102"]
    available_labs = ["LAB101"]
    available_faculty = ["Dr. Smith", "Dr. Jones"]

    course = addCourse(available_rooms, available_labs, available_faculty)

    if course is None:
        print("No course added.")
        return

    print("\nCourse successfully created:")
    print(course)

if __name__ == "__main__":
    main()
