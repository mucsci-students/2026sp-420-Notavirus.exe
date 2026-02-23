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


def main():
    """
    Main entry point for the scheduler application.
    
    Parameters:
        None
    
    Returns:
        None
    """
    # Get config file path from command line or prompt
    if len(sys.argv) >= 2:
        config_path = sys.argv[1]
    else:
        config_path = get_config_path()
    
    # Validate config file exists
    if not Path(config_path).exists():
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
    
    try:
        # Create and run main controller
        print(f"Loading configuration from: {config_path}")
        controller = SchedulerController(config_path)
        controller.run()
    
    except KeyboardInterrupt:
        print("\n\nScheduler interrupted by user. Goodbye!")
        sys.exit(0)
    
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def get_config_path() -> str:
    """
    Prompt user for configuration file path.
    
    Parameters:
        None
    
    Returns:
        str: Path to configuration file
    """
    while True:
        config_path = input("Enter the path to your configuration file: ").strip()
        
        if not config_path:
            print("Path cannot be empty.")
            continue
        
        if Path(config_path).exists():
            return config_path
        
        print(f"File '{config_path}' not found.")
        retry = input("Would you like to try again? [y/n]: ").lower().strip()
        if retry != 'y':
            print("Exiting.")
            sys.exit(0)


if __name__ == "__main__":
    main()