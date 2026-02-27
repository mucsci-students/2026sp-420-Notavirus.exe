# main.py
"""
Main entry point for the Scheduler GUI Application.

Usage:
    python main.py                  # prompts for config file
    python main.py config.json      # uses given config file
"""

import sys
import os
from pathlib import Path


def get_config_path() -> str:
    if len(sys.argv) >= 2:
        return sys.argv[1]

    while True:
        config_path = input("Enter the path to your configuration file: ").strip()
        if not config_path:
            print("Path cannot be empty.")
            continue
        if Path(config_path).exists():
            return config_path
        print(f"File '{config_path}' not found.")
        retry = input("Would you like to try again? [y/n]: ").lower().strip()
        if retry != "y":
            print("Exiting.")
            sys.exit(0)


def main():
    config_path = get_config_path()

    if not Path(config_path).exists():
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)

    # Ensure both the project root and views/ are importable
    root      = os.path.dirname(os.path.abspath(__file__))
    views_dir = os.path.join(root, "views")
    for p in (root, views_dir):
        if p not in sys.path:
            sys.path.insert(0, p)

    # Build models
    from models.config_model    import ConfigModel
    from models.faculty_model   import FacultyModel
    from models.course_model    import CourseModel
    from models.conflict_model  import ConflictModel
    from models.lab_model       import LabModel
    from models.room_model      import RoomModel
    from models.scheduler_model import SchedulerModel

    config_model    = ConfigModel(config_path)
    faculty_model   = FacultyModel(config_model)
    course_model    = CourseModel(config_model)
    conflict_model  = ConflictModel(config_model)
    lab_model       = LabModel(config_model)
    room_model      = RoomModel(config_model)
    scheduler_model = SchedulerModel(config_model)

    # Build controllers (view=None since GUI pages talk to models directly)
    from controllers.faculty_controller  import FacultyController
    from controllers.course_controller   import CourseController
    from controllers.conflict_controller import ConflictController
    from controllers.lab_controller      import LabController
    from controllers.room_controller     import RoomController
    from controllers.schedule_controller import ScheduleController

    faculty_controller  = FacultyController(faculty_model,   None)
    course_controller   = CourseController(course_model,     None, config_model)
    conflict_controller = ConflictController(conflict_model, None)
    lab_controller      = LabController(lab_model,           None)
    room_controller     = RoomController(room_model,         None)
    schedule_controller = ScheduleController(scheduler_model, None)

    # Inject into view classes BEFORE importing them
    from views.faculty_gui_view  import FacultyGUIView
    from views.course_gui_view   import CourseGUIView
    from views.conflict_gui_view import ConflictGUIView
    from views.lab_gui_view      import LabGUIView
    from views.room_gui_view     import RoomGUIView
    from views.schedule_gui_view import ScheduleGUIView

    FacultyGUIView.faculty_model        = faculty_model
    FacultyGUIView.faculty_controller   = faculty_controller

    CourseGUIView.course_model          = course_model
    CourseGUIView.course_controller     = course_controller

    ConflictGUIView.conflict_model      = conflict_model
    ConflictGUIView.conflict_controller = conflict_controller

    LabGUIView.lab_model                = lab_model
    LabGUIView.lab_controller           = lab_controller

    RoomGUIView.room_model              = room_model
    RoomGUIView.room_controller         = room_controller

    ScheduleGUIView.scheduler_model     = scheduler_model
    ScheduleGUIView.schedule_controller = schedule_controller

    # Import GUIView last so all routes are already registered
    from views.gui_view import GUIView  # noqa: F401

    print(f"Loading configuration from: {config_path}")
    from nicegui import ui
    ui.run(title="Course Scheduler", reload=False)


if __name__ in {"__main__", "__mp_main__"}:
    main()