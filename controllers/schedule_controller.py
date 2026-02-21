# controllers/schedule_controller.py
"""
ScheduleController - Coordinates schedule generation workflows

This controller class manages schedule generation workflows including:
- Running the scheduler
- Saving schedules to files
- Displaying schedules
"""

import os
from pathlib import Path


class ScheduleController:
    """
    Controller for schedule generation operations.
    
    Coordinates between SchedulerModel (data) and CLIView (UI) to
    implement schedule generation workflows.
    
    Attributes:
        model: SchedulerModel instance
        view: CLIView instance
    """
    
    def __init__(self, scheduler_model, view):
        """
        Initialize ScheduleController.
        
        Parameters:
            scheduler_model (SchedulerModel): Model for schedule generation
            view (CLIView): View for user interface
        
        Returns:
            None
        """
        self.model = scheduler_model
        self.view = view
    
    def run_scheduler(self):
        """
        Complete workflow for running the scheduler.
        
        Steps:
        1. Get schedule limit from user
        2. Ask if saving to file
        3. If saving, get filename and format
        4. Generate schedules
        5. Display/save results
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Get schedule limit
            limit = self.view.get_schedule_limit()
            
            # Step 2: Ask if saving to file
            save_to_file = self.view.confirm("Do you want to save the schedule to a file?")
            
            output_file = None
            format_is_csv = False
            
            if save_to_file:
                # Step 3: Get filename and format
                output_file, format_is_csv = self._get_output_file_info()
                
                if output_file is None:
                    # User cancelled
                    return
            
            # Step 4 & 5: Generate and display/save
            self._generate_and_output(limit, output_file, format_is_csv)
        
        except Exception as e:
            self.view.display_error(f"Error running scheduler: {e}")
    
    def display_configuration(self):
        """
        Display the current configuration in human-readable format.
        
        Parameters:
            None
        
        Returns:
            None
        """
        config = self.model.config_model.config
        self.view.display_configuration(config)
    
    def display_schedules_csv(self, max_schedules: int = 1):
        """
        Display schedules in CSV format to terminal.
        
        Parameters:
            max_schedules (int): Maximum number of schedules to display
        
        Returns:
            None
        """
        try:
            schedules = self.model.generate_schedules(limit=max_schedules)
            self.view.display_schedules_csv(schedules, max_schedules)
        except Exception as e:
            self.view.display_error(f"Error displaying schedules: {e}")
    
    def _get_output_file_info(self) -> tuple[str | None, bool]:
        """
        Get output filename and format from user.
        
        Handles filename validation and overwrite confirmation.
        
        Parameters:
            None
        
        Returns:
            tuple[str | None, bool]: (filename, is_csv) or (None, False) if cancelled
        """
        while True:
            # Get filename
            filename = self.view.get_output_filename()
            
            if not filename:
                self.view.display_message("Filename cannot be empty.")
                continue
            
            # Keep directory but remove extension
            p = Path(filename)
            filename = str(p.parent / p.stem)
            
            # Get format
            format_is_csv = self.view.get_output_format()
            extension = ".csv" if format_is_csv else ".json"
            output_file = filename + extension
            
            # Check if file exists
            if os.path.exists(output_file):
                if self.view.confirm(f"File '{output_file}' already exists. Overwrite?"):
                    return (output_file, format_is_csv)
                else:
                    # Ask if they want to try a different name
                    if not self.view.confirm("Would you like to choose a different filename?"):
                        return (None, False)
                    continue
            
            return (output_file, format_is_csv)
    
    def _generate_and_output(self, limit: int, output_file: str | None, format_is_csv: bool):
        """
        Generate schedules and output to file and/or console.
        
        Parameters:
            limit (int): Maximum schedules to generate
            output_file (str | None): Output filename, or None for console only
            format_is_csv (bool): True for CSV format, False for JSON
        
        Returns:
            None
        """
        try:
            schedules = self.model.generate_schedules(limit=limit)
            
            if output_file:
                # Save to file
                self._save_schedules_to_file(schedules, output_file, format_is_csv)
            else:
                # Console only - always CSV
                self.view.display_schedules_terminal(schedules)
                self.view.display_message("Schedules displayed in terminal only (not saved to file).")
        
        except Exception as e:
            self.view.display_error(f"Error generating schedules: {e}")
    
    def _save_schedules_to_file(self, schedules, output_file: str, format_is_csv: bool):
        """
        Save schedules to file and display to console.
        
        Parameters:
            schedules: Generator of schedule models
            output_file (str): Path to output file
            format_is_csv (bool): True for CSV, False for JSON
        
        Returns:
            None
        """
        try:
            with open(output_file, "w") as f:
                if format_is_csv:
                    # CSV format - save and display
                    for model in schedules:
                        for course in model:
                            line = course.as_csv()
                            f.write(line + "\n")
                            print(line)  # Also show in terminal
                        f.write("\n")
                        print()  # Blank line between schedules
                else:
                    # JSON format - save JSON, display CSV
                    import json
                    scheduleList = []
                    jsonSchedule = []
                    for model in schedules:
                        for course in model:
                            json_data = course.model_dump()  # dict instead of JSON string
                            jsonSchedule.append(json_data)
                            print(course.as_csv())  # Always show CSV in terminal
                        scheduleList.append(jsonSchedule)
                        jsonSchedule = []
                        print()  # Blank line between schedules
                    # Write all schedules as structured JSON
                    json.dump({"generatedSchedules": scheduleList}, f, indent=4)
            
            self.view.display_message(f"Schedules successfully written to {output_file}")
        
        except IOError as e:
            self.view.display_error(f"Error writing to file {output_file}: {e}")