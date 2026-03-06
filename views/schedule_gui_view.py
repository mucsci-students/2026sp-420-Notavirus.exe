# views/schedule_gui_view.py
"""
ScheduleGUIView - Graphical-user interface for schedule interactions
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor

from nicegui import ui
from scheduler import OptimizerFlags
from views.gui_theme import GUITheme
from views.gui_utils import require_config


class _ScheduleState:
    """Shared state: generated schedules + scheduler model reference."""
    def __init__(self):
        self.schedules: list[list] = []
        self.current_index: int = 0
        self._scheduler_model = None

_state = _ScheduleState()

def _format_time(time_instance) -> str:
    """
    Formats a time instance as a string.

    Parameters:
        time_instance: A time object to format.
    Returns:
        str: String representation of the time instance.
    """
    return str(time_instance)

def _unique_key(prefix: str, idx: int) -> str:
    """
    Generates a unique key string for table row identification.

    Parameters:
        prefix (str): A short string prefix (e.g. 'r' for room, 'f' for faculty).
        idx (int): The row index.
    Returns:
        str: A unique key in the format 'prefix_idx'.
    """
    return f"{prefix}_{idx}"

def _build_room_rows(schedule: list, location_filter: str | None = None) -> list[dict]:
    """
    Builds a list of row dicts for the room/lab table view.

    Each course instance contributes one room row and optionally one lab row.
    Rows are sorted by location, then course, then section. An optional
    location filter narrows the result to a single room or lab.

    Parameters:
        schedule (list): List of course instance objects for the current schedule.
        location_filter (str | None): If provided, only rows matching this location are returned.
    Returns:
        list[dict]: List of row dicts with keys: _key, location, type, course, section, faculty, times.
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
    Builds a list of row dicts for the faculty table view.

    Rows are sorted by faculty name then course. An optional faculty filter
    narrows the result to a single faculty member.

    Parameters:
        schedule (list): List of course instance objects for the current schedule.
        faculty_filter (str | None): If provided, only rows matching this faculty are returned.
    Returns:
        list[dict]: List of row dicts with keys: _key, faculty, course, section, room, lab, times.
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
    """
    Returns a sorted list of unique room and lab names in the schedule.

    Parameters:
        schedule (list): List of course instance objects for the current schedule.
    Returns:
        list[str]: Sorted list of location name strings.
    """
    locations: set[str] = set()
    for ci in schedule:
        if ci.room:
            locations.add(ci.room)
        if ci.lab:
            locations.add(ci.lab)
    return sorted(locations)

def _faculty_options(schedule: list) -> list[str]:
    """
    Returns a sorted list of unique faculty names in the schedule.

    Parameters:
        schedule (list): List of course instance objects for the current schedule.
    Returns:
        list[str]: Sorted list of faculty name strings.
    """
    return sorted({ci.faculty for ci in schedule})

def download_csv():
    """
    Exports all current schedules as a CSV file and triggers a browser download.

    Parameters:
        None
    Returns:
        None
    """
    data = ScheduleGUIView.schedule_controller.export_schedules("csv", _state.schedules)
    ui.download(data, filename="schedules.csv")

def download_json():
    """
    Exports all current schedules as a JSON file and triggers a browser download.

    Parameters:
        None
    Returns:
        None
    """
    data = ScheduleGUIView.schedule_controller.export_schedules("json", _state.schedules)
    ui.download(data, filename="schedules.json")

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


