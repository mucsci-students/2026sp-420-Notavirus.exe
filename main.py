import sys
import scheduler
from scheduler import Day, TimeRange
from conflict import *

# Load the config file and create a scheduler object.
# Returns a tuple with a CombinedConfig and scheduler object variables.
def initConfig(config_path: str):
    # Load configuration from JSON file
    config = load_config_from_file(CombinedConfig, config_path)
    # Create scheduler obj
    scheduler_obj = Scheduler(config)
    return (config, scheduler_obj)

def main():
    config_path = sys.argv[1]
    (config, scheduler) = initConfig(config_path)
    modifyconflict_input(config=config)

if __name__ == "__main__":
    main()

