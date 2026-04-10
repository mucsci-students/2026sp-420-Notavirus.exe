# views/schedule_gui_view.py
"""
ScheduleGUIView - Graphical-user interface for schedule interactions

    - _ScheduleState holds only generated schedule data (UI state), not a Model reference.
    - No Model methods are called directly.
    - Config values (limit, config_path) are fetched through the Controller.
    - test_schedules() no longer constructs Models directly.

Sprint 3 additions:
  - Progress bar on /run_scheduler (SchedulerFacade drives percent updates)
  - SchedulerFacade (Facade design pattern) replaces the raw model call

Sprint 4 additions:
  - Clickable course blocks on both calendar views open a detail dialog
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any
import threading as _threading


from nicegui import ui
from scheduler import OptimizerFlags

from scheduler_facade import SchedulerFacade
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
        self.is_generating: bool = False
        self.progress_pct: int = 0
        self.progress_msg: str = ""
        self.stop_event = None
        self.generation_error: str | None = None
        self.pending_navigate: bool = False
        self.generation_limit: int = 0


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


def _extract_time_range(
    time_str: str,
) -> tuple[tuple[int, int], tuple[int, int]] | None:
    """Parse time string like 'MON 09:00-10:30' to ((start_h, start_m), (end_h, end_m))."""
    try:
        time_str = time_str.strip()
        parts = time_str.split(maxsplit=1)
        if len(parts) < 2:
            return None
        time_part = parts[1]
        start_str, end_str = time_part.split("-")
        start_h, start_m = map(int, start_str.strip().split(":"))
        end_h, end_m = map(int, end_str.strip().split(":"))
        return ((start_h, start_m), (end_h, end_m))
    except (ValueError, IndexError, AttributeError):
        return None


def _generate_hourly_slots(schedule: list) -> list[str]:
    """Generate hourly time slots based on course times in schedule.

    Returns list of slots like "09:00-10:00", "10:00-11:00", etc.
    """
    min_hour = 23
    max_hour = 0

    for ci in schedule:
        for time_instance in ci.times:
            time_str = str(time_instance).strip()
            time_range = _extract_time_range(time_str)
            if time_range:
                start_h, _ = time_range[0]
                end_h, end_m = time_range[1]
                min_hour = min(min_hour, start_h)
                max_hour = max(max_hour, end_h)

    if min_hour == 23:  # No valid times found
        min_hour = 8
        max_hour = 20

    slots = []
    for hour in range(min_hour, max_hour):
        slots.append(f"{hour:02d}:00-{hour + 1:02d}:00")

    return slots


def _extract_time_portion(time_str: str) -> str:
    """Extract just the time portion from 'DAY HH:MM-HH:MM' format."""
    try:
        parts = time_str.strip().split(maxsplit=1)
        return parts[1] if len(parts) > 1 else time_str
    except Exception:
        return time_str


def _extract_day(time_str: str) -> str | None:
    """Extract day from 'DAY HH:MM-HH:MM' format."""
    try:
        parts = time_str.strip().split(maxsplit=1)
        return parts[0].upper() if len(parts) > 0 else None
    except Exception:
        return None


def _time_overlaps_hour(course_time_str: str, hour_slot: str) -> bool:
    """Check if a course time overlaps with an hourly slot."""
    try:
        course_range = _extract_time_range(course_time_str)
        slot_range = _extract_time_range("DAY " + hour_slot)

        if not course_range or not slot_range:
            return False

        (c_start_h, c_start_m), (c_end_h, c_end_m) = course_range
        (s_start_h, s_start_m), (s_end_h, s_end_m) = slot_range

        c_start_min = c_start_h * 60 + c_start_m
        c_end_min = c_end_h * 60 + c_end_m
        s_start_min = s_start_h * 60 + s_start_m
        s_end_min = s_end_h * 60 + s_end_m

        return c_start_min < s_end_min and c_end_min > s_start_min
    except Exception:
        return False


def _calculate_course_span(course_time_str: str, hourly_slots: list[str]) -> int:
    """Calculate how many hourly slots a course spans."""
    span = 0
    for hour_slot in hourly_slots:
        if _time_overlaps_hour(course_time_str, hour_slot):
            span += 1
    return span


def _calculate_course_duration_minutes(course_time_str: str) -> int:
    """Calculate the actual duration of a course in minutes."""
    time_range = _extract_time_range(course_time_str)
    if not time_range:
        return 60

    (start_h, start_m), (end_h, end_m) = time_range
    start_total_min = start_h * 60 + start_m
    end_total_min = end_h * 60 + end_m

    duration = end_total_min - start_total_min
    return max(duration, 50)


def _sort_time_slots(time_slots: set[str] | list[str]) -> list[str]:
    """Sort time slots chronologically by their start time."""

    def get_sort_key(time_str: str) -> tuple[int, int]:
        parsed = _parse_time_string("DAY " + time_str)
        return parsed if parsed else (23, 59)

    return sorted(time_slots, key=get_sort_key)


def _get_full_course_info(schedule: list, course_str: str, faculty: str) -> dict:
    """Gather all details for a course from the schedule for the detail dialog."""
    for ci in schedule:
        if ci.course_str == course_str and ci.faculty == faculty:
            parts = ci.course_str.rsplit(".", 1)
            course_id = parts[0] if len(parts) == 2 else ci.course_str
            section = parts[1] if len(parts) == 2 else "01"
            lecture_times = [
                str(t) for i, t in enumerate(ci.times) if i != ci.lab_index
            ]
            lab_time = str(ci.times[ci.lab_index]) if ci.lab_index is not None else None
            return {
                "course": course_id,
                "section": section,
                "faculty": ci.faculty,
                "room": ci.room or "—",
                "lab": ci.lab or "—",
                "lecture_times": lecture_times,
                "lab_time": lab_time,
            }
    return {}


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
    """Build a color mapping for items, assigning unique colors sequentially."""
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
    Extract unique days and hourly time slots from schedule.
    Returns (sorted_days, sorted_hourly_time_slots).
    """
    days_set: set[str] = set()
    day_order = {"MON": 0, "TUE": 1, "WED": 2, "THU": 3, "FRI": 4}

    for ci in schedule:
        for time_instance in ci.times:
            time_str = str(time_instance).strip()
            parts = time_str.split(maxsplit=1)
            if len(parts) >= 1:
                day = parts[0].upper()
                if day in day_order:
                    days_set.add(day)

    sorted_days = sorted(days_set, key=lambda d: day_order.get(d, 999))
    hourly_slots = _generate_hourly_slots(schedule)
    return sorted_days, hourly_slots