class ScheduleGUIView:
    schedule_controller = None

    class _ModelDescriptor:
        def __get__(self, obj, objtype=None):
            return _state._scheduler_model
        def __set__(self, obj, value):
            _state._scheduler_model = value

    scheduler_model = _ModelDescriptor()

    @ui.page('/run_scheduler')
    @staticmethod
    def run_scheduler():
        GUITheme.applyTheming()
        if not require_config(back_url='/'):
            return
        ui.query('body').style('background-color: var(--q-primary)').classes('dark:!bg-black')

        config_limit = 100
        model = _state._scheduler_model
        if model is not None and getattr(model, "config_model", None) is not None:
            config_limit = model.config_model.config.limit

        with ui.column().classes('gap-6 items-center w-full max-w-lg mx-auto pt-10'):
            ui.label('Generate Schedules').classes('text-4xl font-bold !text-black dark:!text-white')

            with ui.card().classes('w-full rounded-2xl shadow-md p-6 !bg-white dark:!bg-gray-900'):
                ui.label('Schedule Limit').classes('text-lg font-semibold !text-gray-700 dark:!text-white mb-1')
                ui.label(
                    f'Config file limit: {config_limit}.'
                ).classes('text-sm !text-gray-500 dark:!text-gray-300 mb-4')
                limit_input = ui.number(
                    label='Limit (overrides config)',
                    value=config_limit,
                    min=1,
                    step=1,
                    format='%d',
                ).classes('w-full')

            with ui.card().classes('w-full rounded-2xl shadow-md p-6 !bg-white dark:!bg-gray-900'):
                ui.label('Optimization Options').classes('text-lg font-semibold !text-gray-700 dark:!text-white mb-1')
                ui.label(
                    'Select which preferences to optimize for. Leave empty for no optimization.'
                ).classes('text-sm !text-gray-500 dark:!text-gray-300 mb-4')

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

            status_label = ui.label('').classes('text-sm !text-gray-600 dark:!text-gray-300 italic')

            with ui.row().classes('gap-4 justify-center w-full'):
                ui.button('Back').props(
                    'rounded outline color=black no-caps text-color=black'
                ).classes('w-36 h-12 text-base dark:!bg-white dark:!text-black').on(
                    'click', lambda: ui.navigate.to('/')
                )
                generate_btn = ui.button('Generate').props(
                    'rounded color=black text-color=white no-caps'
                ).classes('w-36 h-12 text-base dark:!bg-white dark:!text-black')

        async def on_generate():
            """
            Handles the Generate button click.

            Validates configuration, runs the scheduler asynchronously in a
            thread pool, stores results in shared state, and navigates to the
            display page. Updates the status label on error.

            Parameters:
                None
            Returns:
                None
            """
            model = _state._scheduler_model
            if model is None or getattr(model, "config_model", None) is None:
                status_label.set_text('Error: No configuration loaded.')
                return
            errors = getattr(model, "validate_config", lambda: "")()
            if errors:
                status_label.set_text(f'Configuration invalid:\n{errors}')
                return
            limit = int(limit_input.value or config_limit)
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

    @ui.page('/display_schedules')
    @staticmethod
    def display_schedules():
        """
        Displays the generated schedules in a tabbed viewer.

        Shows schedules in two views: by Room/Lab and by Faculty. Supports
        pagination through multiple schedules, per-column filtering, CSV/JSON
        export of selected schedules, and importing schedule files.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)').classes('dark:!bg-black')
        ui.add_css('''
            .body--dark .schedule-card {
                background-color: #1a1a1a !important;
            }
        ''')

        async def handle_upload(e):
            """
            Handles an uploaded schedule file.

            Reads the file content, delegates parsing to the schedule controller,
            and reloads the display page with the imported schedules on success.

            Parameters:
                e: Upload event containing the file name and file-like object.
            Returns:
                None
            """
            if ScheduleGUIView.schedule_controller is None:
                ui.notify('Controller not initialized', type='negative')
                return
            try:
                content = await e.file.read()
                schedules = ScheduleGUIView.schedule_controller.import_schedule_file(
                    e.file.name, content
                )
                if schedules:
                    _state.schedules = schedules
                    _state.current_index = 0
                    ui.notify(f'Imported {e.file.name}')
                    ui.navigate.to('/display_schedules')
                else:
                    ui.notify(f'No schedules found in {e.file.name}', type='warning')
            except Exception as ex:
                ui.notify(f'Import failed: {ex}', type='negative')
                print({ex})

        upload = ui.upload(multiple=True, auto_upload=True).props('hidden')
        upload.on_upload(handle_upload)

        export_dialog = ui.dialog()
        with export_dialog:
            with ui.card().classes("w-[400px] rounded-2xl shadow-xl p-6 flex flex-col gap-4"):
                ui.label("Export Schedules").classes("text-2xl font-bold text-center w-full")
                schedule_select = ui.select(
                    options=[f"Schedule {i+1}" for i in range(len(_state.schedules))],
                    multiple=True,
                    label="Select schedules"
                ).classes("w-full")
                filename_input = ui.input(label="File name", value="schedules").classes("w-full")
                format_select = ui.select(options=["csv", "json"], value="csv", label="Export format").classes("w-full")
                result_label = ui.label("").classes("text-sm text-gray-500 italic text-center w-full")

                def do_export():
                    """
                    Exports the selected schedules to the chosen file format and triggers a download.

                    Parameters:
                        None
                    Returns:
                        None
                    """
                    if not schedule_select.value:
                        ui.notify("Please select at least one schedule", type="warning")
                        return
                    indices = [int(x.replace("Schedule ", "")) - 1 for x in schedule_select.value]
                    schedules_to_export = [_state.schedules[i] for i in indices]
                    filename = filename_input.value.strip() or "schedules"
                    data = ScheduleGUIView.schedule_controller.export_schedules(
                        format_select.value, schedules_to_export
                    )
                    ui.download(data, filename=f"{filename}.{format_select.value}")
                    export_dialog.close()

                with ui.row().classes("w-full justify-end gap-3 pt-2"):
                    ui.button("Cancel").props("outline rounded no-caps").on("click", export_dialog.close)
                    ui.button("Export").props("color=black text-color=white rounded no-caps").on("click", do_export)

        if not _state.schedules:
            with ui.column().classes('gap-4 items-center w-full pt-20'):
                ui.label('No schedules available.').classes('text-2xl !text-black dark:!text-white')
                ui.label('Please generate schedules first.').classes('text-gray-600')
                ui.button('Go to Generator').props('rounded color=black text-color=white no-caps').classes(
                    'w-48 h-12 text-base dark:!bg-white dark:!text-black'
                ).on('click', lambda: ui.navigate.to('/run_scheduler'))
                ui.button('Import Schedules').props('rounded color=black text-color=white no-caps').classes(
                    'w-48 h-12 text-base'
                ).on('click', lambda: upload.run_method('pickFiles'))
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

            with ui.card().style('background-color: white; border: none;').classes('w-full max-w-7xl rounded-2xl shadow-md schedule-card'):
                with ui.tabs().style('background-color: transparent;').classes('!text-black dark:!text-white schedule-tabs') as tabs:
                    room_tab    = ui.tab('By Room / Lab')
                    faculty_tab = ui.tab('By Faculty')

                with ui.tab_panels(tabs, value=room_tab).style('background-color: transparent;').classes('w-full'):
                    with ui.tab_panel(room_tab):
                        with ui.row().classes('items-center gap-3 px-2 pt-2 pb-1'):
                            ui.label('Filter:').classes('text-sm text-gray-500')
                            room_select = ui.select(
                                options=['All'] + _location_options(_state.schedules[_state.current_index]),
                                value='All',
                                label='Location',
                            ).classes('min-w-[180px]')
                        room_table = ui.table(
                            columns=ROOM_COLUMNS,
                            rows=_build_room_rows(_state.schedules[_state.current_index], location_filter=None),
                            row_key='_key',
                            pagination={'rowsPerPage': 50},
                        ).classes('w-full')
                        room_table.props('flat dense')

                    with ui.tab_panel(faculty_tab):
                        with ui.row().classes('items-center gap-3 px-2 pt-2 pb-1'):
                            ui.label('Filter:').classes('text-sm text-gray-500')
                            faculty_select = ui.select(
                                options=['All'] + _faculty_options(_state.schedules[_state.current_index]),
                                value='All',
                                label='Faculty',
                            ).classes('min-w-[180px]')
                        faculty_table = ui.table(
                            columns=FACULTY_COLUMNS,
                            rows=_build_faculty_rows(_state.schedules[_state.current_index], faculty_filter=None),
                            row_key='_key',
                            pagination={'rowsPerPage': 50},
                        ).classes('w-full')
                        faculty_table.props('flat dense')

            with ui.row().classes('gap-4 justify-center'):
                ui.button('Back to Home').props('rounded color=black text-color=white no-caps').classes(
                    'w-44 h-12 text-base dark:!bg-white dark:!text-black'
                ).on('click', lambda: ui.navigate.to('/'))
                ui.button('Generate New').props('rounded color=black text-color=white no-caps').classes(
                    'w-44 h-12 text-base dark:!bg-white dark:!text-black'
                ).on('click', lambda: ui.navigate.to('/run_scheduler'))
                ui.button('Export Schedules').props('rounded color=black text-color=white no-caps').classes(
                    'w-44 h-12 text-base dark:!bg-white dark:!text-black'
                ).on('click', export_dialog.open)
                ui.button('Import Schedules').props('rounded color=black text-color=white no-caps').classes(
                    'w-48 h-12 text-base dark:!bg-white dark:!text-black'
                ).on('click', lambda: upload.run_method('pickFiles'))

        def on_room_filter(e):
            """
            Filters the room table by the selected location.

            Parameters:
                e: Select change event containing the new value.
            Returns:
                None
            """
            val = e.value if e.value != 'All' else None
            room_filter[0] = val
            room_table.rows = _build_room_rows(_state.schedules[_state.current_index], location_filter=val)
            room_table.update()

        def on_faculty_filter(e):
            """
            Filters the faculty table by the selected faculty member.

            Parameters:
                e: Select change event containing the new value.
            Returns:
                None
            """
            val = e.value if e.value != 'All' else None
            faculty_filter[0] = val
            faculty_table.rows = _build_faculty_rows(_state.schedules[_state.current_index], faculty_filter=val)
            faculty_table.update()

        room_select.on_value_change(on_room_filter)
        faculty_select.on_value_change(on_faculty_filter)

        def _sync_btn_states():
            """
            Enables or disables the prev/next navigation buttons based on current index.

            Parameters:
                None
            Returns:
                None
            """
            if _state.current_index == 0:
                prev_btn.props('disabled')
            else:
                prev_btn.props(remove='disabled')
            if _state.current_index == total - 1:
                next_btn.props('disabled')
            else:
                next_btn.props(remove='disabled')

        def _reload_schedule():
            """
            Reloads table data and filter options for the current schedule index.

            Parameters:
                None
            Returns:
                None
            """
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
            """
            Navigates to the previous schedule if available.

            Parameters:
                None
            Returns:
                None
            """
            if _state.current_index > 0:
                _state.current_index -= 1
                _reload_schedule()

        def go_next():
            """
            Navigates to the next schedule if available.

            Parameters:
                None
            Returns:
                None
            """
            if _state.current_index < total - 1:
                _state.current_index += 1
                _reload_schedule()

        prev_btn.on('click', go_prev)
        next_btn.on('click', go_next)
        _sync_btn_states()

    @ui.page('/test_schedules')
    @staticmethod
    def test_schedules():
        """
        Displays a test schedule generation page for development use.

        Reads a config path from sys.argv[1], generates up to 2 schedules,
        and navigates to the display page on success.

        Parameters:
            None
        Returns:
            None
        """
        import os, sys
        status = ui.label('Generating test schedules…').classes('text-gray-600 italic p-4')

        async def _run():
            """
            Asynchronously generates test schedules from the CLI config path.

            Parameters:
                None
            Returns:
                None
            """
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