# views/schedule_gui_view.py
"""
ScheduleGUIView - Graphical-user interface for schedule interactions

    - _ScheduleState holds only generated schedule data (UI state), not a Model reference.
    - No Model methods are called directly.
    - Config values (limit, config_path) are fetched through the Controller.
    - test_schedules() no longer constructs Models directly.
"""

from typing import Any
import asyncio
from concurrent.futures import ThreadPoolExecutor

from nicegui import ui
from scheduler import OptimizerFlags
from views.gui_theme import GUITheme
from views.gui_utils import require_config


class _ScheduleState:
    _scheduler_model: Any = None
    """
    Holds only transient UI state: generated schedules and current page index.

       Controller when needed.
    """

    def __init__(self):
        self.schedules: list[list] = []
        self.current_index: int = 0


_state = _ScheduleState()

# ---------------------------------------------------------------------------
# Pure helper functions (no model/controller dependencies)
# ---------------------------------------------------------------------------


def _format_time(time_instance) -> str:
    return str(time_instance)


def _unique_key(prefix: str, idx: int) -> str:
    return f"{prefix}_{idx}"


def _build_room_rows(schedule: list, location_filter: str | None = None) -> list[dict]:
    rows = []
    idx = 0
    for ci in sorted(schedule, key=lambda c: (c.course_str,)):
        parts = ci.course_str.rsplit(".", 1)
        course_id = parts[0] if len(parts) == 2 else ci.course_str
        section = parts[1] if len(parts) == 2 else "01"
        lecture_times = "; ".join(
            _format_time(t) for i, t in enumerate(ci.times) if i != ci.lab_index
        )
        lab_time = (
            _format_time(ci.times[ci.lab_index]) if ci.lab_index is not None else ""
        )
        if ci.room:
            rows.append(
                {
                    "_key": _unique_key("r", idx),
                    "location": ci.room,
                    "type": "Room",
                    "course": course_id,
                    "section": section,
                    "faculty": ci.faculty,
                    "times": lecture_times,
                }
            )
            idx += 1
        if ci.lab and ci.lab_index is not None:
            rows.append(
                {
                    "_key": _unique_key("r", idx),
                    "location": ci.lab,
                    "type": "Lab",
                    "course": course_id,
                    "section": section,
                    "faculty": ci.faculty,
                    "times": lab_time,
                }
            )
            idx += 1
    rows.sort(key=lambda r: (r["location"], r["course"], r["section"]))
    if location_filter:
        rows = [r for r in rows if r["location"] == location_filter]
    return rows


def _build_faculty_rows(
    schedule: list, faculty_filter: str | None = None
) -> list[dict]:
    rows = []
    for idx, ci in enumerate(sorted(schedule, key=lambda c: (c.faculty, c.course_str))):
        parts = ci.course_str.rsplit(".", 1)
        course_id = parts[0] if len(parts) == 2 else ci.course_str
        section = parts[1] if len(parts) == 2 else "01"
        rows.append(
            {
                "_key": _unique_key("f", idx),
                "faculty": ci.faculty,
                "course": course_id,
                "section": section,
                "room": ci.room or "—",
                "lab": ci.lab or "—",
                "times": "; ".join(_format_time(t) for t in ci.times),
            }
        )
    if faculty_filter:
        rows = [r for r in rows if r["faculty"] == faculty_filter]
    return rows


def _location_options(schedule: list) -> list[str]:
    locations: set[str] = set()
    for ci in schedule:
        if ci.room:
            locations.add(ci.room)
        if ci.lab:
            locations.add(ci.lab)
    return sorted(locations)


def _faculty_options(schedule: list) -> list[str]:
    return sorted({ci.faculty for ci in schedule})


# ---------------------------------------------------------------------------
# Calendar-style view helper functions
# ---------------------------------------------------------------------------


def _parse_time_string(time_str: str) -> tuple[int, int] | None:
    """Parse time string like 'MON 09:00-10:30' to (hours, minutes) tuple."""
    try:
        time_str = time_str.strip()
        parts = time_str.split(maxsplit=1)
        if len(parts) < 2:
            return None
        time_part = parts[1]
        start_time = time_part.split("-")[0].strip()
        hours, minutes = map(int, start_time.split(":"))
        return (hours, minutes)
    except (ValueError, IndexError, AttributeError):
        return None