def _build_calendar_grid_by_room(
    schedule: list, location_filter: str | None = None
) -> dict[str, dict[str, dict[str, list]]]:
    """
    Build calendar grid organized by room/lab with hourly time slots.
    Returns: {room: {day: {time_slot: [course_info]}}}
    """
    calendar_data: dict[str, dict[str, dict[str, list]]] = {}
    hourly_slots = _generate_hourly_slots(schedule)

    for ci in schedule:
        if ci.room and (location_filter is None or location_filter == ci.room):
            room = ci.room
            if room not in calendar_data:
                calendar_data[room] = {}

            for i, time_instance in enumerate(ci.times):
                if i == ci.lab_index:
                    continue
                time_str = str(time_instance).strip()
                day = _extract_day(time_str)

                if not day:
                    continue

                if day not in calendar_data[room]:
                    calendar_data[room][day] = {}

                course_code = ci.course_str.rsplit(".", 1)[0]
                section = (
                    ci.course_str.rsplit(".", 1)[1] if "." in ci.course_str else "01"
                )

                course_info = {
                    "course": course_code,
                    "section": section,
                    "faculty": ci.faculty,
                    "type": "Lecture",
                    "full_course_str": ci.course_str,
                }

                for hour_slot in hourly_slots:
                    if _time_overlaps_hour(time_str, hour_slot):
                        if hour_slot not in calendar_data[room][day]:
                            calendar_data[room][day][hour_slot] = []
                        calendar_data[room][day][hour_slot].append(course_info)

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
            day = _extract_day(time_str)

            if not day:
                continue

            if day not in calendar_data[lab]:
                calendar_data[lab][day] = {}

            course_code = ci.course_str.rsplit(".", 1)[0]
            section = ci.course_str.rsplit(".", 1)[1] if "." in ci.course_str else "01"

            course_info = {
                "course": course_code,
                "section": section,
                "faculty": ci.faculty,
                "type": "Lab",
                "full_course_str": ci.course_str,
            }

            for hour_slot in hourly_slots:
                if _time_overlaps_hour(time_str, hour_slot):
                    if hour_slot not in calendar_data[lab][day]:
                        calendar_data[lab][day][hour_slot] = []
                    calendar_data[lab][day][hour_slot].append(course_info)

    return calendar_data


