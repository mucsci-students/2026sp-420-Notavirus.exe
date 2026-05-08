# main.py
"""
Main entry point for the Scheduler Application

This application uses MVC architecture:
- Models: Handle data operations (CRUD)
- Views: Handle user input/output
- Controllers: Coordinate models and views
"""

import logging
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv

from nicegui import app
from controllers.app_controller import SchedulerController
from views.gui_view import GUIView

load_dotenv()


@app.on_startup
async def _reset_chat_on_startup():
    app.storage.general["server_instance"] = str(uuid.uuid4())


# NiceGUI timers briefly fire during page-navigation cleanup after their parent
# element is already deleted. This is a known NiceGUI behavior — caught internally
# and non-fatal. Filter it so it doesn't pollute the console.
class _SuppressDeletedSlot(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        return "parent slot" not in record.getMessage().lower()


logging.getLogger("nicegui").addFilter(_SuppressDeletedSlot())


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
    except Exception:
        logging.critical("Fatal error during startup", exc_info=True)
        sys.exit(1)


if __name__ in {"__main__", "__mp_main__"}:
    main()