def _extract_time_portion(time_str: str) -> str:
    """Extract just the time portion from 'DAY HH:MM-HH:MM' format."""
    try:
        parts = time_str.strip().split(maxsplit=1)
        return parts[1] if len(parts) > 1 else time_str
    except Exception:
        return time_str


def _sort_time_slots(time_slots: set[str]) -> list[str]:
    """Sort time slots chronologically by their start time."""

    def get_sort_key(time_str: str) -> tuple[int, int]:
        parsed = _parse_time_string(time_str)
        return parsed if parsed else (23, 59)

    return sorted(time_slots, key=get_sort_key)


# Color palette system - expandable and consistent
COURSE_COLORS = [
    ("bg-blue-100", "dark:bg-blue-900"),
    ("bg-purple-100", "dark:bg-purple-900"),
    ("bg-pink-100", "dark:bg-pink-900"),
    ("bg-green-100", "dark:bg-green-900"),
    ("bg-yellow-100", "dark:bg-yellow-900"),
    ("bg-cyan-100", "dark:bg-cyan-900"),
    ("bg-indigo-100", "dark:bg-indigo-900"),
    ("bg-orange-100", "dark:bg-orange-900"),
    ("bg-red-100", "dark:bg-red-900"),
    ("bg-teal-100", "dark:bg-teal-900"),
    ("bg-lime-100", "dark:bg-lime-900"),
    ("bg-rose-100", "dark:bg-rose-900"),
]


def _build_color_map(items: list[str]) -> dict[str, tuple[str, str]]:
    """Build a color mapping for items, assigning unique colors sequentially.

    Args:
        items: List of unique faculty or course names

    Returns:
        Dictionary mapping each item to a color tuple
    """
    color_map: dict[str, tuple[str, str]] = {}
    sorted_items = sorted(set(items))

    for idx, item in enumerate(sorted_items):
        color_idx = idx % len(COURSE_COLORS)
        color_map[item] = COURSE_COLORS[color_idx]

    return color_map


def _get_color_classes(base_classes: str | tuple[str, str]) -> str:
    """Convert color tuple into space-separated tailwind classes."""
    if isinstance(base_classes, tuple):
        return f"{base_classes[0]} {base_classes[1]}"
    return base_classes


def _extract_calendar_metadata(schedule: list) -> tuple[list[str], list[str]]:
    """
    Extract unique days and time slots from schedule.
    Returns (sorted_days, sorted_time_slots).
    """
    days_set: set[str] = set()
    time_slots_set: set[str] = set()
    day_order = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4}

    for ci in schedule:
        for time_instance in ci.times:
            time_str = str(time_instance).strip()
            parts = time_str.split(maxsplit=1)
            if len(parts) >= 1:
                day = parts[0].upper()
                if day in day_order:
                    days_set.add(day)
                if len(parts) >= 2:
                    time_slots_set.add(time_str)

    sorted_days = sorted(days_set, key=lambda d: day_order.get(d, 999))
    sorted_time_slots = sorted(time_slots_set)
    return sorted_days, sorted_time_slots


def _build_calendar_grid_by_room(
    schedule: list, location_filter: str | None = None
) -> dict[str, dict[str, dict[str, list]]]:
    """
    Build calendar grid organized by room/lab.
    Returns: {room: {day: {time_slot: [course_info]}}}
    """
    calendar_data: dict[str, dict[str, dict[str, list]]] = {}

    for ci in schedule:
        # Process room course assignments
        if ci.room and (location_filter is None or location_filter == ci.room):
            room = ci.room
            if room not in calendar_data:
                calendar_data[room] = {}

            for i, time_instance in enumerate(ci.times):
                if i == ci.lab_index:
                    continue  # Skip lab times in room section
                time_str = str(time_instance).strip()
                parts = time_str.split(maxsplit=1)
                if len(parts) >= 1:
                    day = parts[0].upper()
                    if day not in calendar_data[room]:
                        calendar_data[room][day] = {}
                    if time_str not in calendar_data[room][day]:
                        calendar_data[room][day][time_str] = []

                    course_code = ci.course_str.rsplit(".", 1)[0]
                    section = (
                        ci.course_str.rsplit(".", 1)[1]
                        if "." in ci.course_str
                        else "01"
                    )
                    calendar_data[room][day][time_str].append(
                        {
                            "course": course_code,
                            "section": section,
                            "faculty": ci.faculty,
                            "type": "Lecture",
                            "full_course_str": ci.course_str,
                        }
                    )

        # Process lab course assignments
        if (
            ci.lab
            and ci.lab_index is not None
            and (location_filter is None or location_filter == ci.lab)
        ):
            lab = ci.lab
            if lab not in calendar_data:
                calendar_data[lab] = {}

            time_instance = ci.times[ci.lab_index]
            time_str = str(time_instance).strip()
            parts = time_str.split(maxsplit=1)
            if len(parts) >= 1:
                day = parts[0].upper()
                if day not in calendar_data[lab]:
                    calendar_data[lab][day] = {}
                if time_str not in calendar_data[lab][day]:
                    calendar_data[lab][day][time_str] = []

                course_code = ci.course_str.rsplit(".", 1)[0]
                section = (
                    ci.course_str.rsplit(".", 1)[1] if "." in ci.course_str else "01"
                )
                calendar_data[lab][day][time_str].append(
                    {
                        "course": course_code,
                        "section": section,
                        "faculty": ci.faculty,
                        "type": "Lab",
                        "full_course_str": ci.course_str,
                    }
                )

    return calendar_data