def _build_calendar_grid_by_faculty(
    schedule: list, faculty_filter: str | None = None
) -> dict[str, dict[str, dict[str, list]]]:
    """
    Build calendar grid organized by faculty with hourly time slots.
    Returns: {faculty: {day: {time_slot: [course_info]}}}
    """
    calendar_data: dict[str, dict[str, dict[str, list]]] = {}
    hourly_slots = _generate_hourly_slots(schedule)

    for ci in schedule:
        if faculty_filter and ci.faculty != faculty_filter:
            continue

        faculty = ci.faculty
        if faculty not in calendar_data:
            calendar_data[faculty] = {}

        for i, time_instance in enumerate(ci.times):
            time_str = str(time_instance).strip()
            day = _extract_day(time_str)

            if not day:
                continue

            if day not in calendar_data[faculty]:
                calendar_data[faculty][day] = {}

            course_code = ci.course_str.rsplit(".", 1)[0]
            section = ci.course_str.rsplit(".", 1)[1] if "." in ci.course_str else "01"
            location = ci.room if i != ci.lab_index else ci.lab
            location_type = "Room" if i != ci.lab_index else "Lab"

            course_info = {
                "course": course_code,
                "section": section,
                "location": location or "TBA",
                "type": location_type,
                "full_course_str": ci.course_str,
            }

            for hour_slot in hourly_slots:
                if _time_overlaps_hour(time_str, hour_slot):
                    if hour_slot not in calendar_data[faculty][day]:
                        calendar_data[faculty][day][hour_slot] = []
                    calendar_data[faculty][day][hour_slot].append(course_info)

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
    def run_scheduler():  # noqa: C901
        GUITheme.applyTheming()
        ui.add_css("""
            .body--dark .q-linear-progress__model { background: white !important; }
            .body--dark .q-linear-progress__track { background: rgba(255,255,255,0.2) !important; }
        """)
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
                        options=dict(_flag_labels.items()),
                        multiple=True,
                        value=[],
                        label="Optimization",
                    )
                    .classes("w-full")
                    .props("use-chips")
                )

            # ----------------------------------------------------------------
            # Progress bar (hidden until generation starts)
            # ----------------------------------------------------------------
            progress_card = ui.card().classes(
                "w-full rounded-2xl shadow-md p-6 !bg-white dark:!bg-gray-900 gap-3"
            )
            progress_card.set_visibility(_state.is_generating)

            with progress_card:
                progress_message = ui.label(_state.progress_msg).classes(
                    "text-sm !text-gray-600 dark:!text-gray-300 italic"
                )
                cancel_btn = (
                    ui.button("Cancel")
                    .props("rounded outline color=red no-caps")
                    .classes("w-28 h-9 text-sm self-end")
                )
                progress_bar = ui.linear_progress(
                    value=_state.progress_pct / 100,
                    size="12px",
                    color="black",
                    show_value=False,
                ).classes("w-full rounded-full")
                progress_label = ui.label(f"{_state.progress_pct}%").classes(
                    "text-xs !text-gray-400 dark:!text-white text-right w-full"
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

        if _state.is_generating:
            generate_btn.props("loading disabled")

        async def _attach_poll():  # noqa: C901
            while _state.is_generating:
                try:
                    progress_bar.set_value(_state.progress_pct / 100)
                    progress_label.set_text(f"{_state.progress_pct}%")
                    progress_message.set_text(_state.progress_msg)
                except RuntimeError:
                    return
                await asyncio.sleep(0.05)

            try:
                generate_btn.props(remove="loading disabled")
                cancel_btn.props(remove="disabled")
                progress_card.set_visibility(False)
            except RuntimeError:
                _state.pending_navigate = bool(
                    _state.schedules and not _state.generation_error
                )
                return

            if _state.generation_error:
                try:
                    status_label.set_text(f"Error: {_state.generation_error}")
                except RuntimeError:
                    pass
                return

            cancelled = _state.stop_event and _state.stop_event.is_set()
            if cancelled:
                if _state.schedules:
                    _state.current_index = 0
                    try:
                        ui.navigate.to("/display_schedules")
                    except RuntimeError:
                        _state.pending_navigate = True
                else:
                    try:
                        status_label.set_text("Generation cancelled.")
                    except RuntimeError:
                        pass
                return

            if not _state.schedules:
                try:
                    diagnosis = GUIView.controller.diagnose_schedule_failure()
                    status_label.set_text(
                        diagnosis or "No valid schedules could be generated."
                    )
                except RuntimeError:
                    pass
                return

            _state.current_index = 0
            try:
                ui.navigate.to("/display_schedules")
            except RuntimeError:
                _state.pending_navigate = True

        if _state.is_generating:
            asyncio.ensure_future(_attach_poll())

        if _state.pending_navigate:
            _state.pending_navigate = False
            ui.navigate.to("/display_schedules")
            return

        def _on_cancel():
            if _state.stop_event:
                _state.stop_event.set()
            try:
                cancel_btn.props("disabled")
            except RuntimeError:
                pass

        cancel_btn.on("click", _on_cancel)

        async def on_generate():
            if _state.is_generating:
                return
            if GUIView.controller is None or not GUIView.controller.has_config():
                status_label.set_text("Error: No configuration loaded.")
                return
            errors = GUIView.controller.validate_schedule_config()
            if errors:
                status_label.set_text(f"Configuration invalid:\n{errors}")
                return

            limit = int(limit_input.value or config_limit)

            _state.schedules = []
            _state.current_index = 0
            _state.generation_error = None
            _state.progress_pct = 0
            _state.progress_msg = "Starting..."
            _state.pending_navigate = False
            _state.generation_limit = limit
            _state.stop_event = _threading.Event()
            _state.is_generating = True

            progress_card.set_visibility(True)
            status_label.set_text("")
            progress_bar.set_value(0.0)
            progress_label.set_text("0%")
            progress_message.set_text("Starting...")
            generate_btn.props("loading disabled")

            def _run():
                try:
                    if GUIView.controller is None:
                        _state.generation_error = "No controller"
                        return
                    scheduler_model = GUIView.controller.scheduler_model
                    facade = SchedulerFacade(scheduler_model)
                    facade.generate(
                        limit=limit,
                        progress_callback=lambda pct, msg: (
                            setattr(_state, "progress_pct", pct)
                            or setattr(_state, "progress_msg", msg)
                        ),
                        schedule_callback=lambda s: _state.schedules.append(s),
                        stop_event=_state.stop_event,
                    )
                except Exception as exc:
                    _state.generation_error = str(exc)
                finally:
                    _state.is_generating = False

            pool = ThreadPoolExecutor()
            asyncio.get_event_loop().run_in_executor(pool, _run)
            pool.shutdown(wait=False)

            await _attach_poll()

        generate_btn.on("click", on_generate)

    @ui.page("/display_schedules")
    @staticmethod
    def display_schedules():  # noqa: C901
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

        # ----------------------------------------------------------------
        # Course detail dialog — shared by both calendar views
        # ----------------------------------------------------------------
        detail_dialog = ui.dialog()

        def _show_course_detail(info: dict):
            detail_dialog.clear()
            with (
                detail_dialog,
                ui.card().classes("w-[380px] rounded-2xl shadow-xl p-6 gap-3"),
            ):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label(
                        f"{info.get('course', '')}  ·  Section {info.get('section', '')}"
                    ).classes("text-xl font-bold")
                    ui.button(icon="close", on_click=detail_dialog.close).props(
                        "flat round dense"
                    )
                ui.separator()
                with ui.column().classes("gap-2 w-full"):
                    with ui.row().classes("gap-2 items-center"):
                        ui.icon("person").classes("text-gray-500")
                        ui.label(info.get("faculty", "—")).classes("text-sm")
                    with ui.row().classes("gap-2 items-center"):
                        ui.icon("meeting_room").classes("text-gray-500")
                        ui.label(f"Room: {info.get('room', '—')}").classes("text-sm")
                    with ui.row().classes("gap-2 items-center"):
                        ui.icon("science").classes("text-gray-500")
                        ui.label(f"Lab: {info.get('lab', '—')}").classes("text-sm")
                    ui.separator()
                    ui.label("Lecture Times").classes(
                        "text-xs font-semibold text-gray-500 uppercase tracking-wide"
                    )
                    for t in info.get("lecture_times", []):
                        ui.label(t).classes("text-sm ml-2")
                    if info.get("lab_time"):
                        ui.label("Lab Time").classes(
                            "text-xs font-semibold text-gray-500 uppercase tracking-wide mt-1"
                        )
                        ui.label(info["lab_time"]).classes("text-sm ml-2")
            detail_dialog.open()

        if not _state.schedules:
            with ui.column().classes("gap-4 items-center w-full pt-20"):
                ui.label("No schedules available.").classes(
                    "text-2xl !text-black dark:!text-white"
                )
                ui.label("Please generate schedules first.").classes("text-gray-600")
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("w-48 h-12 text-base dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
                ui.button("Generate Schedules").props(
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

        room_filter = [None]
        faculty_filter = [None]

        with ui.column().classes("gap-4 items-center w-full px-4 pt-6 pb-24"):
            ui.label("Schedule Viewer").classes(
                "text-4xl font-bold !text-black dark:!text-white"
            )

            with ui.column().classes("items-center gap-1"):
                with ui.row().classes("items-center gap-4 justify-center"):
                    prev_btn = (
                        ui.button(icon="chevron_left")
                        .props("round flat color=black")
                        .classes("dark:!text-white")
                    )
                    index_label = ui.label(
                        f"Schedule {_state.current_index + 1} of {len(_state.schedules)}"
                    ).classes(
                        "text-lg font-semibold !text-black dark:!text-white min-w-[160px] text-center"
                    )
                    next_btn = (
                        ui.button(icon="chevron_right")
                        .props("round flat color=black")
                        .classes("dark:!text-white")
                    )
                generation_status = ui.label(
                    f"Generating {_state.generation_limit} schedules…"
                    if _state.is_generating
                    else "Generation complete."
                ).classes("text-xs !text-gray-400 text-center")

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

        ui.add_css("""
            .sticky-btn {
                box-shadow: 0 4px 14px rgba(0,0,0,0.35);
            }
            .body--dark .sticky-btn {
                box-shadow: 0 0 12px rgba(255,255,255,0.25);
            }
        """)
        with ui.row().classes(
            "gap-4 justify-center fixed bottom-4 left-0 right-0 z-40 py-2"
        ):
            ui.button("Back to Home").props(
                "rounded color=black text-color=white no-caps"
            ).classes(
                "w-44 h-12 text-base dark:!bg-white dark:!text-black sticky-btn"
            ).on("click", lambda: ui.navigate.to("/"))
            ui.button("Generate Schedules").props(
                "rounded color=black text-color=white no-caps"
            ).classes(
                "w-44 h-12 text-base dark:!bg-white dark:!text-black sticky-btn"
            ).on("click", lambda: ui.navigate.to("/run_scheduler"))
            ui.button("Export Schedules").props(
                "rounded color=black text-color=white no-caps"
            ).classes(
                "w-44 h-12 text-base dark:!bg-white dark:!text-black sticky-btn"
            ).on("click", export_dialog.open)
            ui.button("Import Schedules").props(
                "rounded color=black text-color=white no-caps"
            ).classes(
                "w-48 h-12 text-base dark:!bg-white dark:!text-black sticky-btn"
            ).on("click", upload_dialog.open)

        def _render_room_calendar(location_filter: str | None = None):
            """Render calendar like Google Calendar with actual course durations."""
            calendar_room_container.clear()
            calendar_data = _build_calendar_grid_by_room(
                _state.schedules[_state.current_index], location_filter=location_filter
            )

            if not calendar_data:
                with calendar_room_container:
                    ui.label("No schedule data available.").classes("text-gray-500 p-4")
                return

            days, hourly_slots = _extract_calendar_metadata(
                _state.schedules[_state.current_index]
            )
            all_faculty = [ci.faculty for ci in _state.schedules[_state.current_index]]
            faculty_color_map = _build_color_map(all_faculty)

            min_hour = 8
            max_hour = 17
            if hourly_slots:
                try:
                    min_hour = int(hourly_slots[0].split(":")[0])
                    max_hour = int(hourly_slots[-1].split(":")[0]) + 1
                except Exception:
                    pass
            min_hour = max(0, min_hour - 1)
            max_hour = min(24, max_hour + 1)

            for location in sorted(calendar_data.keys()):
                with calendar_room_container:
                    with ui.card().classes("w-full p-2 mb-4"):
                        ui.label(location).classes("text-lg font-bold mb-2 px-2")

                        hour_height = 80
                        pixels_per_minute = hour_height / 60.0
                        total_hours = max_hour - min_hour

                        header = ui.row().classes("w-full gap-0")
                        with header:
                            ui.label("").classes("text-xs font-semibold").style(
                                "width: 50px;"
                            )
                            for day in days:
                                ui.label(day).classes(
                                    "text-xs font-semibold text-center flex-1"
                                )

                        grid = (
                            ui.row()
                            .classes(
                                "w-full gap-0 border border-gray-300 dark:border-gray-600"
                            )
                            .style("position: relative;")
                        )

                        with grid:
                            time_col = (
                                ui.column()
                                .classes("gap-0")
                                .style(
                                    "width: 50px; flex-shrink: 0; border-r border-gray-300 dark:border-gray-600;"
                                )
                            )
                            with time_col:
                                for hour in range(min_hour, max_hour):
                                    hour_str = f"{hour:02d}:00"
                                    ui.label(hour_str).classes(
                                        "text-xs font-semibold p-1 text-center"
                                    ).style(
                                        f"height: {hour_height}px; border-b border-gray-300 dark:border-gray-600;"
                                    )

                            for day in days:
                                day_col = (
                                    ui.column()
                                    .classes(
                                        "flex-1 border-r border-gray-300 dark:border-gray-600"
                                    )
                                    .style("position: relative; overflow: visible;")
                                )

                                with day_col:
                                    total_height = hour_height * total_hours
                                    svg_html = f'<svg style="position: absolute; top: 0; left: 0; width: 100%; height: {total_height}px; pointer-events: none; z-index: 1;">'
                                    for i in range(1, total_hours):
                                        y = i * hour_height
                                        svg_html += f'<line x1="0" y1="{y}" x2="100%" y2="{y}" stroke="#d1d5db" stroke-width="1"/>'
                                    svg_html += f'<line x1="100%" y1="0" x2="100%" y2="{total_height}" stroke="#d1d5db" stroke-width="1"/>'
                                    svg_html += "</svg>"
                                    ui.html(svg_html).style("width: 100%;")

                                    # Deduplicate courses for this day
                                    all_courses_for_day = {}
                                    for time_slot in hourly_slots:
                                        courses_list = (
                                            calendar_data[location]
                                            .get(day, {})
                                            .get(time_slot, [])
                                        )
                                        for course_info in courses_list:
                                            course_id = course_info.get(
                                                "full_course_str", ""
                                            )
                                            fac = course_info["faculty"]
                                            key = (course_id, fac)
                                            if key not in all_courses_for_day:
                                                all_courses_for_day[key] = course_info

                                    for (
                                        course_id,
                                        faculty,
                                    ), course_info in all_courses_for_day.items():
                                        course_time_str = None
                                        for ci in _state.schedules[
                                            _state.current_index
                                        ]:
                                            if (
                                                ci.course_str == course_id
                                                and ci.faculty == faculty
                                            ):
                                                for t_idx, time_instance in enumerate(
                                                    ci.times
                                                ):
                                                    t_str = str(time_instance).strip()
                                                    if _extract_day(t_str) == day:
                                                        course_time_str = t_str
                                                        break
                                                if course_time_str:
                                                    break

                                        if course_time_str:
                                            time_range = _extract_time_range(
                                                course_time_str
                                            )
                                            if time_range:
                                                start_time, end_time = time_range
                                                start_hour, start_min = start_time

                                                duration_minutes = (
                                                    _calculate_course_duration_minutes(
                                                        course_time_str
                                                    )
                                                )
                                                top_offset = (
                                                    (start_hour - min_hour)
                                                    * hour_height
                                                ) + (start_min * pixels_per_minute)
                                                block_height = max(
                                                    20,
                                                    int(
                                                        duration_minutes
                                                        * pixels_per_minute
                                                    ),
                                                )

                                                color_tuple = faculty_color_map.get(
                                                    faculty, COURSE_COLORS[0]
                                                )
                                                color_class = _get_color_classes(
                                                    color_tuple
                                                )

                                                block = (
                                                    ui.card()
                                                    .classes(
                                                        f"{color_class} p-1 text-xs shadow-sm absolute"
                                                    )
                                                    .style(
                                                        f"top: {top_offset}px; left: 1px; right: 1px; "
                                                        f"height: {block_height}px; overflow: hidden; "
                                                        f"border-radius: 3px; z-index: 10; "
                                                        f"box-sizing: border-box; cursor: pointer;"
                                                    )
                                                )
                                                with block:
                                                    ui.label(
                                                        course_info["course"]
                                                    ).classes(
                                                        "font-bold text-xs leading-tight"
                                                    )
                                                    ui.label(
                                                        f"Sec: {course_info['section']}"
                                                    ).classes("text-xs leading-tight")

                                                # Factory to capture loop variables
                                                def _make_room_handler(cid, fac):
                                                    def _handler():
                                                        info = _get_full_course_info(
                                                            _state.schedules[
                                                                _state.current_index
                                                            ],
                                                            cid,
                                                            fac,
                                                        )
                                                        _show_course_detail(info)

                                                    return _handler

                                                block.on(
                                                    "click",
                                                    _make_room_handler(
                                                        course_id, faculty
                                                    ),
                                                )

        def _render_faculty_calendar(faculty_filter: str | None = None):
            """Render calendar like Google Calendar with actual course durations."""
            calendar_faculty_container.clear()
            calendar_data = _build_calendar_grid_by_faculty(
                _state.schedules[_state.current_index], faculty_filter=faculty_filter
            )

            if not calendar_data:
                with calendar_faculty_container:
                    ui.label("No schedule data available.").classes("text-gray-500 p-4")
                return

            days, hourly_slots = _extract_calendar_metadata(
                _state.schedules[_state.current_index]
            )
            all_courses = [
                ci.course_str.rsplit(".", 1)[0]
                for ci in _state.schedules[_state.current_index]
            ]
            course_color_map = _build_color_map(all_courses)

            min_hour = 8
            max_hour = 17
            if hourly_slots:
                try:
                    min_hour = int(hourly_slots[0].split(":")[0])
                    max_hour = int(hourly_slots[-1].split(":")[0]) + 1
                except Exception:
                    pass
            min_hour = max(0, min_hour - 1)
            max_hour = min(24, max_hour + 1)

            for faculty in sorted(calendar_data.keys()):
                with calendar_faculty_container:
                    with ui.card().classes("w-full p-2 mb-4"):
                        ui.label(faculty).classes("text-lg font-bold mb-2 px-2")

                        hour_height = 80
                        pixels_per_minute = hour_height / 60.0
                        total_hours = max_hour - min_hour

                        header = ui.row().classes("w-full gap-0")
                        with header:
                            ui.label("").classes("text-xs font-semibold").style(
                                "width: 50px;"
                            )
                            for day in days:
                                ui.label(day).classes(
                                    "text-xs font-semibold text-center flex-1"
                                )

                        grid = (
                            ui.row()
                            .classes(
                                "w-full gap-0 border border-gray-300 dark:border-gray-600"
                            )
                            .style("position: relative;")
                        )

                        with grid:
                            time_col = (
                                ui.column()
                                .classes("gap-0")
                                .style(
                                    "width: 50px; flex-shrink: 0; border-r border-gray-300 dark:border-gray-600;"
                                )
                            )
                            with time_col:
                                for hour in range(min_hour, max_hour):
                                    hour_str = f"{hour:02d}:00"
                                    ui.label(hour_str).classes(
                                        "text-xs font-semibold p-1 text-center"
                                    ).style(
                                        f"height: {hour_height}px; border-b border-gray-300 dark:border-gray-600;"
                                    )

                            for day in days:
                                day_col = (
                                    ui.column()
                                    .classes(
                                        "flex-1 border-r border-gray-300 dark:border-gray-600"
                                    )
                                    .style("position: relative; overflow: visible;")
                                )

                                with day_col:
                                    total_height = hour_height * total_hours
                                    svg_html = f'<svg style="position: absolute; top: 0; left: 0; width: 100%; height: {total_height}px; pointer-events: none; z-index: 1;">'
                                    for i in range(1, total_hours):
                                        y = i * hour_height
                                        svg_html += f'<line x1="0" y1="{y}" x2="100%" y2="{y}" stroke="#d1d5db" stroke-width="1"/>'
                                    svg_html += f'<line x1="100%" y1="0" x2="100%" y2="{total_height}" stroke="#d1d5db" stroke-width="1"/>'
                                    svg_html += "</svg>"
                                    ui.html(svg_html).style("width: 100%;")

                                    # Deduplicate courses for this day
                                    all_courses_for_day = {}
                                    for time_slot in hourly_slots:
                                        courses_list = (
                                            calendar_data[faculty]
                                            .get(day, {})
                                            .get(time_slot, [])
                                        )
                                        for course_info in courses_list:
                                            course_id = course_info.get(
                                                "full_course_str", ""
                                            )
                                            key = course_id
                                            if key not in all_courses_for_day:
                                                all_courses_for_day[key] = course_info

                                    for (
                                        course_id,
                                        course_info,
                                    ) in all_courses_for_day.items():
                                        course_time_str = None
                                        for ci in _state.schedules[
                                            _state.current_index
                                        ]:
                                            if (
                                                ci.course_str == course_id
                                                and ci.faculty == faculty
                                            ):
                                                for t_idx, time_instance in enumerate(
                                                    ci.times
                                                ):
                                                    t_str = str(time_instance).strip()
                                                    if _extract_day(t_str) == day:
                                                        course_time_str = t_str
                                                        break
                                                if course_time_str:
                                                    break

                                        if course_time_str:
                                            time_range = _extract_time_range(
                                                course_time_str
                                            )
                                            if time_range:
                                                start_time, end_time = time_range
                                                start_hour, start_min = start_time

                                                duration_minutes = (
                                                    _calculate_course_duration_minutes(
                                                        course_time_str
                                                    )
                                                )
                                                top_offset = (
                                                    (start_hour - min_hour)
                                                    * hour_height
                                                ) + (start_min * pixels_per_minute)
                                                block_height = max(
                                                    20,
                                                    int(
                                                        duration_minutes
                                                        * pixels_per_minute
                                                    ),
                                                )

                                                color_tuple = course_color_map.get(
                                                    course_info["course"],
                                                    COURSE_COLORS[0],
                                                )
                                                color_class = _get_color_classes(
                                                    color_tuple
                                                )

                                                block = (
                                                    ui.card()
                                                    .classes(
                                                        f"{color_class} p-1 text-xs shadow-sm absolute"
                                                    )
                                                    .style(
                                                        f"top: {top_offset}px; left: 1px; right: 1px; "
                                                        f"height: {block_height}px; overflow: hidden; "
                                                        f"border-radius: 3px; z-index: 10; "
                                                        f"box-sizing: border-box; cursor: pointer;"
                                                    )
                                                )
                                                with block:
                                                    ui.label(
                                                        course_info["course"]
                                                    ).classes(
                                                        "font-bold text-xs leading-tight"
                                                    )
                                                    ui.label(
                                                        f"Sec: {course_info['section']}"
                                                    ).classes("text-xs leading-tight")

                                                # Factory to capture loop variables
                                                def _make_faculty_handler(cid, fac):
                                                    def _handler():
                                                        info = _get_full_course_info(
                                                            _state.schedules[
                                                                _state.current_index
                                                            ],
                                                            cid,
                                                            fac,
                                                        )
                                                        _show_course_detail(info)

                                                    return _handler

                                                block.on(
                                                    "click",
                                                    _make_faculty_handler(
                                                        course_id, faculty
                                                    ),
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
            if _state.current_index >= len(_state.schedules) - 1:
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
            index_label.set_text(
                f"Schedule {_state.current_index + 1} of {len(_state.schedules)}"
            )
            _sync_btn_states()

        def go_prev():
            if _state.current_index > 0:
                _state.current_index -= 1
                _reload_schedule()

        def go_next():
            if _state.current_index < len(_state.schedules) - 1:
                _state.current_index += 1
                _reload_schedule()

        prev_btn.on("click", go_prev)
        next_btn.on("click", go_next)
        _reload_schedule()

        async def _poll_count():
            last_count = len(_state.schedules)
            while _state.is_generating:
                await asyncio.sleep(0.2)
                current_count = len(_state.schedules)
                if current_count != last_count:
                    last_count = current_count
                    try:
                        index_label.set_text(
                            f"Schedule {_state.current_index + 1} of {current_count}"
                        )
                        _sync_btn_states()
                    except RuntimeError:
                        return
            try:
                generation_status.set_text("Generation complete.")
            except RuntimeError:
                pass

        if _state.is_generating:
            asyncio.ensure_future(_poll_count())

    @ui.page("/test_schedules")
    @staticmethod
    def test_schedules():
        """Development test page — generates schedules from the CLI config path."""
        import os
        import sys

        status = ui.label("Generating test schedules...").classes(
            "text-gray-600 italic p-4"
        )

        async def _run():
            try:
                if len(sys.argv) < 2 or not os.path.exists(sys.argv[1]):
                    status.set_text("Error: no valid config path in sys.argv[1]")
                    return
                from views.gui_view import GUIView

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
