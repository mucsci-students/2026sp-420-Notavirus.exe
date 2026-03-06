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
from controllers.app_controller import SchedulerController
from views.gui_view import GUIView


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
                print(f"Error: Configuration file '{config_path}' not found.")
                sys.exit(1)
            print(f"Loading configuration from: {config_path}")
        else:
            print("No config file provided. Launching GUI — use Load Configuration to load a file.")

        controller = SchedulerController(config_path)
        GUIView.controller = controller
        controller.run()

    except KeyboardInterrupt:
        print("\n\nScheduler interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ in {"__main__", "__mp_main__"}:
    main()