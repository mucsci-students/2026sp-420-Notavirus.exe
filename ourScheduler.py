import scheduler
import os
from pathlib import Path

# Global variables
formatChoice = False
outputFile = ""
scheduleLimit = 0
configFileName = ""
saveToFile = True

def main():
    """Main entry point for the scheduler application"""
    global configFileName
    try:
        promptConfigFile()
        print(f"Using config file: {configFileName}")
        config = scheduler.load_config_from_file(scheduler.CombinedConfig, configFileName)
        runScheduler(config)
    except FileNotFoundError as e:
        print(f"Error: Config file not found - {e}")
    except Exception as e:
        print(f"Error loading config: {e}")


def runScheduler(config: scheduler.CombinedConfig):
    """Run the scheduler with user-specified parameters"""
    specifyLimit()
    promptSaveToFile()
    
    if saveToFile:
        promptOutputFileName()
    
    config.limit = scheduleLimit
    generateSchedule(config, outputFile if saveToFile else None)


def generateSchedule(config: scheduler.CombinedConfig, outputFile: str = None):
    """
    Generate schedules and output to file and/or console
    
    Parameters:
        config: CombinedConfig containing scheduler configuration
        outputFile: Path to output file (None if not saving to file)
    """
    try:
        schedulerGen = scheduler.Scheduler(config)
        
        if outputFile:
            # Save to file
            with open(outputFile, "w") as f:
                if formatChoice:
                    # CSV format - output to both file and console
                    for model in schedulerGen.get_models():
                        for course in model:
                            line = course.as_csv()
                            f.write(line + "\n")
                            print(line)
                        f.write("\n")
                        print()
                else:
                    # JSON format - output to file only, CSV to console
                    for model in schedulerGen.get_models():
                        for course in model:
                            json_data = course.model_dump_json()
                            f.write(json_data + "\n")
                            # Always show CSV in terminal
                            print(course.as_csv())
                        f.write("\n")
                        print()
            
            print(f"\nSchedules successfully written to {outputFile}")
        else:
            # Console output only - always use CSV format
            for model in schedulerGen.get_models():
                for course in model:
                    print(course.as_csv())
                print()
            
            print("\nSchedules displayed in terminal only (not saved to file)")
        
    except IOError as e:
        print(f"Error writing to file {outputFile}: {e}")
    except Exception as e:
        print(f"Error generating schedule: {e}")


def promptSaveToFile():
    """Prompt whether to save output to a file"""
    global saveToFile
    
    while True:
        save_input = input("Do you want to save the schedule to a file? (yes/no): ").strip().lower()
        if save_input in ['yes', 'y']:
            saveToFile = True
            return
        elif save_input in ['no', 'n']:
            saveToFile = False
            return
        else:
            print("Invalid input. Please enter 'yes' or 'no'")


def promptFormat():
    """
    Prompt for output format with validation
    Returns True for CSV, False for JSON
    """
    while True:
        formatInput = input("What output file format do you prefer? (csv/json): ").strip().lower()
        if formatInput in ['csv', 'json']:
            return formatInput == 'csv'
        print("Invalid input. Please enter 'csv' or 'json'")


def promptOutputFileName():
    """Prompt for output filename and format"""
    global formatChoice, outputFile
    
    while True:
        fileName = input("What do you want to call the output file? (without extension): ").strip()
        if fileName:
            # Remove any extension if user added one
            fileName = Path(fileName).stem
            break
        print("Filename cannot be empty. Please try again.")
    
    formatChoice = promptFormat()
    extension = ".csv" if formatChoice else ".json"
    outputFile = fileName + extension
    
    # Warn if file exists
    if os.path.exists(outputFile):
        while True:
            overwrite = input(f"File '{outputFile}' already exists. Overwrite? (yes/no): ").strip().lower()
            if overwrite in ['yes', 'y']:
                break
            elif overwrite in ['no', 'n']:
                print("Please choose a different filename.")
                promptOutputFileName()
                return
            else:
                print("Please enter 'yes' or 'no'")


def specifyLimit():
    """Prompt for schedule limit with validation"""
    global scheduleLimit
    
    while True:
        try:
            limit_input = input("What is the max number of schedules you want generated? ").strip()
            scheduleLimit = int(limit_input)
            
            if scheduleLimit <= 0:
                print("Please enter a positive number.")
                continue
            
            return
        except ValueError:
            print("Invalid input. Please enter a valid number.")


def promptConfigFile():
    """Prompt for config filename with validation"""
    global configFileName
    
    while True:
        fileName = input("Which config file do you want to use? (Must be a CombinedConfig): ").strip()
        
        if not fileName:
            print("Filename cannot be empty. Please try again.")
            continue
        
        # Check if file exists
        if not os.path.exists(fileName):
            print(f"Error: File '{fileName}' not found.")
            retry = input("Would you like to try again? (yes/no): ").strip().lower()
            if retry not in ['yes', 'y']:
                raise FileNotFoundError(f"Config file '{fileName}' not found")
            continue
        
        configFileName = fileName
        return


if __name__ == "__main__":
    main()