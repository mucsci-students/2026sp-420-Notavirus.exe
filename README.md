# Notavirus.exe

# Course Scheduler

A command-line tool for managing and generating academic course schedules. Built to handle faculty assignments, course configurations, scheduling conflicts, labs, and rooms — all driven by a JSON config file.

---

## Authors

Lauryn Gilbert, Hailey Haldeman, Luke Leopold, Brooks Stouffer, Ashton Kunkle, Phinehas Maina, Keller Emswiler.

---

## Requirements

- Python 3.13+
- Dependencies listed in `requirements.txt` (install with `pip install -r requirements.txt`)

---

## Project Structure

```
.
├── main.py               # Entry point and CLI menu
├── faculty/              # Faculty add/modify/delete logic
├── course/               # Course add/modify/delete logic
├── room/                 # Room add/modify/delete logic
├── lab/                  # Lab add/modify/delete logic
├── conflict/             # Conflict add/modify/delete logic
├── scheduler/            # Core scheduling engine and config loader
│   └── config.py         # CombinedConfig and related data models
└── example.json          # Example configuration file
```

---

## Setup

1. Clone the repository:

   ```bash
   git clone <repo-url>
   cd <repo-folder>
   ```

2. Install dependencies:

   ```bash
   uv init
   uv add course-constraint-scheduler
   uv sync
   source .venv/bin/activate
   ```

3. Prepare your configuration file (see [Configuration](#configuration) below).

---

## Usage

Run the program by passing a path to your JSON config file:

```bash
python main.py <config_path>
```

**Example:**

```bash
python main.py example.json
```

Once running, you'll see an interactive menu.

Click the button of the action (or group of actions) you want to perform and follow the prompts.

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

Conflicts indicate pairs of courses that cannot be scheduled at the same time — typically because students in the same cohort are likely enrolled in both.

```json
{
  "course_id": "CMSC 340",
  "conflicts": ["CMSC 380", "CMSC 420", "CMSC 453"]
}
```

---

## Features

- **Faculty Management** — Add, modify, and delete faculty members including their name, position type, credit limits, course preferences (weighted 0–10), and availability by day and time.
- **Course Management** — Add, modify, and delete courses from the configuration.
- **Conflict Management** — Define course pairs that must not overlap. The scheduler automatically avoids room, faculty, and time conflicts; the conflicts list is specifically for student co-enrollment constraints.
- **Lab Management** — Add, modify, and delete lab sections tied to courses.
- **Room Management** — Add, modify, and delete rooms available for scheduling.
- **Run Scheduler** — Generate an optimized schedule based on the current configuration using a constraint solver.
- **Export to CSV** — Display or export generated schedules in CSV format.

---

## Example Config

An `example.json` file is included in the repository to help you get started. It contains a sample set of CMSC courses with pre-defined conflicts, faculty, and time slots.

---

## Contributing

When adding new menu options, follow the existing hierarchical pattern in `views/gui_view.py` and `views/X_gui_view.py`:

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
