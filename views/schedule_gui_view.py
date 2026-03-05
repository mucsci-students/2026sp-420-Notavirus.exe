# views/schedule_gui_view.py
"""
ScheduleGUIView - Graphical-user interface for schedule interactions

This view class handles all GUI pages related to schedules, including:
- Running the scheduler (limit input, generate button)
- Displaying generated schedules with prev/next navigation
- Tabular views by Room/Lab and by Faculty, with filter dropdowns
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor

from nicegui import ui
from scheduler import OptimizerFlags
from views.gui_theme import GUITheme


# ---------------------------------------------------------------------------
# Module-level state
#
# NiceGUI with reload=False runs page handlers inside a subprocess.
# Class attributes written in the main process are NOT visible there.
# Module-level objects survive because the subprocess re-imports the module
# fresh, but values assigned *before* ui.run() are baked in at import time.
# The _ModelDescriptor mirrors writes into _state so subprocess handlers
# can always read the model via _state._scheduler_model.
# ---------------------------------------------------------------------------
class _ScheduleState:
    """Shared state: generated schedules + scheduler model reference."""

    def __init__(self):
        self.schedules: list[list] = []   # list[list[CourseInstance]]
        self.current_index: int = 0
        self._scheduler_model = None


_state = _ScheduleState()


# ---------------------------------------------------------------------------
# Row builders
# ---------------------------------------------------------------------------

def _format_time(time_instance) -> str:
    return str(time_instance)


def _unique_key(prefix: str, idx: int) -> str:
    """Generate a guaranteed-unique row key."""
    return f"{prefix}_{idx}"


def _build_room_rows(schedule: list, location_filter: str | None = None) -> list[dict]:
    """
    One row per (course × room) and per (course × lab).

    Columns: _key, location, type, course, section, faculty, times

    If location_filter is set, only rows whose location matches are returned.
    Rows are sorted deterministically by (location, course, section).
    """
    rows = []
    idx = 0
    for ci in sorted(schedule, key=lambda c: (c.course_str,)):
        parts = ci.course_str.rsplit(".", 1)
        course_id = parts[0] if len(parts) == 2 else ci.course_str
        section   = parts[1] if len(parts) == 2 else "01"

        lecture_times = "; ".join(
            _format_time(t)
            for i, t in enumerate(ci.times)
            if i != ci.lab_index
        )
        lab_time = (
            _format_time(ci.times[ci.lab_index])
            if ci.lab_index is not None else ""
        )

        if ci.room:
            rows.append({
                "_key":     _unique_key("r", idx),
                "location": ci.room,
                "type":     "Room",
                "course":   course_id,
                "section":  section,
                "faculty":  ci.faculty,
                "times":    lecture_times,
            })
            idx += 1

        if ci.lab and ci.lab_index is not None:
            rows.append({
                "_key":     _unique_key("r", idx),
                "location": ci.lab,
                "type":     "Lab",
                "course":   course_id,
                "section":  section,
                "faculty":  ci.faculty,
                "times":    lab_time,
            })
            idx += 1

    rows.sort(key=lambda r: (r["location"], r["course"], r["section"]))

    if location_filter:
        rows = [r for r in rows if r["location"] == location_filter]

    return rows


def _build_faculty_rows(schedule: list, faculty_filter: str | None = None) -> list[dict]:
    """
    One row per course instance.

    Columns: _key, faculty, course, section, room, lab, times

    If faculty_filter is set, only rows for that faculty are returned.
    Rows are sorted deterministically by (faculty, course, section).
    """
    rows = []
    for idx, ci in enumerate(
        sorted(schedule, key=lambda c: (c.faculty, c.course_str))
    ):
        parts = ci.course_str.rsplit(".", 1)
        course_id = parts[0] if len(parts) == 2 else ci.course_str
        section   = parts[1] if len(parts) == 2 else "01"

        rows.append({
            "_key":    _unique_key("f", idx),
            "faculty": ci.faculty,
            "course":  course_id,
            "section": section,
            "room":    ci.room or "—",
            "lab":     ci.lab  or "—",
            "times":   "; ".join(_format_time(t) for t in ci.times),
        })

    if faculty_filter:
        rows = [r for r in rows if r["faculty"] == faculty_filter]

    return rows


def _location_options(schedule: list) -> list[str]:
    """Sorted list of all unique rooms + labs in the schedule."""
    locations: set[str] = set()
    for ci in schedule:
        if ci.room:
            locations.add(ci.room)
        if ci.lab:
            locations.add(ci.lab)
    return sorted(locations)


def _faculty_options(schedule: list) -> list[str]:
    """Sorted list of all unique faculty names in the schedule."""
    return sorted({ci.faculty for ci in schedule})


# ---------------------------------------------------------------------------
# Table column definitions
# ---------------------------------------------------------------------------

ROOM_COLUMNS = [
    {"name": "location", "label": "Room / Lab",   "field": "location", "sortable": True,  "align": "left"},
    {"name": "type",     "label": "Type",          "field": "type",     "sortable": True,  "align": "center"},
    {"name": "course",   "label": "Course",        "field": "course",   "sortable": True,  "align": "left"},
    {"name": "section",  "label": "Section",       "field": "section",  "sortable": False, "align": "center"},
    {"name": "faculty",  "label": "Faculty",       "field": "faculty",  "sortable": True,  "align": "left"},
    {"name": "times",    "label": "Meeting Times", "field": "times",    "sortable": False, "align": "left"},
]

FACULTY_COLUMNS = [
    {"name": "faculty",  "label": "Faculty",       "field": "faculty",  "sortable": True,  "align": "left"},
    {"name": "course",   "label": "Course",        "field": "course",   "sortable": True,  "align": "left"},
    {"name": "section",  "label": "Section",       "field": "section",  "sortable": False, "align": "center"},
    {"name": "room",     "label": "Room",          "field": "room",     "sortable": True,  "align": "left"},
    {"name": "lab",      "label": "Lab",           "field": "lab",      "sortable": True,  "align": "left"},
    {"name": "times",    "label": "Meeting Times", "field": "times",    "sortable": False, "align": "left"},
]


# ---------------------------------------------------------------------------
# View class
# ---------------------------------------------------------------------------

class ScheduleGUIView:
    """
    GUI pages for schedule generation and display.

    main.py injects dependencies before ui.run():
        ScheduleGUIView.scheduler_model     = scheduler_model
        ScheduleGUIView.schedule_controller = schedule_controller
    """

    schedule_controller = None

    class _ModelDescriptor:
        """Mirrors scheduler_model writes into _state so subprocess handlers can read it."""
        def __get__(self, obj, objtype=None):
            return _state._scheduler_model

        def __set__(self, obj, value):
            _state._scheduler_model = value

    scheduler_model = _ModelDescriptor()

    # -----------------------------------------------------------------------
    # Page: /run_scheduler
    # -----------------------------------------------------------------------

    @ui.page('/run_scheduler')
    @staticmethod
    def run_scheduler():
        """
        Schedule generation page.
        Provides a limit input and Generate button.
        On success, stores results in _state and navigates to /display_schedules.
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)').classes('dark:!bg-black')

        with ui.column().classes('gap-6 items-center w-full max-w-lg mx-auto pt-10'):
            ui.label('Generate Schedules').classes('text-4xl font-bold !text-black dark:!text-white')

            with ui.card().classes('w-full rounded-2xl shadow-md p-6 !bg-white dark:!bg-white'):
                ui.label('Schedule Limit').classes('text-lg font-semibold text-gray-700 mb-1')
                ui.label(
                    'Maximum number of schedules to generate. Higher limits take longer.'
                ).classes('text-sm text-gray-500 mb-4')

                limit_input = ui.number(
                    label='Limit',
                    value=5,
                    min=1,
                    max=500,
                    step=1,
                    format='%d',
                ).classes('w-full').props('color=black label-color=black input-class="!text-black" :dark="false"')

            with ui.card().classes('w-full rounded-2xl shadow-md p-6'):
                ui.label('Optimization Options').classes('text-lg font-semibold text-gray-700 mb-1')
                ui.label(
                    'Select which preferences to optimize for. Leave empty for no optimization.'
                ).classes('text-sm text-gray-500 mb-4')

                _flag_labels = {
                    OptimizerFlags.FACULTY_COURSE: 'Course Preference',
                    OptimizerFlags.FACULTY_ROOM:   'Room Preference',
                    OptimizerFlags.FACULTY_LAB:    'Lab Preference',
                    OptimizerFlags.SAME_ROOM:      'Same Room per Faculty',
                    OptimizerFlags.SAME_LAB:       'Same Lab per Faculty',
                    OptimizerFlags.PACK_ROOMS:     'Pack Rooms',
                    OptimizerFlags.PACK_LABS:      'Pack Labs',
                }

                optimizer_select = ui.select(
                    options={flag: label for flag, label in _flag_labels.items()},
                    multiple=True,
                    value=[],
                    label='Optimization',
                ).classes('w-full').props('use-chips')

            status_label = ui.label('').classes('text-sm text-gray-600 italic')

            with ui.row().classes('gap-4 justify-center w-full'):
                ui.button('Back').props(
                    'rounded outline color=black no-caps text-color=black'
                ).classes('w-36 h-12 text-base dark:!bg-white dark:!text-black').on(
                    'click', lambda: ui.navigate.to('/')
                )
                generate_btn = ui.button('Generate').props(
                    'rounded color=black text-color=white no-caps'
                ).classes('w-36 h-12 text-base')

        async def on_generate():
            model = _state._scheduler_model
            if model is None or getattr(model, "config_model", None) is None:
                status_label.set_text('Error: No configuration loaded.')
                return

            errors = getattr(model, "validate_config", lambda: "")()
            if errors:
                status_label.set_text(f'Configuration invalid:\n{errors}')
                return

            limit = int(limit_input.value or 5)
            model.config_model.config.optimizer_flags = list(optimizer_select.value or [])
            status_label.set_text('Generating schedules… this may take a moment.')
            generate_btn.props('loading disabled')

            try:
                def _run():
                    return list(model.generate_schedules(limit=limit))

                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as pool:
                    schedules = await loop.run_in_executor(pool, _run)

                if not schedules:
                    status_label.set_text('No valid schedules could be generated.')
                    return

                _state.schedules = schedules
                _state.current_index = 0
                ui.navigate.to('/display_schedules')

            except Exception as e:
                status_label.set_text(f'Error: {e}')
            finally:
                generate_btn.props(remove='loading disabled')

        generate_btn.on('click', on_generate)

    # -----------------------------------------------------------------------
    # Page: /display_schedules
    # -----------------------------------------------------------------------

    @ui.page('/display_schedules')
    @staticmethod
    def display_schedules():
        """
        Schedule viewer page.

        - Prev/Next buttons navigate between schedules.
        - "By Room/Lab" tab: filter dropdown + table sorted by location.
        - "By Faculty" tab: filter dropdown + table sorted by faculty name.
        - Both tabs default to showing all rows (no filter selected).
        - Unique _key field prevents Quasar from misidentifying rows on update.
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)').classes('dark:!bg-black')

        # Guard: nothing generated yet
        if not _state.schedules:
            with ui.column().classes('gap-4 items-center w-full pt-20'):
                ui.label('No schedules available.').classes('text-2xl !text-black dark:!text-white')
                ui.label('Please generate schedules first.').classes('text-gray-600')
                ui.button('Go to Generator').props(
                    'rounded color=black text-color=white no-caps'
                ).classes('w-48 h-12 text-base dark:!bg-white dark:!text-black').on(
                    'click', lambda: ui.navigate.to('/run_scheduler')
                )
            return

        total = len(_state.schedules)

        room_filter    = [None]
        faculty_filter = [None]

        with ui.column().classes('gap-4 items-center w-full px-4 pt-6 pb-10'):

            ui.label('Schedule Viewer').classes('text-4xl font-bold !text-black dark:!text-white')

            with ui.row().classes('items-center gap-4 justify-center'):
                prev_btn = ui.button(icon='chevron_left').props('round flat color=black').classes('dark:!text-white')
                index_label = ui.label(
                    f'Schedule {_state.current_index + 1} of {total}'
                ).classes('text-lg font-semibold !text-black dark:!text-white min-w-[160px] text-center')
                next_btn = ui.button(icon='chevron_right').props('round flat color=black').classes('dark:!text-white')

            with ui.card().classes('w-full max-w-7xl rounded-2xl shadow-md'):
                with ui.tabs().classes('!text-black dark:!text-white') as tabs:
                    room_tab    = ui.tab('By Room / Lab')
                    faculty_tab = ui.tab('By Faculty')

                with ui.tab_panels(tabs, value=room_tab).classes('w-full'):

                    with ui.tab_panel(room_tab):
                        with ui.row().classes('items-center gap-3 px-2 pt-2 pb-1'):
                            ui.label('Filter:').classes('text-sm text-gray-500')
                            room_select = ui.select(
                                options=['All'] + _location_options(
                                    _state.schedules[_state.current_index]
                                ),
                                value='All',
                                label='Location',
                            ).classes('min-w-[180px]').props('bg-color=white color=black text-color=black')

                        room_table = ui.table(
                            columns=ROOM_COLUMNS,
                            rows=_build_room_rows(
                                _state.schedules[_state.current_index],
                                location_filter=None,
                            ),
                            row_key='_key',
                            pagination={'rowsPerPage': 50},
                        ).classes('w-full')
                        room_table.props('flat dense')

                    with ui.tab_panel(faculty_tab):
                        with ui.row().classes('items-center gap-3 px-2 pt-2 pb-1'):
                            ui.label('Filter:').classes('text-sm text-gray-500')
                            faculty_select = ui.select(
                                options=['All'] + _faculty_options(
                                    _state.schedules[_state.current_index]
                                ),
                                value='All',
                                label='Faculty',
                            ).classes('min-w-[180px]').props('bg-color=white color=black text-color=black')

                        faculty_table = ui.table(
                            columns=FACULTY_COLUMNS,
                            rows=_build_faculty_rows(
                                _state.schedules[_state.current_index],
                                faculty_filter=None,
                            ),
                            row_key='_key',
                            pagination={'rowsPerPage': 50},
                        ).classes('w-full')
                        faculty_table.props('flat dense')

            with ui.row().classes('gap-4 justify-center'):
                ui.button('Back to Home').props(
                    'rounded outline color=black no-caps text-color=black'
                ).classes('w-44 h-12 text-base dark:!bg-white dark:!text-black').on(
                    'click', lambda: ui.navigate.to('/')
                )
                ui.button('Generate New').props(
                    'rounded color=black text-color=white no-caps'
                ).classes('w-44 h-12 text-base').on(
                    'click', lambda: ui.navigate.to('/run_scheduler')
                )

        def on_room_filter(e):
            val = e.value if e.value != 'All' else None
            room_filter[0] = val
            room_table.rows = _build_room_rows(
                _state.schedules[_state.current_index], location_filter=val
            )
            room_table.update()

        def on_faculty_filter(e):
            val = e.value if e.value != 'All' else None
            faculty_filter[0] = val
            faculty_table.rows = _build_faculty_rows(
                _state.schedules[_state.current_index], faculty_filter=val
            )
            faculty_table.update()

        room_select.on_value_change(on_room_filter)
        faculty_select.on_value_change(on_faculty_filter)

        def _sync_btn_states():
            if _state.current_index == 0:
                prev_btn.props('disabled')
            else:
                prev_btn.props(remove='disabled')
            if _state.current_index == total - 1:
                next_btn.props('disabled')
            else:
                next_btn.props(remove='disabled')

        def _reload_schedule():
            schedule = _state.schedules[_state.current_index]

            room_filter[0]    = None
            faculty_filter[0] = None
            room_select.set_value('All')
            faculty_select.set_value('All')

            room_select.options    = ['All'] + _location_options(schedule)
            faculty_select.options = ['All'] + _faculty_options(schedule)

            room_table.rows    = _build_room_rows(schedule, location_filter=None)
            faculty_table.rows = _build_faculty_rows(schedule, faculty_filter=None)
            room_table.update()
            faculty_table.update()

            index_label.set_text(f'Schedule {_state.current_index + 1} of {total}')
            _sync_btn_states()

        def go_prev():
            if _state.current_index > 0:
                _state.current_index -= 1
                _reload_schedule()

        def go_next():
            if _state.current_index < total - 1:
                _state.current_index += 1
                _reload_schedule()

        prev_btn.on('click', go_prev)
        next_btn.on('click', go_next)
        _sync_btn_states()

    # -----------------------------------------------------------------------
    # DEV ONLY: /test_schedules
    # Bootstraps _state directly from sys.argv config path so the viewer
    # can be tested without needing the /run_scheduler generate button.
    # Remove before final submission.
    # -----------------------------------------------------------------------

    @ui.page('/test_schedules')
    @staticmethod
    def test_schedules():
        import os, sys

        status = ui.label('Generating test schedules…').classes('text-gray-600 italic p-4')

        async def _run():
            try:
                if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
                    status.set_text('Error: no valid config path in sys.argv[1]')
                    return

                from models.config_model import ConfigModel
                from models.scheduler_model import SchedulerModel

                def _generate():
                    model = SchedulerModel(ConfigModel(sys.argv[1]))
                    return list(model.generate_schedules(limit=2))

                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as pool:
                    schedules = await loop.run_in_executor(pool, _generate)

                if not schedules:
                    status.set_text('No schedules generated - check your config.')
                    return

                _state.schedules = schedules
                _state.current_index = 0
                ui.navigate.to('/display_schedules')

            except Exception as e:
                status.set_text(f'Error: {e}')

        ui.timer(0.1, _run, once=True)