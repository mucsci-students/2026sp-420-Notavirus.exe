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

    root = os.path.dirname(os.path.abspath(__file__))
    if root not in sys.path:
        sys.path.insert(0, root)

    print(f"Loading configuration from: {config_path}")

    from controllers.app_controller import SchedulerController
    controller = SchedulerController(config_path)
    controller.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()