# views/faculty_gui_view.py
"""
FacultyGUIView - Graphical-user interface for faculty interactions

  MVC rules followed in this file:
    - No Model references are stored or imported.
    - No Model methods are called directly.
    - All data operations go through GUIView.controller.faculty_controller.
    - Validation lives in the Controller.
    - Save orchestration is delegated to Controller methods.
"""

from typing import Any
from nicegui import ui
from views.gui_theme import GUITheme
from views.gui_utils import require_config
from views.schedule_gui_view import (
    _extract_calendar_metadata,
    _build_calendar_grid_by_faculty,
    _sort_time_slots,
    _extract_time_portion,
    _build_color_map,
    _get_color_classes,
    _extract_day,
    _calculate_course_span,
    COURSE_COLORS,
)


class _FacultyCalendarState:
    """Holds calendar state for faculty view."""

    def __init__(self):
        self.schedules: list[list] = []
        self.current_index: int = 0


_faculty_calendar_state = _FacultyCalendarState()


class FacultyGUIView:
    faculty_model: Any = None
    faculty_controller: Any = None
    # Faculty GUI View

    @ui.page("/faculty")
    @staticmethod
    def faculty():
        """
        Displays the Faculty hub page with navigation buttons.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/"):
            return
        with ui.column().classes("w-full items-center pt-12 pb-12 font-sans"):
            ui.label("Faculty").classes("text-4xl mb-10 !text-black dark:!text-white")
            ui.button("Add Faculty").props("rounded text-color=white no-caps").classes(
                "w-80 h-16 text-xl"
            ).style(
                "background: linear-gradient(135deg, var(--q-facultyBegin), var(--q-facultyEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/faculty/add"))
            ui.button("Modify Faculty").props(
                "rounded text-color=white no-caps"
            ).classes("w-80 h-16 text-xl").style(
                "background: linear-gradient(135deg, var(--q-facultyBegin), var(--q-facultyEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/faculty/modify"))
            ui.button("Delete Faculty").props(
                "rounded text-color=white no-caps"
            ).classes("w-80 h-16 text-xl").style(
                "background: linear-gradient(135deg, var(--q-facultyBegin), var(--q-facultyEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/faculty/delete"))
            ui.button("View Faculty").props("rounded text-color=white no-caps").classes(
                "w-80 h-16 text-xl"
            ).style(
                "background: linear-gradient(135deg, var(--q-facultyBegin), var(--q-facultyEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/faculty/view"))
            ui.space()
            ui.button("Back").props(
                "rounded color=backbtn text-color=white no-caps"
            ).classes(
                "w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]"
            ).on("click", lambda: ui.navigate.to("/"))

    @ui.page("/faculty/add")
    @staticmethod
    def faculty_add():
        """
        Displays the GUI for adding a faculty member.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/faculty"):
            return
        from views.gui_view import GUIView

        # Read controller reference at render time.
        if GUIView.controller is None:
            return
        controller = GUIView.controller.faculty_controller

        with ui.column().classes("w-full items-center font-sans p-8 gap-0"):
            with ui.row().classes("w-full max-w-6xl justify-start mb-4"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )

            ui.label("Add Faculty").classes(
                "text-5xl mb-12 mt-4 !text-black dark:!text-white"
            )

            with ui.row().classes("w-full max-w-6xl justify-between items-start"):
                # Left Column
                with ui.column().classes("w-[50%] gap-6"):
                    with ui.row().classes("items-center gap-4 w-full"):
                        ui.label("Enter Faculty Name:").classes(
                            "text-2xl !text-black dark:!text-white"
                        )
                        name_input = (
                            ui.input()
                            .props(
                                'outlined dense square color=dark input-style="color: black !important"'
                            )
                            .classes("w-64 text-xl")
                            .style("background-color: white;")
                        )

                    with ui.row().classes("items-center gap-6 w-full"):
                        ui.label("Faculty Position:").classes(
                            "text-2xl !text-black dark:!text-white"
                        )
                        position_radio = (
                            ui.radio(["Full Time", "Adjunct"], value="Full Time")
                            .props("inline")
                            .classes(
                                "text-xl !text-black dark:!text-white gap-4 faculty-radio"
                            )
                        )
                        ui.add_css(
                            ".faculty-radio .q-radio__inner { color: inherit !important; }"
                        )

                    ui.label("Faculty Availability:").classes(
                        "text-2xl !text-black dark:!text-white"
                    )

                    day_inputs = {}
                    with ui.column().classes("w-full pl-4 gap-2"):
                        for day in [
                            "Monday",
                            "Tuesday",
                            "Wednesday",
                            "Thursday",
                            "Friday",
                        ]:
                            with ui.row().classes("items-center w-full pr-4 gap-4"):
                                cb = (
                                    ui.checkbox(day)
                                    .props("color=dark")
                                    .classes("text-xl !text-black dark:!text-white")
                                )

                                def handle_time_change(e, is_start, related_input):
                                    if e.value and not related_input.value:
                                        related_input.value = (
                                            "20:00" if is_start else "08:00"
                                        )

                                with (
                                    ui.row()
                                    .classes("items-center gap-2")
                                    .bind_visibility_from(cb, "value")
                                ):
                                    start_input = (
                                        ui.input("Start (e.g. 08:00)")
                                        .props(
                                            'outlined dense square color=dark label-color=grey-7 input-style="color: black !important"'
                                        )
                                        .classes("w-28")
                                        .style("background-color: white;")
                                    )
                                    ui.label("to").classes(
                                        "text-lg !text-black dark:!text-white"
                                    )
                                    end_input = (
                                        ui.input("End (e.g. 20:00)")
                                        .props(
                                            'outlined dense square color=dark label-color=grey-7 input-style="color: black !important"'
                                        )
                                        .classes("w-28")
                                        .style("background-color: white;")
                                    )
                                    start_input.on_value_change(
                                        lambda e, si=start_input, ei=end_input: (
                                            handle_time_change(e, True, ei)
                                        )
                                    )
                                    end_input.on_value_change(
                                        lambda e, si=start_input, ei=end_input: (
                                            handle_time_change(e, False, si)
                                        )
                                    )
                                day_inputs[day] = {
                                    "cb": cb,
                                    "start": start_input,
                                    "end": end_input,
                                }

                    with ui.column().classes("w-full mt-6 gap-2"):
                        ui.label("Courses and Preferences:").classes(
                            "text-2xl !text-black dark:!text-white"
                        )
                        course_container = ui.column().classes("w-full gap-2")
                        course_rows = []

                        def add_course_row():
                            options = controller.get_available_courses()
                            with course_container:
                                row_container = ui.row().classes(
                                    "items-center gap-4 w-full wrap"
                                )
                                with row_container:
                                    course_input = (
                                        ui.select(
                                            options,
                                            label="Course Code",
                                            with_input=True,
                                        )
                                        .props(
                                            'outlined dense square options-dense behavior="menu" label-color=grey-7 input-style="color: black !important"'
                                        )
                                        .classes("flex-grow")
                                        .style(
                                            "background-color: white; color: black; min-width: 150px;"
                                        )
                                    )
                                    weight_input = (
                                        ui.number(
                                            "Weight (1-10)", min=1, max=10, value=5
                                        )
                                        .props(
                                            'outlined dense square label-color=grey-7 input-style="color: black !important"'
                                        )
                                        .classes("w-40")
                                        .style("background-color: white; color: black;")
                                    )
                                    row_data = {
                                        "course": course_input,
                                        "weight": weight_input,
                                    }
                                    course_rows.append(row_data)

                                    def delete_row(e, rc=row_container, rd=row_data):
                                        rc.delete()
                                        if rd in course_rows:
                                            course_rows.remove(rd)

                                    ui.button("X", on_click=delete_row).props(
                                        "color=red text-color=white rounded glossy"
                                    ).classes("h-10 w-10 min-w-10")

                        add_course_row()
                        ui.button("+ Add Course", on_click=add_course_row).props(
                            "color=black text-color=white rounded"
                        ).classes("mt-2 px-6")

                    with ui.column().classes("w-full mt-6 gap-2"):
                        ui.label("Lab Preferences:").classes(
                            "text-2xl !text-black dark:!text-white"
                        )
                        lab_container = ui.column().classes("w-full gap-2")
                        lab_rows = []

                        def add_lab_row():
                            options = controller.get_available_labs()
                            with lab_container:
                                row_container = ui.row().classes(
                                    "items-center gap-4 w-full wrap"
                                )
                                with row_container:
                                    lab_input = (
                                        ui.select(
                                            options, label="Lab Name", with_input=True
                                        )
                                        .props(
                                            'outlined dense square options-dense behavior="menu" label-color=grey-7 input-style="color: black !important"'
                                        )
                                        .classes("flex-grow")
                                        .style(
                                            "background-color: white; color: black; min-width: 150px;"
                                        )
                                    )
                                    weight_input = (
                                        ui.number(
                                            "Weight (1-10)", min=1, max=10, value=5
                                        )
                                        .props(
                                            'outlined dense square label-color=grey-7 input-style="color: black !important"'
                                        )
                                        .classes("w-40")
                                        .style("background-color: white; color: black;")
                                    )
                                    row_data = {
                                        "lab": lab_input,
                                        "weight": weight_input,
                                    }
                                    lab_rows.append(row_data)

                                    def delete_row(e, rc=row_container, rd=row_data):
                                        rc.delete()
                                        if rd in lab_rows:
                                            lab_rows.remove(rd)

                                    ui.button("X", on_click=delete_row).props(
                                        "color=red text-color=white rounded glossy"
                                    ).classes("h-10 w-10 min-w-10")

                        add_lab_row()
                        ui.button("+ Add Lab", on_click=add_lab_row).props(
                            "color=black text-color=white rounded"
                        ).classes("mt-2 px-6")

                # Right Column — uses controller to fetch faculty list, not model directly.
                with (
                    ui.column()
                    .classes(
                        "w-[45%] h-[500px] border-4 p-6 items-start justify-start overflow-hidden"
                    )
                    .style("border-color: black; background-color: white;")
                ):
                    ui.label("Existing Faculty").classes(
                        "text-3xl !text-black text-center w-full mb-4 font-bold pb-2"
                    ).style("border-bottom: 2px solid black;")
                    scroll_area = ui.scroll_area().classes("w-full h-full pr-4")

                    def refresh_faculty_list():
                        scroll_area.clear()
                        with scroll_area:
                            faculty_list = controller.get_all_faculty()
                            if faculty_list:
                                for f in faculty_list:
                                    ui.label(f.name).classes(
                                        "text-xl !text-black mb-2 py-2 w-full"
                                    ).style("border-bottom: 1px solid #e5e7eb;")
                            else:
                                ui.label("No existing faculty found.").classes(
                                    "text-xl text-gray-500 italic"
                                )

                    refresh_faculty_list()

            def _collect_faculty_data():
                """Collect form data into a dict. Returns None and notifies if invalid."""
                import re

                name = name_input.value
                if not name:
                    ui.notify("Faculty name is required!", type="negative")
                    return None
                is_full_time = position_radio.value == "Full Time"
                times_data = {}
                time_pattern = re.compile(r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$")
                for day, inputs in day_inputs.items():
                    if inputs["cb"].value:
                        start_time = inputs["start"].value or "08:00"
                        end_time = inputs["end"].value or "20:00"
                        if not time_pattern.match(start_time):
                            ui.notify(
                                f'Invalid start time "{start_time}" for {day}. Use HH:MM format.',
                                type="negative",
                            )
                            return None
                        if not time_pattern.match(end_time):
                            ui.notify(
                                f'Invalid end time "{end_time}" for {day}. Use HH:MM format.',
                                type="negative",
                            )
                            return None
                        start_mins = int(start_time[:2]) * 60 + int(start_time[3:])
                        end_mins = int(end_time[:2]) * 60 + int(end_time[3:])
                        if end_mins <= start_mins:
                            ui.notify(
                                f"End time must be after start time for {day}.",
                                type="negative",
                            )
                            return None
                        times_data[day] = [{"start": start_time, "end": end_time}]
                course_prefs = {
                    row["course"].value: int(row["weight"].value or 5)
                    for row in course_rows
                    if row["course"].value
                }
                lab_prefs = {
                    row["lab"].value: int(row["weight"].value or 5)
                    for row in lab_rows
                    if row["lab"].value
                }
                return {
                    "name": name,
                    "is_full_time": is_full_time,
                    "times": times_data,
                    "days": list(times_data.keys()),
                    "course_preferences": course_prefs,
                    "lab_preferences": lab_prefs,
                }

            def save_faculty():
                """Save to memory and persist to config immediately."""
                faculty_data = _collect_faculty_data()
                if faculty_data is None:
                    return
                try:
                    from views.gui_view import GUIView

                    if not GUIView.controller:
                        ui.notify("System not initialized properly.", type="negative")
                        return
                    controller = GUIView.controller.faculty_controller
                    if controller.add_faculty(faculty_data):
                        ui.notify(
                            f"Faculty '{faculty_data['name']}' added.", type="positive"
                        )
                        name_input.value = ""
                        refresh_faculty_list()
                    else:
                        ui.notify(
                            "Failed to add faculty. Maybe they already exist?",
                            type="negative",
                        )
                except Exception as e:
                    ui.notify(f"Error saving: {e}", type="negative")

            with ui.row().classes("w-full max-w-6xl justify-between items-end mt-16"):
                ui.button("Cancel").props(
                    "rounded color=black text-color=white no-caps"
                ).classes(
                    "w-48 h-16 text-2xl font-bold dark:!bg-white dark:!text-black"
                ).on("click", lambda: ui.navigate.to("/faculty"))
                ui.button("Save").props(
                    "rounded color=black text-color=white no-caps"
                ).classes(
                    "w-48 h-16 text-2xl font-bold dark:!bg-white dark:!text-black"
                ).on("click", save_faculty)

    @ui.page("/faculty/modify")
    @staticmethod
    def faculty_modify():
        """
        Displays the GUI for modifying faculty.

        User first selects a faculty member from a dropdown, then sees
        all of their current information with structured button-based
        controls for making changes. Changes are in-memory until Save
        Configuration is clicked.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/faculty"):
            return
        from views.gui_view import GUIView

        ui.query("body").style("background-color: var(--q-modify)").classes(
            "dark:!bg-black"
        )

        if GUIView.controller is None:
            return
        controller = GUIView.controller.faculty_controller
        all_faculty = controller.model.get_all_faculty()

        with ui.column().classes("w-full items-center pt-12 pb-12 font-sans gap-6"):
            with ui.row().classes("w-full max-w-2xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )

            ui.label("Modify Faculty").classes(
                "text-4xl mb-4 !text-black dark:!text-white"
            )
            ui.label("Select a Faculty member to modify their information.").classes(
                "text-lg !text-black dark:!text-white text-center max-w-xl"
            )

            if not all_faculty:
                ui.label("There are no faculty in the configuration.").classes(
                    "text-xl !text-black dark:!text-white"
                )
                ui.button("Back").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/faculty")
                )
                return

            faculty_options = {f.name: f for f in all_faculty}
            selected_faculty = {"value": None}
            form_card = ui.card().classes("w-full max-w-2xl")
            form_card.set_visibility(False)

            def reload_form():
                val = selected_faculty["value"]
                if not val:
                    return
                updated = controller.get_faculty_by_name(val.name)
                selected_faculty["value"] = updated
                faculty_options[updated.name] = updated
                form_card.clear()
                build_form(updated)

            def apply(field, value, feedback_label):
                """Apply a single field update via the Controller."""
                f = selected_faculty["value"]
                if not f:
                    return
                success, message = controller.modify_faculty_field(f.name, field, value)
                if success:
                    feedback_label.set_text("Updated.")
                    feedback_label.classes(replace="text-md text-green-600")
                    reload_form()
                else:
                    feedback_label.set_text(f"Failed to update: {message}")
                    feedback_label.classes(replace="text-md text-red-600")

            def build_form(f):
                with form_card:
                    with ui.column().classes("w-full gap-6 p-6"):
                        # --- Position Type ---
                        with ui.column().classes("w-full gap-2"):
                            ui.label("Position Type").classes(
                                "!text-black dark:!text-white font-bold text-lg"
                            )
                            is_fulltime = f.unique_course_limit >= 2
                            ui.label(
                                f"Current: {'Full-time' if is_fulltime else 'Adjunct'} | Max Credits: {f.maximum_credits} | Course Limit: {f.unique_course_limit}"
                            ).classes("!text-black dark:!text-white")
                            position_feedback = ui.label(" ").classes(
                                "text-md !text-black dark:!text-white"
                            )
                            with ui.row().classes("gap-4"):
                                ui.button("Set Full-time").props(
                                    "rounded color=black text-color=white no-caps"
                                ).on(
                                    "click",
                                    lambda: [
                                        controller.gui_set_position(
                                            (
                                                selected_faculty["value"].name
                                                if selected_faculty["value"]
                                                else ""
                                            ),
                                            True,
                                        ),
                                        position_feedback.set_text(
                                            "Position set to Full-time."
                                        ),
                                        position_feedback.classes(
                                            replace="text-md text-green-600"
                                        ),
                                        reload_form(),
                                    ],
                                )
                                ui.button("Set Adjunct").props(
                                    "rounded color=black text-color=white no-caps"
                                ).on(
                                    "click",
                                    lambda: [
                                        controller.gui_set_position(
                                            (
                                                selected_faculty["value"].name
                                                if selected_faculty["value"]
                                                else ""
                                            ),
                                            False,
                                        ),
                                        position_feedback.set_text(
                                            "Position set to Adjunct."
                                        ),
                                        position_feedback.classes(
                                            replace="text-md text-green-600"
                                        ),
                                        reload_form(),
                                    ],
                                )

                        ui.separator()

                        # --- Maximum Credits ---
                        with ui.column().classes("w-full gap-2"):
                            ui.label("Maximum Credits").classes(
                                "!text-black dark:!text-white font-bold text-lg"
                            )
                            ui.label(f"Current: {f.maximum_credits}").classes(
                                "!text-black dark:!text-white"
                            )
                            max_credits_feedback = ui.label("").classes(
                                "text-md !text-black dark:!text-white"
                            )
                            with ui.row().classes("gap-4 items-center"):
                                max_credits_input = ui.number(
                                    min=0, max=20, value=f.maximum_credits
                                ).classes("w-32")

                                def save_max_credits():
                                    val = selected_faculty["value"]
                                    if not val:
                                        return
                                    success, message = controller.set_maximum_credits(
                                        val.name,
                                        int(max_credits_input.value),
                                    )
                                    if success:
                                        max_credits_feedback.set_text("Updated.")
                                        max_credits_feedback.classes(
                                            replace="text-md text-green-600"
                                        )
                                    reload_form()

                                ui.button("Save").props(
                                    "rounded color=black text-color=white no-caps"
                                ).on("click", save_max_credits)

                        ui.separator()

                        # --- Minimum Credits ---
                        with ui.column().classes("w-full gap-2"):
                            ui.label("Minimum Credits").classes(
                                "!text-black dark:!text-white font-bold text-lg"
                            )
                            ui.label(f"Current: {f.minimum_credits}").classes(
                                "!text-black dark:!text-white"
                            )
                            min_credits_feedback = ui.label("").classes(
                                "text-md !text-black dark:!text-white"
                            )
                            with ui.row().classes("gap-4 items-center"):
                                min_credits_input = ui.number(
                                    min=0,
                                    max=f.maximum_credits,
                                    value=f.minimum_credits,
                                ).classes("w-32")
                                ui.button("Save").props(
                                    "rounded color=black text-color=white no-caps"
                                ).on(
                                    "click",
                                    lambda: apply(
                                        "minimum_credits",
                                        int(min_credits_input.value),
                                        min_credits_feedback,
                                    ),
                                )

                        ui.separator()

                        # --- Availability Times ---
                        with ui.column().classes("w-full gap-2"):
                            ui.label("Availability Times").classes(
                                "!text-black dark:!text-white font-bold text-lg"
                            )
                            ui.label("Current:").classes("!text-black dark:!text-white")
                            for day, ranges in f.times.items():
                                times_str = (
                                    ", ".join(str(r) for r in ranges)
                                    if ranges
                                    else "unavailable"
                                )
                                ui.label(f"  {day}: {times_str}").classes(
                                    "!text-black dark:!text-white text-sm"
                                )

                            ui.label("Add/Update a day:").classes(
                                "!text-black dark:!text-white mt-2"
                            )
                            times_feedback = ui.label("").classes(
                                "text-md !text-black dark:!text-white"
                            )
                            with ui.row().classes("gap-4 items-center flex-wrap"):
                                day_select = ui.select(
                                    options=["MON", "TUE", "WED", "THU", "FRI"],
                                    label="Day",
                                ).classes("w-32")
                                start_input = ui.input(
                                    label="Start (HH:MM)", value="09:00"
                                ).classes("w-32")
                                end_input = ui.input(
                                    label="End (HH:MM)", value="17:00"
                                ).classes("w-32")

                                def save_time():
                                    import re
                                    from scheduler import TimeRange as TR

                                    if not day_select.value:
                                        times_feedback.set_text("Please select a day.")
                                        times_feedback.classes(
                                            replace="text-md text-red-600"
                                        )
                                        return
                                    start_val = start_input.value.strip()
                                    end_val = end_input.value.strip()
                                    time_pattern = re.compile(
                                        r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$"
                                    )
                                    if not time_pattern.match(
                                        start_val
                                    ) or not time_pattern.match(end_val):
                                        times_feedback.set_text(
                                            "Invalid time. Use HH:MM format."
                                        )
                                        times_feedback.classes(
                                            replace="text-md text-red-600"
                                        )
                                        return
                                    start_mins = int(start_val[:2]) * 60 + int(
                                        start_val[3:]
                                    )
                                    end_mins = int(end_val[:2]) * 60 + int(end_val[3:])
                                    if end_mins <= start_mins:
                                        times_feedback.set_text(
                                            "End time must be after start time."
                                        )
                                        times_feedback.classes(
                                            replace="text-md text-red-600"
                                        )
                                        return
                                    try:
                                        val = selected_faculty["value"]
                                        if not val:
                                            return
                                        new_times = dict(val.times)
                                        new_times[day_select.value] = [
                                            TR(start=start_val, end=end_val)
                                        ]
                                        apply("times", new_times, times_feedback)
                                    except Exception as ex:
                                        times_feedback.set_text(
                                            f"Invalid time format: {ex}"
                                        )
                                        times_feedback.classes(
                                            replace="text-md text-red-600"
                                        )

                                ui.button("Save Time").props(
                                    "rounded color=black text-color=white no-caps"
                                ).on("click", save_time)

                            def clear_day():
                                if not day_select.value:
                                    times_feedback.set_text("Please select a day.")
                                    times_feedback.classes(
                                        replace="text-md text-red-600"
                                    )
                                    return
                                val = selected_faculty["value"]
                                if not val:
                                    return
                                new_times = dict(val.times)
                                new_times[day_select.value] = []
                                apply("times", new_times, times_feedback)

                            ui.button("Mark Day Unavailable").props(
                                "rounded color=grey text-color=white no-caps"
                            ).on("click", clear_day)

                        ui.separator()

                        # --- Course Preferences ---
                        with ui.column().classes("w-full gap-2"):
                            ui.label("Course Preferences").classes(
                                "!text-black dark:!text-white font-bold text-lg"
                            )
                            if f.course_preferences:
                                for course, weight in f.course_preferences.items():
                                    ui.label(f"  {course}: {weight}").classes(
                                        "!text-black dark:!text-white text-sm"
                                    )
                            else:
                                ui.label("  None").classes(
                                    "!text-black dark:!text-white text-sm"
                                )

                            ui.label("Add/Update a course preference:").classes(
                                "!text-black dark:!text-white mt-2"
                            )
                            course_pref_feedback = ui.label("").classes(
                                "text-md !text-black dark:!text-white"
                            )
                            with ui.row().classes("gap-4 items-center flex-wrap"):
                                course_input = ui.input(
                                    label="Course ID (e.g. CMSC 161)"
                                ).classes("w-48")
                                weight_input = ui.number(
                                    label="Weight (0-10)", min=0, max=10, value=5
                                ).classes("w-32")

                                def save_course_pref():
                                    course = course_input.value.strip()
                                    if not course:
                                        course_pref_feedback.set_text(
                                            "Please enter a course ID."
                                        )
                                        course_pref_feedback.classes(
                                            replace="text-md text-red-600"
                                        )
                                        return
                                    val = selected_faculty["value"]
                                    if not val:
                                        return
                                    new_prefs = dict(val.course_preferences)
                                    new_prefs[course] = int(weight_input.value)
                                    apply(
                                        "course_preferences",
                                        new_prefs,
                                        course_pref_feedback,
                                    )

                                ui.button("Save").props(
                                    "rounded color=black text-color=white no-caps"
                                ).on("click", save_course_pref)

                            if f.course_preferences:
                                ui.label("Remove a course preference:").classes(
                                    "!text-black dark:!text-white mt-2"
                                )
                                with ui.row().classes("gap-4 items-center"):
                                    remove_course_select = ui.select(
                                        options=list(f.course_preferences.keys()),
                                        label="Course to Remove",
                                    ).classes("w-48")

                                    def remove_course_pref():
                                        if not remove_course_select.value:
                                            return
                                        val = selected_faculty["value"]
                                        if not val:
                                            return
                                        new_prefs = dict(val.course_preferences)
                                        new_prefs.pop(remove_course_select.value, None)
                                        apply(
                                            "course_preferences",
                                            new_prefs,
                                            course_pref_feedback,
                                        )

                                    ui.button("Remove").props(
                                        "rounded color=red text-color=white no-caps"
                                    ).on("click", remove_course_pref)

                        ui.separator()

                        # --- Room Preferences ---
                        with ui.column().classes("w-full gap-2"):
                            ui.label("Room Preferences").classes(
                                "!text-black dark:!text-white font-bold text-lg"
                            )
                            if f.room_preferences:
                                for room, weight in f.room_preferences.items():
                                    ui.label(f"  {room}: {weight}").classes(
                                        "!text-black dark:!text-white text-sm"
                                    )
                            else:
                                ui.label("  None").classes(
                                    "!text-black dark:!text-white text-sm"
                                )

                            ui.label("Add/Update a room preference:").classes(
                                "!text-black dark:!text-white mt-2"
                            )
                            room_pref_feedback = ui.label("").classes(
                                "text-md !text-black dark:!text-white"
                            )

                            available_rooms = controller.get_available_rooms()
                            if available_rooms:
                                with ui.row().classes("gap-4 items-center flex-wrap"):
                                    room_select = ui.select(
                                        options=available_rooms, label="Room"
                                    ).classes("w-48")
                                    room_weight_input = ui.number(
                                        label="Weight (0-10)", min=0, max=10, value=5
                                    ).classes("w-32")

                                    def save_room_pref():
                                        if not room_select.value:
                                            room_pref_feedback.set_text(
                                                "Please select a room."
                                            )
                                            room_pref_feedback.classes(
                                                replace="text-md text-red-600"
                                            )
                                            return
                                        val = selected_faculty["value"]
                                        if not val:
                                            return
                                        new_prefs = dict(val.room_preferences)
                                        new_prefs[room_select.value] = int(
                                            room_weight_input.value
                                        )
                                        apply(
                                            "room_preferences",
                                            new_prefs,
                                            room_pref_feedback,
                                        )

                                    ui.button("Save").props(
                                        "rounded color=black text-color=white no-caps"
                                    ).on("click", save_room_pref)

                                if f.room_preferences:
                                    ui.label("Remove a room preference:").classes(
                                        "!text-black dark:!text-white mt-2"
                                    )
                                    with ui.row().classes("gap-4 items-center"):
                                        remove_room_select = ui.select(
                                            options=list(f.room_preferences.keys()),
                                            label="Room to Remove",
                                        ).classes("w-48")

                                        def remove_room_pref():
                                            if not remove_room_select.value:
                                                return
                                            val = selected_faculty["value"]
                                            if not val:
                                                return
                                            new_prefs = dict(val.room_preferences)
                                            new_prefs.pop(
                                                remove_room_select.value, None
                                            )
                                            apply(
                                                "room_preferences",
                                                new_prefs,
                                                room_pref_feedback,
                                            )

                                        ui.button("Remove").props(
                                            "rounded color=red text-color=white no-caps"
                                        ).on("click", remove_room_pref)
                            else:
                                ui.label(
                                    "No rooms available in configuration."
                                ).classes("!text-black dark:!text-white text-sm")

                        ui.separator()

                        # --- Lab Preferences ---
                        with ui.column().classes("w-full gap-2"):
                            ui.label("Lab Preferences").classes(
                                "!text-black dark:!text-white font-bold text-lg"
                            )
                            if f.lab_preferences:
                                for lab, weight in f.lab_preferences.items():
                                    ui.label(f"  {lab}: {weight}").classes(
                                        "!text-black dark:!text-white text-sm"
                                    )
                            else:
                                ui.label("  None").classes(
                                    "!text-black dark:!text-white text-sm"
                                )

                            ui.label("Add/Update a lab preference:").classes(
                                "!text-black dark:!text-white mt-2"
                            )
                            lab_pref_feedback = ui.label("").classes(
                                "text-md !text-black dark:!text-white"
                            )

                            available_labs = controller.get_available_labs()
                            if available_labs:
                                with ui.row().classes("gap-4 items-center flex-wrap"):
                                    lab_select = ui.select(
                                        options=available_labs, label="Lab"
                                    ).classes("w-48")
                                    lab_weight_input = ui.number(
                                        label="Weight (0-10)", min=0, max=10, value=5
                                    ).classes("w-32")

                                    def save_lab_pref():
                                        if not lab_select.value:
                                            lab_pref_feedback.set_text(
                                                "Please select a lab."
                                            )
                                            lab_pref_feedback.classes(
                                                replace="text-md text-red-600"
                                            )
                                            return
                                        val = selected_faculty["value"]
                                        if not val:
                                            return
                                        new_prefs = dict(val.lab_preferences)
                                        new_prefs[lab_select.value] = int(
                                            lab_weight_input.value
                                        )
                                        apply(
                                            "lab_preferences",
                                            new_prefs,
                                            lab_pref_feedback,
                                        )

                                    ui.button("Save").props(
                                        "rounded color=black text-color=white no-caps"
                                    ).on("click", save_lab_pref)

                                if f.lab_preferences:
                                    ui.label("Remove a lab preference:").classes(
                                        "!text-black dark:!text-white mt-2"
                                    )
                                    with ui.row().classes("gap-4 items-center"):
                                        remove_lab_select = ui.select(
                                            options=list(f.lab_preferences.keys()),
                                            label="Lab to Remove",
                                        ).classes("w-48")

                                        def remove_lab_pref():
                                            if not remove_lab_select.value:
                                                return
                                            val = selected_faculty["value"]
                                            if not val:
                                                return
                                            new_prefs = dict(val.lab_preferences)
                                            new_prefs.pop(remove_lab_select.value, None)
                                            apply(
                                                "lab_preferences",
                                                new_prefs,
                                                lab_pref_feedback,
                                            )

                                        ui.button("Remove").props(
                                            "rounded color=red text-color=white no-caps"
                                        ).on("click", remove_lab_pref)
                            else:
                                ui.label("No labs available in configuration.").classes(
                                    "!text-black dark:!text-white text-sm"
                                )

            def on_select(e):
                if not e.value or e.value not in faculty_options:
                    form_card.set_visibility(False)
                    return
                f = faculty_options[e.value]
                selected_faculty["value"] = f
                form_card.clear()
                form_card.set_visibility(True)
                build_form(f)

            ui.select(
                options=list(faculty_options.keys()),
                label="Select Faculty Member",
                on_change=on_select,
            ).props("label-color=grey-7").classes("w-full max-w-2xl text-xl")
            form_card
            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/faculty")
            )

    @ui.page("/faculty/delete")
    @staticmethod
    def faculty_delete():
        """
        Displays the GUI for deleting a faculty member.

        Loads all faculty from FacultyModel and displays them as cards.
        Each card has a Delete button that opens a confirmation dialog
        before calling controllers delete_faculty. The list refreshes after
        each deletion.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/faculty"):
            return
        from views.gui_view import GUIView

        ui.query("body").style("background-color: var(--q-delete)").classes(
            "dark:!bg-black"
        )

        if GUIView.controller is None:
            return
        controller = GUIView.controller.faculty_controller

        with ui.column().classes("w-full items-center pt-12 pb-12 gap-4"):
            with ui.row().classes("w-full max-w-2xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
            ui.label("Delete Faculty").classes(
                "text-4xl mb-6 !text-black dark:!text-white"
            )

            container = ui.column().classes("w-full max-w-lg gap-3 items-center")
            status = ui.label("").classes("text-sm !text-black dark:!text-white")

            def build(c):
                c.clear()
                faculty_list = controller.get_all_faculty()
                with c:
                    if not faculty_list:
                        ui.label("No faculty to delete.").classes("text-gray-600")
                        return
                    for faculty in faculty_list:
                        is_ft = faculty.maximum_credits >= 12
                        tag_label = "Full Time" if is_ft else "Adjunct"
                        with ui.card().classes("w-full px-5 py-4"):
                            with ui.row().classes(
                                "w-full items-center justify-between"
                            ):
                                with ui.column().classes("gap-1"):
                                    ui.label(faculty.name).classes(
                                        "text-base font-semibold"
                                    )
                                    ui.label(
                                        f"{tag_label}  ·  Max {faculty.maximum_credits} credits  ·  Limit {faculty.unique_course_limit} courses"
                                    ).classes("text-xs text-gray-500")

                                def make_delete_handler(name):
                                    def _delete():
                                        with (
                                            ui.dialog() as dlg,
                                            ui.card().classes(
                                                "p-8 gap-4 items-center text-center"
                                            ),
                                        ):
                                            ui.label(f"Delete '{name}'?").classes(
                                                "text-xl font-bold"
                                            )
                                            with ui.row().classes("gap-4 mt-4"):
                                                ui.button(
                                                    "Cancel", on_click=dlg.close
                                                ).props(
                                                    "rounded color=black text-color=white no-caps"
                                                )

                                                def confirm(d=dlg, n=name):
                                                    ok, message = (
                                                        controller.delete_faculty(n)
                                                    )
                                                    d.close()
                                                    status.set_text(
                                                        f"✓ '{n}' deleted."
                                                        if ok
                                                        else f"⚠ Could not delete '{n}'."
                                                    )
                                                    build(container)

                                                ui.button(
                                                    "Delete", on_click=confirm
                                                ).props(
                                                    "rounded color=red text-color=white no-caps"
                                                )
                                        dlg.open()

                                    return _delete

                                ui.button(
                                    "Delete", on_click=make_delete_handler(faculty.name)
                                ).props("flat color=red no-caps")

            build(container)

            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl mt-4 dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/faculty")
            )

    @ui.page("/faculty/view")
    @staticmethod
    def faculty_view():
        """
        Displays faculty schedules in a calendar view.

        Allows users to upload or generate schedules and view them as
        calendar grids organized by faculty member.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/faculty"):
            return
        from views.gui_view import GUIView

        ui.query("body").style("background-color: var(--q-primary)").classes(
            "dark:!bg-black"
        )

        if GUIView.controller is None:
            return

        async def handle_upload(e):
            """Handle file upload for schedule import."""
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
                    _faculty_calendar_state.schedules = schedules
                    _faculty_calendar_state.current_index = 0
                    ui.notify(f"Imported {e.file.name}")
                    _reload_calendar()
                else:
                    ui.notify(f"No schedules found in {e.file.name}", type="warning")
            except Exception as ex:
                ui.notify(f"Import failed: {ex}", type="negative")

        with ui.dialog() as upload_dialog:
            with ui.card().classes("w-[400px]"):
                ui.label("Import Schedule").classes("text-lg font-bold")
                ui.upload(
                    label="Select schedule file (CSV or JSON)",
                    multiple=False,
                    auto_upload=True,
                    on_upload=handle_upload,
                ).classes("w-full")
                ui.button("Close", on_click=upload_dialog.close)

        calendar_container = ui.column().classes("w-full gap-4")
        faculty_filter_select = None

        def _render_faculty_calendars(faculty_filter: str | None = None):
            """Render calendar grids for each faculty member."""
            calendar_container.clear()

            if not _faculty_calendar_state.schedules:
                with calendar_container:
                    ui.label("No schedules loaded.").classes(
                        "text-gray-600 dark:!text-gray-300 p-4"
                    )
                return

            current_schedule = _faculty_calendar_state.schedules[
                _faculty_calendar_state.current_index
            ]
            calendar_data = _build_calendar_grid_by_faculty(
                current_schedule, faculty_filter=faculty_filter
            )

            if not calendar_data:
                with calendar_container:
                    ui.label("No schedule data available.").classes(
                        "text-gray-600 dark:!text-gray-300 p-4"
                    )
                return

            days, hourly_slots = _extract_calendar_metadata(current_schedule)

            # Build color map for courses
            all_courses = [ci.course_str.rsplit(".", 1)[0] for ci in current_schedule]
            course_color_map = _build_color_map(all_courses)

            for faculty in sorted(calendar_data.keys()):
                # Collect time slots for this faculty
                time_slots_set: set[str] = set()
                for day_data in calendar_data[faculty].values():
                    time_slots_set.update(day_data.keys())
                time_slots = _sort_time_slots(time_slots_set)

                with calendar_container:
                    with ui.card().classes("w-full p-4 mb-4"):
                        ui.label(faculty).classes(
                            "text-lg font-bold mb-3 !text-black dark:!text-white"
                        )

                        # Track rendered courses by day to show as connected blocks
                        rendered_courses_by_day: dict[str, set[str]] = {
                            day: set() for day in days
                        }

                        # Calendar grid
                        with ui.column().classes("w-full overflow-x-auto"):
                            # Header row with days
                            with ui.row().classes("w-full gap-1"):
                                ui.label("Time").classes(
                                    "font-semibold w-32 p-2 bg-gray-100 dark:bg-gray-700 text-sm"
                                )
                                for day in days:
                                    ui.label(day).classes(
                                        "flex-1 font-semibold p-2 bg-gray-100 dark:bg-gray-700 text-center text-sm"
                                    )

                            # Time slot rows
                            for time_slot in time_slots:
                                time_display = _extract_time_portion(time_slot)
                                with ui.row().classes("w-full gap-1"):
                                    ui.label(time_display).classes(
                                        "font-semibold w-32 p-2 bg-gray-50 dark:bg-gray-800 overflow-auto text-xs"
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
                                                course_id = course_info.get(
                                                    "full_course_str", ""
                                                )

                                                # Skip if already rendered in this day (render as single block)
                                                if (
                                                    course_id
                                                    in rendered_courses_by_day[day]
                                                ):
                                                    continue

                                                rendered_courses_by_day[day].add(
                                                    course_id
                                                )

                                                # Calculate span for this course
                                                course_time_str = None
                                                for ci in current_schedule:
                                                    if (
                                                        ci.course_str == course_id
                                                        and ci.faculty == faculty
                                                    ):
                                                        for (
                                                            t_idx,
                                                            time_instance,
                                                        ) in enumerate(ci.times):
                                                            t_str = str(
                                                                time_instance
                                                            ).strip()
                                                            if (
                                                                _extract_day(t_str)
                                                                == day
                                                            ):
                                                                course_time_str = t_str
                                                                break
                                                        if course_time_str:
                                                            break

                                                span = 1
                                                if course_time_str:
                                                    span = _calculate_course_span(
                                                        course_time_str, hourly_slots
                                                    )

                                                # Color by course code
                                                color_tuple = course_color_map.get(
                                                    course_info["course"],
                                                    COURSE_COLORS[0],
                                                )
                                                bg_color = _get_color_classes(
                                                    f"{color_tuple[0]} {color_tuple[1]}"
                                                )
                                                with (
                                                    ui.card()
                                                    .classes(
                                                        f"{bg_color} p-1.5 text-sm w-full"
                                                    )
                                                    .style(
                                                        f"min-height: {20 * span * 5}px;"
                                                        if span > 1
                                                        else ""
                                                    )
                                                ):
                                                    ui.label(
                                                        course_info["course"]
                                                    ).classes("font-bold text-sm")
                                                    ui.label(
                                                        f"Section: {course_info['section']}"
                                                    ).classes("text-xs")
                                                    ui.label(
                                                        f"Location: {course_info['location']}"
                                                    ).classes("text-xs")
                                                    ui.label(
                                                        f"Type: {course_info['type']}"
                                                    ).classes("text-xs italic")

        def _reload_calendar():
            """Reload calendar with current filters."""
            faculty_val = None
            if faculty_filter_select and hasattr(faculty_filter_select, "value"):
                faculty_val = faculty_filter_select.value
                if faculty_val == "All":
                    faculty_val = None
            _render_faculty_calendars(faculty_filter=faculty_val)

        def on_faculty_filter(e):
            """Handle faculty filter change."""
            _reload_calendar()

        with ui.column().classes("w-full items-center pt-6 pb-24 px-4 gap-4"):
            with ui.row().classes("w-full max-w-6xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )

            ui.label("Faculty Schedules").classes(
                "text-4xl mb-4 !text-black dark:!text-white"
            )

            # Control buttons
            with ui.row().classes("gap-2 mb-4"):
                ui.button("Import Schedule").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("dark:!bg-white dark:!text-black").on(
                    "click", upload_dialog.open
                )
                ui.button("Generate Schedule").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/run_scheduler")
                )

            # Faculty filter
            if _faculty_calendar_state.schedules:
                current_schedule = _faculty_calendar_state.schedules[
                    _faculty_calendar_state.current_index
                ]
                faculty_options = ["All"] + sorted(
                    {ci.faculty for ci in current_schedule}
                )
                faculty_filter_select = ui.select(
                    options=faculty_options,
                    value="All",
                    label="Filter by Faculty",
                ).classes("w-48")
                faculty_filter_select.on_value_change(on_faculty_filter)

            # Calendar container
            calendar_container

            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-32 h-12 text-base dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/faculty")
            )
