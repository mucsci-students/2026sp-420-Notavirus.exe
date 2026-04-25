# main.py
"""
Main entry point for the Scheduler Application

This application uses MVC architecture:
- Models: Handle data operations (CRUD)
- Views: Handle user input/output
- Controllers: Coordinate models and views
"""

import sys
from pathlib import Path
from dotenv import load_dotenv

from controllers.app_controller import SchedulerController
from views.gui_view import GUIView

load_dotenv()


def main():
    """
    Main entry point for the scheduler application.

    If a config file path is provided as a command-line argument it is loaded
    automatically. Otherwise the GUI launches without a config and the user
    can load one via the Load Configuration dialog.

    Parameters:
        None
    Returns:
        None
    """
    config_path = sys.argv[1] if len(sys.argv) >= 2 else None

    try:
        if config_path:
            if not Path(config_path).exists():
                sys.exit(1)

        controller = SchedulerController(config_path)
        GUIView.controller = controller
        controller.run()

    except KeyboardInterrupt:
        print("\n\nScheduler interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        sys.exit(1)


if __name__ in {"__main__", "__mp_main__"}:
    main()
