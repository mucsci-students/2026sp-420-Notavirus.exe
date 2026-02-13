import scheduler
from scheduler import Day, TimeRange
from conflict import *
CONFIG_JSON = "example.json"

# Save data to a config.json file
def save_config_json(config: CombinedConfig, filename: str) -> None:
    with open(filename, 'w') as file:
        file.write(config.model_dump_json(indent=2))

# Load the config file and create a scheduler object.
# Returns a tuple with a CombinedConfig and scheduler object variables.
def initConfig():
    # Load configuration from JSON file
    config = load_config_from_file(CombinedConfig, CONFIG_JSON)
    # Create scheduler obj
    scheduler_obj = Scheduler(config)
    return (config, scheduler_obj)

def main():
    (config, scheduler) = initConfig()
    modifyconflict_input(config=config)

if __name__ == "__main__":
    main()

