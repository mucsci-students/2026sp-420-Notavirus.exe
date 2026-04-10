# views/room_gui_view.py
"""
RoomGUIView - Graphical-user interface for room interactions

  MVC rules followed in this file:
    - No class-level model or controller attributes.
    - No Model methods are called directly.
    - All data operations go through GUIView.controller.room_controller.
    - Save orchestration is delegated to GUIView.controller methods.
"""

from typing import Any
from nicegui import ui
from views.gui_theme import GUITheme
from views.gui_utils import require_config
from views.schedule_gui_view import (
    _extract_calendar_metadata,
    _build_calendar_grid_by_room,
    _sort_time_slots,
    _extract_time_portion,
    _build_color_map,
    _get_color_classes,
    _extract_day,
    _calculate_course_span,
    COURSE_COLORS,
)
#    Views should never import Controller classes directly.


class _RoomCalendarState:
    """Holds calendar state for room view."""

    def __init__(self):
        self.schedules: list[list] = []
        self.current_index: int = 0


_room_calendar_state = _RoomCalendarState()


class RoomGUIView:
    # Class for Room GUI View
    room_controller: Any = None
    room_model: Any = None

    @ui.page("/room")
    @staticmethod
    def room():
        """
        Displays the GUI for the Room hub page with navigation buttons.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/"):
            return
        with ui.column().classes("w-full items-center pt-12 pb-12 font-sans"):
            ui.label("Room").classes("text-4xl mb-10 !text-black dark:!text-white")
            ui.button("Add Room").props("rounded text-color=white no-caps").classes(
                "w-80 h-16 text-xl"
            ).style(
                "background: linear-gradient(135deg, var(--q-roomBegin), var(--q-roomEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/room/add"))
            ui.button("Modify Room").props("rounded text-color=white no-caps").classes(
                "w-80 h-16 text-xl"
            ).style(
                "background: linear-gradient(135deg, var(--q-roomBegin), var(--q-roomEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/room/modify"))
            ui.button("Delete Room").props("rounded text-color=white no-caps").classes(
                "w-80 h-16 text-xl"
            ).style(
                "background: linear-gradient(135deg, var(--q-roomBegin), var(--q-roomEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/room/delete"))
            ui.button("View Room").props("rounded text-color=white no-caps").classes(
                "w-80 h-16 text-xl"
            ).style(
                "background: linear-gradient(135deg, var(--q-roomBegin), var(--q-roomEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/room/view"))
            ui.space()
            ui.button("Back").props(
                "rounded color=backbtn text-color=white no-caps"
            ).classes(
                "w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]"
            ).on("click", lambda: ui.navigate.to("/"))

    @ui.page("/room/add")
    @staticmethod
    def room_add():
        """
        Displays the GUI for adding a room.

        Allows the user to enter a room name and number. Save adds the
        room to memory and immediately persists it to the configuration file.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/room"):
            return
        from views.gui_view import GUIView

        if GUIView.controller is None:
            return
        controller = GUIView.controller.room_controller

        with ui.column().classes("gap-6 items-center w-full"):
            with ui.row().classes("w-full max-w-2xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
            ui.label("Add Room").classes("text-3xl !text-black dark:!text-white")
            ui.label("Enter a room name and number below. Press Save to add.").classes(
                "text-lg !text-black dark:!text-white text-center max-w-xl"
            )

            rooms_container = ui.column()

            def refresh_rooms():
                rooms_container.clear()
                with rooms_container:
                    ui.label("Existing Rooms:").classes("!text-black dark:!text-white")
                    with ui.list():
                        for r in controller.get_all_rooms():
                            ui.item(r).classes("!text-black dark:!text-white")

            refresh_rooms()

            room_input = ui.input("Room name and number")
            result_label = ui.label().classes("!text-black dark:!text-white")

            ui.button("Save").on("click", lambda: handle_save()).props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black")
            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/room")
            )

            def handle_save():
                """
                Adds the room to memory and saves to config immediately.

                Parameters:
                    None
                Returns:
                    None
                """

                success = RoomGUIView.room_controller.model.add_room(room_input.value)
                if success:
                    result_label.set_text("Room added.")
                    refresh_rooms()

    @ui.page("/room/modify")
    @staticmethod
    def room_modify():
        """
        Displays the GUI for modifying a room.

        Allows the user to select an existing room and enter a new name.
        Save modifies the room in memory and immediately persists the change
        to the configuration file.

        Parameters:
            None
        Returns:
            None
        """

        GUITheme.applyTheming()
        if not require_config(back_url="/room"):
            return
        from views.gui_view import GUIView

        if GUIView.controller is None:
            return
        controller = GUIView.controller.room_controller

        with ui.column().classes("gap-6 items-center w-full"):
            with ui.row().classes("w-full max-w-2xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
            ui.label("Modify Room").classes("text-3xl !text-black dark:!text-white")
            ui.label(
                "Select a room to modify, then enter a new name. Press Save to apply changes."
            ).classes("text-lg !text-black dark:!text-white text-center max-w-xl")

            rooms = controller.get_all_rooms()
            selected_room = ui.select(options=rooms, label="Select Room")
            new_name = ui.input("New Room Name")
            result_label = ui.label().classes("!text-black dark:!text-white")

            def refresh_select():
                updated = controller.get_all_rooms()
                selected_room.set_options(updated)
                selected_room.set_value(None)

            def handle_save():
                """
                Modifies the selected room in memory and saves to config immediately.

                Parameters:
                    None
                Returns:
                    None
                """

                if not selected_room.value:
                    result_label.set_text("Select a room first.")
                    return
                if not new_name.value or not new_name.value.strip():
                    result_label.set_text("New room name cannot be empty.")
                    return
                success, message = controller.modify_room(
                    selected_room.value, new_name.value
                )
                result_label.set_text(message)
                if success:
                    result_label.set_text("Room modified.")
                    refresh_select()

            ui.button("Save").on("click", handle_save).props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black")
            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/room")
            )

    @ui.page("/room/delete")
    @staticmethod
    def room_delete():
        """
        Displays the GUI for deleting a room.

        Allows the user to select a room and delete it. Deletion is immediately
        persisted to the configuration file.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/room"):
            return

        ui.add_css("""
            .body--dark .q-field__control { background-color: #383838 !important; border-color: white !important; }
            .body--dark .q-field__native, .body--dark .q-field__label,
            .body--dark .q-field__input, .body--dark .q-select__dropdown-icon { color: white !important; }
            .body--dark .q-item__label { color: white !important; }
        """)

        rooms = (
            RoomGUIView.room_controller.model.get_all_rooms()
            if RoomGUIView.room_controller
            else []
        )

        with ui.column().classes("gap-6 items-center w-full"):
            with ui.row().classes("w-full max-w-2xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
            ui.label("Delete Room").classes(
                "text-4xl mb-10 !text-black dark:!text-white"
            )
            ui.label("Select a room to delete.").classes(
                "text-lg !text-black dark:!text-white text-center max-w-xl"
            )

            selected_room = (
                ui.select(rooms, label="Select Room to Delete")
                .props("rounded outlined color=black")
                .classes("w-80")
            )
            result_label = ui.label("").classes(
                "text-base !text-black dark:!text-white"
            )

            def delete():
                """
                Deletes the selected room and saves to config immediately.

                Parameters:
                    None
                Returns:
                    None
                """
                try:
                    success, message = RoomGUIView.room_controller.delete_room(
                        selected_room.value
                    )
                    result_label.set_text(message)
                    if success:
                        updated_rooms = (
                            RoomGUIView.room_controller.model.get_all_rooms()
                        )
                        selected_room.set_options(updated_rooms)
                        selected_room.set_value(None)
                except Exception as e:
                    result_label.set_text(f"Error: {e}")

            ui.button("Delete").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", delete
            )
            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/room")
            )

    @ui.page("/room/view")
    @staticmethod
    def room_view():
        """
        Displays room schedules in a calendar view.

        Allows users to upload or generate schedules and view them as
        calendar grids organized by room/lab.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/room"):
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
                    _room_calendar_state.schedules = schedules
                    _room_calendar_state.current_index = 0
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
        room_filter_select = None

        def _render_room_calendars(room_filter: str | None = None):
            """Render calendar grids for each room/lab."""
            calendar_container.clear()

            if not _room_calendar_state.schedules:
                with calendar_container:
                    ui.label("No schedules loaded.").classes(
                        "text-gray-600 dark:!text-gray-300 p-4"
                    )
                return

            current_schedule = _room_calendar_state.schedules[
                _room_calendar_state.current_index
            ]
            calendar_data = _build_calendar_grid_by_room(
                current_schedule, location_filter=room_filter
            )

            if not calendar_data:
                with calendar_container:
                    ui.label("No schedule data available.").classes(
                        "text-gray-600 dark:!text-gray-300 p-4"
                    )
                return

            days, hourly_slots = _extract_calendar_metadata(current_schedule)

            # Build color map for faculty
            all_faculty = [ci.faculty for ci in current_schedule]
            faculty_color_map = _build_color_map(all_faculty)

            for location in sorted(calendar_data.keys()):
                # Collect time slots for this location
                time_slots_set: set[str] = set()
                for day_data in calendar_data[location].values():
                    time_slots_set.update(day_data.keys())
                time_slots = _sort_time_slots(time_slots_set)

                with calendar_container:
                    with ui.card().classes("w-full p-4 mb-4"):
                        ui.label(location).classes(
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
                                            calendar_data[location]
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
                                                        and ci.faculty
                                                        == course_info["faculty"]
                                                        and (
                                                            (
                                                                ci.room == location
                                                                and course_info["type"]
                                                                == "Lecture"
                                                            )
                                                            or (
                                                                ci.lab == location
                                                                and course_info["type"]
                                                                == "Lab"
                                                            )
                                                        )
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

                                                # Color by faculty
                                                color_tuple = faculty_color_map.get(
                                                    course_info["faculty"],
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
                                                        f"Instructor: {course_info['faculty']}"
                                                    ).classes("text-xs")
                                                    ui.label(
                                                        f"Type: {course_info['type']}"
                                                    ).classes("text-xs italic")

        def _reload_calendar():
            """Reload calendar with current filters."""
            room_val = None
            if room_filter_select and hasattr(room_filter_select, "value"):
                room_val = room_filter_select.value
                if room_val == "All":
                    room_val = None
            _render_room_calendars(room_filter=room_val)

        def on_room_filter(e):
            """Handle room filter change."""
            _reload_calendar()

        with ui.column().classes("w-full items-center pt-6 pb-24 px-4 gap-4"):
            with ui.row().classes("w-full max-w-6xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )

            ui.label("Room Schedules").classes(
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

            # Room filter
            if _room_calendar_state.schedules:
                current_schedule = _room_calendar_state.schedules[
                    _room_calendar_state.current_index
                ]
                room_options = ["All"] + sorted(
                    {ci.room for ci in current_schedule if ci.room}
                    | {ci.lab for ci in current_schedule if ci.lab}
                )
                room_filter_select = ui.select(
                    options=room_options,
                    value="All",
                    label="Filter by Room/Lab",
                ).classes("w-48")
                room_filter_select.on_value_change(on_room_filter)

            # Calendar container
            calendar_container

            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-32 h-12 text-base dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/room")
            )
