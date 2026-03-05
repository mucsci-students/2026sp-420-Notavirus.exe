# Notavirus.exe


# Course Scheduler

A graphical web-based tool for managing and generating academic course schedules. 
Built with NiceGUI to handle faculty assignments, course configurations, 
scheduling conflicts, labs, and rooms — all driven by a JSON config file.

---


## Authors

Lauryn Gilbert, Hailey Haldeman, Luke Leopold, Brooks Stouffer, 
Ashton Kunkle, Phinehas Maina, Keller Emswiler.

---


## Requirements

- Python 3.13+
- UV package manager (recommended) or pip
- NiceGUI for the web interface
- course-constraint-scheduler library

---


## Project Structure

```
.
├── main.py                  # Entry point - launches GUI
├── controllers/             # Application logic and workflows
│   ├── app_controller.py    # Main controller
│   ├── faculty_controller.py
│   ├── course_controller.py
│   └── ...
├── models/                  # Data operations (CRUD)
│   ├── faculty_model.py
│   ├── course_model.py
│   └── ...
├── views/                   # GUI interface
│   ├── gui_view.py          # Main GUI and navigation
│   ├── faculty_gui_view.py
│   ├── course_gui_view.py
│   └── ...
├── scheduler/               # Core scheduling engine
│   └── config.py            # Configuration data models
├── tests/                   # Test suite
│   ├── test_models/         # 99 model tests
│   ├── test_integration/    # 3 integration tests
│   └── test_controllers/    # 13 controller tests
└── example.json             # Example configuration file
```

---


## Setup