def _build_calendar_grid_by_faculty(
    schedule: list, faculty_filter: str | None = None
) -> dict[str, dict[str, dict[str, list]]]:
    """
    Build calendar grid organized by faculty.
    Returns: {faculty: {day: {time_slot: [course_info]}}}
    """
    calendar_data: dict[str, dict[str, dict[str, list]]] = {}

    for ci in schedule:
        if faculty_filter and ci.faculty != faculty_filter:
            continue

        faculty = ci.faculty
        if faculty not in calendar_data:
            calendar_data[faculty] = {}

        for i, time_instance in enumerate(ci.times):
            time_str = str(time_instance).strip()
            parts = time_str.split(maxsplit=1)
            if len(parts) >= 1:
                day = parts[0].upper()
                if day not in calendar_data[faculty]:
                    calendar_data[faculty][day] = {}
                if time_str not in calendar_data[faculty][day]:
                    calendar_data[faculty][day][time_str] = []

                course_code = ci.course_str.rsplit(".", 1)[0]
                section = (
                    ci.course_str.rsplit(".", 1)[1] if "." in ci.course_str else "01"
                )
                location = ci.room if i != ci.lab_index else ci.lab
                location_type = "Room" if i != ci.lab_index else "Lab"
                calendar_data[faculty][day][time_str].append(
                    {
                        "course": course_code,
                        "section": section,
                        "location": location or "TBA",
                        "type": location_type,
                        "full_course_str": ci.course_str,
                    }
                )

    return calendar_data


ROOM_COLUMNS = [
    {
        "name": "location",
        "label": "Room / Lab",
        "field": "location",
        "sortable": True,
        "align": "left",
    },
    {
        "name": "type",
        "label": "Type",
        "field": "type",
        "sortable": True,
        "align": "center",
    },
    {
        "name": "course",
        "label": "Course",
        "field": "course",
        "sortable": True,
        "align": "left",
    },
    {
        "name": "section",
        "label": "Section",
        "field": "section",
        "sortable": False,
        "align": "center",
    },
    {
        "name": "faculty",
        "label": "Faculty",
        "field": "faculty",
        "sortable": True,
        "align": "left",
    },
    {
        "name": "times",
        "label": "Meeting Times",
        "field": "times",
        "sortable": False,
        "align": "left",
    },
]

FACULTY_COLUMNS = [
    {
        "name": "faculty",
        "label": "Faculty",
        "field": "faculty",
        "sortable": True,
        "align": "left",
    },
    {
        "name": "course",
        "label": "Course",
        "field": "course",
        "sortable": True,
        "align": "left",
    },
    {
        "name": "section",
        "label": "Section",
        "field": "section",
        "sortable": False,
        "align": "center",
    },
    {
        "name": "room",
        "label": "Room",
        "field": "room",
        "sortable": True,
        "align": "left",
    },
    {"name": "lab", "label": "Lab", "field": "lab", "sortable": True, "align": "left"},
    {
        "name": "times",
        "label": "Meeting Times",
        "field": "times",
        "sortable": False,
        "align": "left",
    },
]