1. Install UV (if you don't have it)
UV is a fast Python package manager. Install it with:
  ```bash
    # macOS/Linux
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Windows
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

    # Or with pip
    pip install uv
  ```

2. Clone the repository
  ```bash
    git clone <repo-url>
    cd 2026sp-420-Notavirus.exe
  ```

3. Install dependencies
  ```bash
    # Initialize UV environment
    uv init

    # Install required packages
    uv pip install nicegui
    uv pip install course-constraint-scheduler

    # Sync environment
    uv sync

    # Activate virtual environment
    source .venv/bin/activate  # macOS/Linux
    # or
    .venv\Scripts\activate     # Windows

  ```

4. Prepare your configuration file
Use the included example.json as a template or create your own (see Configuration below).

---


## Usage

Run the program by passing a path to your JSON config file:

```bash
python main.py <config_path>
```

Once running, you'll see an interactive menu.

What happens:

- Configuration loads from the JSON file
- GUI server starts on port 8080
- Your browser opens automatically to http://localhost:8080
- Use the graphical interface to manage schedules

To stop the server:

Press Ctrl+C in the terminal

** Example:
python main.py example.json

Output:
- Loading configuration from: example.json
- 🚀 Starting Scheduler GUI...
- 🌐 Browser will open at: http://localhost:8080
- 🛑 To stop: Press Ctrl+C in this terminal

---


## Configuration

The scheduler is driven by a JSON config file. Below is an overview of the key sections:

### Faculty

Each faculty entry defines a faculty member's teaching preferences and availability.

```json
{
  "name": "Dr. Smith",
  "maximum_credits": 12,
  "minimum_credits": 6,
  "unique_course_limit": 3,
  "course_preferences": {
    "CMSC 161": 8,
    "CMSC 340": 5
  },
  "maximum_days": 5,
  "times": [{ "days": ["M", "W", "F"], "start": "09:00", "end": "10:00" }]
}
```

### Courses

Each course entry defines a course offered in the schedule.

```json
{
  "course_id": "CMSC 340",
  "name": "Data Structures",
  "credits": 3,
  "conflicts": ["CMSC 380", "CMSC 420"]
}
```

### Conflicts

Conflicts indicate pairs of courses that cannot be scheduled at the same time
 — typically because students in the same cohort are likely enrolled in both.

```json
{
  "course_id": "CMSC 340",
  "conflicts": ["CMSC 380", "CMSC 420", "CMSC 453"]
}
```

---


## Features

### Sprint 1
- **Faculty Management** — Add, modify, and delete faculty members including their name, position type, credit limits, course preferences (weighted 0–10), and availability by day and time. Course preferences can reference courses that do not yet exist in the configuration (hypothetical courses). These preferences are stored in-memory and will only persist to disk when Save Configuration is used, provided the referenced courses exist at save time.
- **Course Management** — Add, modify, and delete courses from the configuration.
- **Conflict Management** — Define course pairs that must not overlap. The scheduler automatically avoids room, faculty, and time conflicts; the conflicts list is specifically for student co-enrollment constraints.
- **Lab Management** — Add, modify, and delete lab sections tied to courses.
- **Room Management** — Add, modify, and delete rooms available for scheduling.
- **Run Scheduler** — Generate an optimized schedule based on the current configuration using a constraint solver.
- **Export to CSV** — Display or export generated schedules in CSV format.
- **In-Memory Editing** - All add, modify, and delete operations update the in-memory configuration only. Changes are not written to disk until Save Configuration is explicitly triggered from the relevant page.

### Sprint 2
#### Scheduler Config Editor
- **Save Configuration** — Save the current configuration to a JSON file from within the GUI.
- **Load Configuration** — Load a JSON configuration file from within the GUI without restarting.
- Sometimes you may see changes in sections that you did not make because of the JSON reloading after modifications.

#### Schedule Generator
- **Limit Override** — Input field to override the schedule generation limit from the configuration file.
- **Optimization Selection** — Checkboxes to enable/disable individual optimizer flags, overriding the configuration file.
- **Generate Button** — Trigger schedule generation from the GUI with current settings.

#### Schedule Viewer
- **Schedule Navigation** — Browse between multiple generated schedules using previous/next controls.
- **By Room View** — Tabular display of generated schedules organized by room and lab.
- **By Faculty View** — Tabular display of generated schedules organized by faculty member.
- **Export Schedules** — Save generated schedules to a file from the viewer.
- **Import Schedules** — Load previously exported schedules directly into the schedule viewer.

#### Build System
- **pyproject.toml** — Project metadata and dependencies managed via `pyproject.toml`.
- **uv tooling** — Full `uv` support for dependency management and virtual environments.
- **pytest** — Test suite runs via `pytest` with coverage reporting.

---


## Example Config

An `example.json` file is included in the repository to help you get started. 
It contains a sample set of CMSC courses with pre-defined conflicts, faculty, 
and time slots.

---


## GUI Navigation 

The main GUI presents a menu with buttons for each feature:
┌─────────────────────────┐
│      Scheduler          │
├─────────────────────────┤
│  Faculty   │    Room    │
│  Course    │  Conflict  │
│           Lab           │
├─────────────────────────┤
│     Print Config        │
│     Run Scheduler       │
│    Display Schedules    │
└─────────────────────────┘
Click any button to access that feature's interface. Each feature page includes 
forms for input and displays results in a user-friendly format.

---


## Testing

The project includes a comprehensive test suite:
```bash
# Run all tests
pytest tests/ -v

# Run only model tests (99 tests)
pytest tests/test_models/ -v

# Run only controller tests (13 tests)
pytest tests/test_controllers/ -v

# Run only controller tests (3 tests)
pytest tests/test_integration/ -v

# Run with coverage
pytest tests/ --cov=models --cov=controllers
```
Test Coverage:

✅ 99 model tests - Data operations and business logic
✅ 13 controller tests - Integration and workflow
✅ 3 integration tests - End-to-end workflows

---


## Contributing

When adding new menu options, follow the existing hierarchical pattern 
in `views/gui_view.py` and `views/X_gui_view.py`:

```python
@ui.page('/feature_group/feature')
@staticmethod
def your_function():
    """
    Displays the GUI for your function.

    Parameters:
        None
    Returns:
        None
    """
    GUITheme.applyTheming()
    ui.query('body').style('background-color: var(--q-primary)')
    with ui.column().classes('gap-6 items-center w-full'):
        # Your GUI code here
```

---


## Troubleshooting 

Port Already in Use
  If you see ERROR: "[Errno 48] Address already in use":
  ```bash
    # Kill the process using port 8080
    lsof -ti:8080 | xargs kill -9

    # Then run again
    python main.py example.json
  ```

Pydantic Warnings
  You may see warnings like UnsupportedFieldAttributeWarning - these are 
  harmless and come from the scheduler library. To suppress them:
  ```python
    # Add to top of main.py
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="pydantic")
  ```

Browser Doesn't Open
  Manually navigate to: http://localhost:8080

Hypothetical Course Preferences
Faculty course preferences can reference courses that don't exist yet. However, the configuration file on disk must always be valid. If the app fails to start with a validation error referencing a course preference, manually remove the invalid entry from the JSON file before restarting.

---

# Acknowledgements

Built using: 
  - NiceGUI - Python web framework
  - course-constraint-scheduler - Scheduling engine
  - Pydantic for data validation

--- 


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright © 2026 Notavirus.exe

---