class ScheduleGUIView:
    schedule_model: Any = None
    schedule_controller: Any = None
    pass

    @ui.page("/run_scheduler")
    @staticmethod
    def run_scheduler():
        GUITheme.applyTheming()
        if not require_config(back_url="/"):
            return
        ui.query("body").style("background-color: var(--q-primary)").classes(
            "dark:!bg-black"
        )

        from views.gui_view import GUIView

        if GUIView.controller is None:
            return
        config_limit = GUIView.controller.get_schedule_limit()

        with ui.column().classes("gap-6 items-center w-full max-w-lg mx-auto pt-10"):
            ui.label("Generate Schedules").classes(
                "text-4xl font-bold !text-black dark:!text-white"
            )

            with ui.card().classes(
                "w-full rounded-2xl shadow-md p-6 !bg-white dark:!bg-gray-900"
            ):
                ui.label("Schedule Limit").classes(
                    "text-lg font-semibold !text-gray-700 dark:!text-white mb-1"
                )
                ui.label(f"Config file limit: {config_limit}.").classes(
                    "text-sm !text-gray-500 dark:!text-gray-300 mb-4"
                )
                limit_input = ui.number(
                    label="Limit (overrides config)",
                    value=config_limit,
                    min=1,
                    step=1,
                    format="%d",
                ).classes("w-full")

            with ui.card().classes(
                "w-full rounded-2xl shadow-md p-6 !bg-white dark:!bg-gray-900"
            ):
                ui.label("Optimization Options").classes(
                    "text-lg font-semibold !text-gray-700 dark:!text-white mb-1"
                )
                ui.label(
                    "Select which preferences to optimize for. Leave empty for no optimization."
                ).classes("text-sm !text-gray-500 dark:!text-gray-300 mb-4")
                _flag_labels = {
                    OptimizerFlags.FACULTY_COURSE: "Course Preference",
                    OptimizerFlags.FACULTY_ROOM: "Room Preference",
                    OptimizerFlags.FACULTY_LAB: "Lab Preference",
                    OptimizerFlags.SAME_ROOM: "Same Room per Faculty",
                    OptimizerFlags.SAME_LAB: "Same Lab per Faculty",
                    OptimizerFlags.PACK_ROOMS: "Pack Rooms",
                    OptimizerFlags.PACK_LABS: "Pack Labs",
                }
                (
                    ui.select(
                        options={flag: label for flag, label in _flag_labels.items()},
                        multiple=True,
                        value=[],
                        label="Optimization",
                    )
                    .classes("w-full")
                    .props("use-chips")
                )

            status_label = ui.label("").classes(
                "text-sm !text-gray-600 dark:!text-gray-300 italic"
            )

            with ui.row().classes("gap-4 justify-center w-full"):
                ui.button("Back").props(
                    "rounded outline color=black no-caps text-color=black"
                ).classes("w-36 h-12 text-base dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
                generate_btn = (
                    ui.button("Generate")
                    .props("rounded color=black text-color=white no-caps")
                    .classes("w-36 h-12 text-base dark:!bg-white dark:!text-black")
                )

        async def on_generate():
            if GUIView.controller is None or not GUIView.controller.has_config():
                status_label.set_text("Error: No configuration loaded.")
                return
            if GUIView.controller is None:
                return
            errors = GUIView.controller.validate_schedule_config()
            if errors:
                status_label.set_text(f"Configuration invalid:\n{errors}")
                return
            limit = int(limit_input.value or config_limit)
            status_label.set_text("Generating schedules… this may take a moment.")
            generate_btn.props("loading disabled")
            try:

                def _run():
                    if GUIView.controller is None:
                        return []
                    return GUIView.controller.generate_schedules(limit=limit)

                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as pool:
                    schedules = await loop.run_in_executor(pool, _run)
                if not schedules:
                    status_label.set_text("No valid schedules could be generated.")
                    return
                _state.schedules = schedules
                _state.current_index = 0
                ui.navigate.to("/display_schedules")
            except Exception as e:
                status_label.set_text(f"Error: {e}")
            finally:
                generate_btn.props(remove="loading disabled")

        generate_btn.on("click", on_generate)

    @ui.page("/display_schedules")
    @staticmethod
    def display_schedules():
        GUITheme.applyTheming()
        ui.query("body").style("background-color: var(--q-primary)").classes(
            "dark:!bg-black"
        )
        ui.add_css("""
            .body--dark .schedule-card { background-color: #1a1a1a !important; }
            .q-uploader__title, .q-uploader__subtitle, .q-uploader .q-btn { color: black !important; }
        """)

        from views.gui_view import GUIView

        async def handle_upload(e):
            if GUIView.controller is None:
                return
            controller = GUIView.controller.schedule_controller
            if controller is None:
                ui.notify("Controller not initialized", type="negative")
                return
            try:
                content = await e.file.read()
                schedules = controller.import_schedule_file(e.file.name, content)
                if schedules:
                    _state.schedules += schedules
                    _state.current_index = 0
                    ui.notify(f"Imported {e.file.name}")
                    ui.navigate.to("/display_schedules")
                else:
                    ui.notify(f"No schedules found in {e.file.name}", type="warning")
            except Exception as ex:
                ui.notify(f"Import failed: {ex}", type="negative")

        with ui.dialog() as upload_dialog:
            with ui.card():
                ui.label("Import Schedule")
                ui.upload(
                    label="Select schedule file",
                    multiple=True,
                    auto_upload=True,
                    on_upload=handle_upload,
                ).classes("w-full text-black").style(
                    "color: black !important; background-color: white;"
                )
                ui.button("Close", on_click=upload_dialog.close).style(
                    "color: black !important;"
                )

        export_dialog = ui.dialog()
        with export_dialog:
            with ui.card().classes(
                "w-[400px] rounded-2xl shadow-xl p-6 flex flex-col gap-4"
            ):
                ui.label("Export Schedules").classes(
                    "text-2xl font-bold text-center w-full"
                )
                schedule_select = ui.select(
                    options=[f"Schedule {i + 1}" for i in range(len(_state.schedules))],
                    multiple=True,
                    label="Select schedules",
                ).classes("w-full")
                import os

                config_path = (
                    GUIView.controller.config_path if GUIView.controller else None
                )
                default_name = (
                    os.path.splitext(os.path.basename(config_path))[0]
                    if config_path
                    else "schedules"
                )
                filename_input = ui.input(
                    label="File name", value=default_name
                ).classes("w-full")
                format_select = ui.select(
                    options=["csv", "json"], value="csv", label="Export format"
                ).classes("w-full")

                def do_export():
                    if not schedule_select.value:
                        ui.notify("Please select at least one schedule", type="warning")
                        return
                    indices = [
                        int(x.replace("Schedule ", "")) - 1
                        for x in schedule_select.value
                    ]
                    schedules_to_export = [_state.schedules[i] for i in indices]
                    filename = filename_input.value.strip() or "schedules"
                    if GUIView.controller is None:
                        return
                    data = GUIView.controller.schedule_controller.export_schedules(
                        format_select.value, schedules_to_export
                    )
                    ui.download(data, filename=f"{filename}.{format_select.value}")
                    export_dialog.close()

                with ui.row().classes("w-full justify-end gap-3 pt-2"):
                    ui.button("Cancel").props("outline rounded no-caps").on(
                        "click", export_dialog.close
                    )
                    ui.button("Export").props(
                        "color=black text-color=white rounded no-caps"
                    ).on("click", do_export)

        if not _state.schedules:
            with ui.column().classes("gap-4 items-center w-full pt-20"):
                ui.label("No schedules available.").classes(
                    "text-2xl !text-black dark:!text-white"
                )
                ui.label("Please generate schedules first.").classes("text-gray-600")
                ui.button("Go to Generator").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("w-48 h-12 text-base dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/run_scheduler")
                )
                ui.button("Import Schedules").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("w-48 h-12 text-base dark:!bg-white dark:!text-black").on(
                    "click", upload_dialog.open
                )
            return

        total = len(_state.schedules)
        room_filter = [None]
        faculty_filter = [None]

        with ui.column().classes("gap-4 items-center w-full px-4 pt-6 pb-10"):
            ui.label("Schedule Viewer").classes(
                "text-4xl font-bold !text-black dark:!text-white"
            )

            with ui.row().classes("items-center gap-4 justify-center"):
                prev_btn = (
                    ui.button(icon="chevron_left")
                    .props("round flat color=black")
                    .classes("dark:!text-white")
                )
                index_label = ui.label(
                    f"Schedule {_state.current_index + 1} of {total}"
                ).classes(
                    "text-lg font-semibold !text-black dark:!text-white min-w-[160px] text-center"
                )
                next_btn = (
                    ui.button(icon="chevron_right")
                    .props("round flat color=black")
                    .classes("dark:!text-white")
                )

            with (
                ui.card()
                .style("background-color: white; border: none;")
                .classes("w-full max-w-7xl rounded-2xl shadow-md schedule-card")
            ):
                with (
                    ui.tabs()
                    .style("background-color: transparent;")
                    .classes("!text-black dark:!text-white schedule-tabs") as tabs
                ):
                    calendar_room_tab = ui.tab("Calendar - Room")
                    calendar_faculty_tab = ui.tab("Calendar - Faculty")
                    room_tab = ui.tab("By Room / Lab")
                    faculty_tab = ui.tab("By Faculty")

                with (
                    ui.tab_panels(tabs, value=calendar_room_tab)
                    .style("background-color: transparent;")
                    .classes("w-full")
                ):
                    with ui.tab_panel(room_tab):
                        with ui.row().classes("items-center gap-3 px-2 pt-2 pb-1"):
                            ui.label("Filter:").classes("text-sm text-gray-500")
                            room_select = ui.select(
                                options=["All"]
                                + _location_options(
                                    _state.schedules[_state.current_index]
                                ),
                                value="All",
                                label="Location",
                            ).classes("min-w-[180px]")
                        room_table = ui.table(
                            columns=ROOM_COLUMNS,
                            rows=_build_room_rows(
                                _state.schedules[_state.current_index],
                                location_filter=None,
                            ),
                            row_key="_key",
                            pagination={"rowsPerPage": 50},
                        ).classes("w-full")
                        room_table.props("flat dense")

                    with ui.tab_panel(faculty_tab):
                        with ui.row().classes("items-center gap-3 px-2 pt-2 pb-1"):
                            ui.label("Filter:").classes("text-sm text-gray-500")
                            faculty_select = ui.select(
                                options=["All"]
                                + _faculty_options(
                                    _state.schedules[_state.current_index]
                                ),
                                value="All",
                                label="Faculty",
                            ).classes("min-w-[180px]")
                        faculty_table = ui.table(
                            columns=FACULTY_COLUMNS,
                            rows=_build_faculty_rows(
                                _state.schedules[_state.current_index],
                                faculty_filter=None,
                            ),
                            row_key="_key",
                            pagination={"rowsPerPage": 50},
                        ).classes("w-full")
                        faculty_table.props("flat dense")

                    with ui.tab_panel(calendar_room_tab):
                        with ui.row().classes("items-center gap-3 px-2 pt-2 pb-1"):
                            ui.label("Filter:").classes("text-sm text-gray-500")
                            calendar_room_select = ui.select(
                                options=["All"]
                                + _location_options(
                                    _state.schedules[_state.current_index]
                                ),
                                value="All",
                                label="Location",
                            ).classes("min-w-[180px]")
                        calendar_room_container = ui.column().classes("w-full px-2")

                    with ui.tab_panel(calendar_faculty_tab):
                        with ui.row().classes("items-center gap-3 px-2 pt-2 pb-1"):
                            ui.label("Filter:").classes("text-sm text-gray-500")
                            calendar_faculty_select = ui.select(
                                options=["All"]
                                + _faculty_options(
                                    _state.schedules[_state.current_index]
                                ),
                                value="All",
                                label="Faculty",
                            ).classes("min-w-[180px]")
                        calendar_faculty_container = ui.column().classes("w-full px-2")

            with ui.row().classes("gap-4 justify-center"):
                ui.button("Back to Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("w-44 h-12 text-base dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
                ui.button("Generate New").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("w-44 h-12 text-base dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/run_scheduler")
                )
                ui.button("Export Schedules").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("w-44 h-12 text-base dark:!bg-white dark:!text-black").on(
                    "click", export_dialog.open
                )
                ui.button("Import Schedules").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("w-48 h-12 text-base dark:!bg-white dark:!text-black").on(
                    "click", upload_dialog.open
                )

        def _render_room_calendar(location_filter: str | None = None):
            """Render calendar grid organized by room/lab."""
            calendar_room_container.clear()
            calendar_data = _build_calendar_grid_by_room(
                _state.schedules[_state.current_index], location_filter=location_filter
            )

            if not calendar_data:
                with calendar_room_container:
                    ui.label("No schedule data available.").classes("text-gray-500 p-4")
                return

            days, _ = _extract_calendar_metadata(_state.schedules[_state.current_index])

            # Build color map for all faculty in the schedule
            all_faculty = [ci.faculty for ci in _state.schedules[_state.current_index]]
            faculty_color_map = _build_color_map(all_faculty)

            for location in sorted(calendar_data.keys()):
                # Collect all unique time slots for this location
                time_slots_set: set[str] = set()
                for day_data in calendar_data[location].values():
                    time_slots_set.update(day_data.keys())
                time_slots = _sort_time_slots(time_slots_set)

                with calendar_room_container:
                    with ui.card().classes("w-full p-4 mb-4"):
                        ui.label(location).classes("text-lg font-bold mb-2")

                        # Table headers
                        with ui.row().classes("w-full gap-1"):
                            ui.label("Time").classes(
                                "font-semibold w-40 p-2 bg-gray-100 dark:bg-gray-700"
                            )
                            for day in days:
                                ui.label(day).classes(
                                    "flex-1 font-semibold p-2 bg-gray-100 dark:bg-gray-700 text-center"
                                )

                        # Calendar rows
                        for time_slot in time_slots:
                            time_display = _extract_time_portion(time_slot)
                            with ui.row().classes("w-full gap-1"):
                                ui.label(time_display).classes(
                                    "font-semibold w-40 p-2 bg-gray-50 dark:bg-gray-800 overflow-auto text-sm"
                                )
                                for day in days:
                                    courses = (
                                        calendar_data[location]
                                        .get(day, {})
                                        .get(time_slot, [])
                                    )
                                    with ui.column().classes(
                                        "flex-1 p-1 min-h-20 border border-gray-200 dark:border-gray-700"
                                    ):
                                        for course_info in courses:
                                            # Color by faculty for room view
                                            color_tuple = faculty_color_map.get(
                                                course_info["faculty"], COURSE_COLORS[0]
                                            )
                                            bg_color = _get_color_classes(
                                                f"{color_tuple[0]} {color_tuple[1]}"
                                            )
                                            with ui.card().classes(
                                                f"{bg_color} p-1.5 text-sm w-full"
                                            ):
                                                ui.label(course_info["course"]).classes(
                                                    "font-bold text-sm"
                                                )
                                                ui.label(
                                                    f"Section: {course_info['section']}"
                                                ).classes("text-xs leading-tight")
                                                ui.label(
                                                    f"Instructor: {course_info['faculty']}"
                                                ).classes("text-xs leading-tight")
                                                ui.label(
                                                    f"Type: {course_info['type']}"
                                                ).classes(
                                                    "text-xs italic leading-tight"
                                                )

        def _render_faculty_calendar(faculty_filter: str | None = None):
            """Render calendar grid organized by faculty."""
            calendar_faculty_container.clear()
            calendar_data = _build_calendar_grid_by_faculty(
                _state.schedules[_state.current_index], faculty_filter=faculty_filter
            )

            if not calendar_data:
                with calendar_faculty_container:
                    ui.label("No schedule data available.").classes("text-gray-500 p-4")
                return

            days, _ = _extract_calendar_metadata(_state.schedules[_state.current_index])

            # Build color map for all courses in the schedule
            all_courses = [
                ci.course_str.rsplit(".", 1)[0]
                for ci in _state.schedules[_state.current_index]
            ]
            course_color_map = _build_color_map(all_courses)

            for faculty in sorted(calendar_data.keys()):
                # Collect all unique time slots for this faculty
                time_slots_set: set[str] = set()
                for day_data in calendar_data[faculty].values():
                    time_slots_set.update(day_data.keys())
                time_slots = _sort_time_slots(time_slots_set)

                with calendar_faculty_container:
                    with ui.card().classes("w-full p-4 mb-4"):
                        ui.label(faculty).classes("text-lg font-bold mb-2")

                        # Table headers
                        with ui.row().classes("w-full gap-1"):
                            ui.label("Time").classes(
                                "font-semibold w-40 p-2 bg-gray-100 dark:bg-gray-700"
                            )
                            for day in days:
                                ui.label(day).classes(
                                    "flex-1 font-semibold p-2 bg-gray-100 dark:bg-gray-700 text-center"
                                )
                        # Calendar rows
                        for time_slot in time_slots:
                            time_display = _extract_time_portion(time_slot)
                            with ui.row().classes("w-full gap-1"):
                                ui.label(time_display).classes(
                                    "font-semibold w-40 p-2 bg-gray-50 dark:bg-gray-800 overflow-auto text-sm"
                                )
                                for day in days:
                                    courses = (
                                        calendar_data[faculty]
                                        .get(day, {})
                                        .get(time_slot, [])
                                    )
                                    with ui.column().classes(
                                        "flex-1 p-1 min-h-20 border border-gray-200 dark:border-gray-700"
                                    ):
                                        for course_info in courses:
                                            # Color by course code for faculty view
                                            color_tuple = course_color_map.get(
                                                course_info["course"], COURSE_COLORS[0]
                                            )
                                            bg_color = _get_color_classes(
                                                f"{color_tuple[0]} {color_tuple[1]}"
                                            )
                                            with ui.card().classes(
                                                f"{bg_color} p-1.5 text-sm w-full"
                                            ):
                                                ui.label(course_info["course"]).classes(
                                                    "font-bold text-sm"
                                                )
                                                ui.label(
                                                    f"Section: {course_info['section']}"
                                                ).classes("text-xs leading-tight")
                                                ui.label(
                                                    f"Location: {course_info['location']}"
                                                ).classes("text-xs leading-tight")
                                                ui.label(
                                                    f"Type: {course_info['type']}"
                                                ).classes(
                                                    "text-xs italic leading-tight"
                                                )

        def on_room_filter(e):
            val = e.value if e.value != "All" else None
            room_filter[0] = val
            room_table.rows = _build_room_rows(
                _state.schedules[_state.current_index], location_filter=val
            )
            room_table.update()

        def on_faculty_filter(e):
            val = e.value if e.value != "All" else None
            faculty_filter[0] = val
            faculty_table.rows = _build_faculty_rows(
                _state.schedules[_state.current_index], faculty_filter=val
            )
            faculty_table.update()

        def on_calendar_room_filter(e):
            val = e.value if e.value != "All" else None
            _render_room_calendar(location_filter=val)

        def on_calendar_faculty_filter(e):
            val = e.value if e.value != "All" else None
            _render_faculty_calendar(faculty_filter=val)

        room_select.on_value_change(on_room_filter)
        faculty_select.on_value_change(on_faculty_filter)
        calendar_room_select.on_value_change(on_calendar_room_filter)
        calendar_faculty_select.on_value_change(on_calendar_faculty_filter)

        def _sync_btn_states():
            if _state.current_index == 0:
                prev_btn.props("disabled")
            else:
                prev_btn.props(remove="disabled")
            if _state.current_index == total - 1:
                next_btn.props("disabled")
            else:
                next_btn.props(remove="disabled")

        def _reload_schedule():
            schedule = _state.schedules[_state.current_index]
            room_filter[0] = None
            faculty_filter[0] = None
            room_select.set_value("All")
            faculty_select.set_value("All")
            calendar_room_select.set_value("All")
            calendar_faculty_select.set_value("All")
            room_select.options = ["All"] + _location_options(schedule)
            faculty_select.options = ["All"] + _faculty_options(schedule)
            calendar_room_select.options = ["All"] + _location_options(schedule)
            calendar_faculty_select.options = ["All"] + _faculty_options(schedule)
            room_table.rows = _build_room_rows(schedule, location_filter=None)
            faculty_table.rows = _build_faculty_rows(schedule, faculty_filter=None)
            _render_room_calendar(location_filter=None)
            _render_faculty_calendar(faculty_filter=None)
            room_table.update()
            faculty_table.update()
            index_label.set_text(f"Schedule {_state.current_index + 1} of {total}")
            _sync_btn_states()

        def go_prev():
            if _state.current_index > 0:
                _state.current_index -= 1
                _reload_schedule()

        def go_next():
            if _state.current_index < total - 1:
                _state.current_index += 1
                _reload_schedule()

        prev_btn.on("click", go_prev)
        next_btn.on("click", go_next)
        _reload_schedule()

    @ui.page("/test_schedules")
    @staticmethod
    def test_schedules():
        """Development test page — generates schedules from the CLI config path."""
        import os
        import sys

        status = ui.label("Generating test schedules…").classes(
            "text-gray-600 italic p-4"
        )

        async def _run():
            try:
                if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
                    status.set_text("Error: no valid config path in sys.argv[1]")
                    return
                from views.gui_view import GUIView

                #    Load config first if not already loaded.
                if GUIView.controller is None:
                    return
                if GUIView.controller.config_path != sys.argv[1]:
                    ok, msg = GUIView.controller.load_config(sys.argv[1])
                    if not ok:
                        status.set_text(f"Config load failed: {msg}")
                        return

                def _generate():
                    if GUIView.controller is None:
                        return []
                    return GUIView.controller.generate_schedules(limit=2)

                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as pool:
                    schedules = await loop.run_in_executor(pool, _generate)
                if not schedules:
                    status.set_text("No schedules generated - check your config.")
                    return
                _state.schedules = schedules
                _state.current_index = 0
                ui.navigate.to("/display_schedules")
            except Exception as e:
                status.set_text(f"Error: {e}")

        ui.timer(0.1, _run, once=True)
