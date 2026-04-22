# views/gui_view.py
"""
GUIView - Graphical-user interface for all user interactions

This view class handles all files for the GUI that don't have
their own files (i.e. the landing page, the navigation page, and currently including
print config, run scheduler, and display schedules)
"""

from typing import Any
import re
from nicegui import ui
from views.gui_theme import GUITheme
from views.gui_utils import require_config
from time_config_data_class import time_config_data
from scheduler import TimeBlock, Meeting
from scheduler.config import ClassPattern


class GUIView:
    config_path: Any = None
    #    The View holds exactly one reference: the Controller.
    #    All data is fetched through the Controller at render time.
    #    No model references, no sub-controller references are stored here.
    controller: Any = None

    @ui.page("/")
    @staticmethod
    def home():
        GUITheme.applyTheming()

        # Styling for loading a configuration button
        ui.add_css("""
            .load-dialog, .load-dialog *,
            .load-dialog .q-field__label,
            .load-dialog .q-field__native,
            .load-dialog .q-uploader__title,
            .load-dialog .q-uploader__subtitle,
            .load-dialog .q-uploader__header,
            .load-dialog .q-uploader__list {
                color: black !important;
            }
            .load-dialog .q-uploader {
                background: #f5f5f5 !important;
                color: black !important;
            }
            .load-dialog .q-uploader__file-status,
            .load-dialog .q-uploader__file,
            .load-dialog .q-uploader__list {
                display: none !important;
            }
            .load-dialog .q-uploader__subtitle {
                display: none !important;
            }
        """)

        with ui.column().classes("w-full items-center pt-12 pb-12 font-sans gap-10"):
            ui.label("Scheduler").classes("text-4xl !text-black dark:!text-white")

            btn_classes = "w-52 h-14 text-lg !bg-black dark:!bg-white !text-white dark:!text-black"
            header_classes = "text-sm font-semibold !text-gray-500 dark:!text-gray-400 tracking-widest uppercase text-center pb-2"

            with ui.row().classes("gap-16 items-start justify-center"):
                # Setup — 2×3 grid
                with ui.column().classes("items-center gap-2"):
                    ui.label("Setup").classes(header_classes)
                    with ui.element("table").classes(
                        "border-separate border-spacing-[40px]"
                    ):
                        with ui.element("tbody"):
                            for row in [
                                ("Faculty", "/faculty", "Room", "/room"),
                                ("Course", "/course", "Lab", "/lab"),
                                ("Conflict", "/conflict", "Time Slots", "/time_config"),
                            ]:
                                with ui.element("tr"):
                                    for label, route in [
                                        (row[0], row[1]),
                                        (row[2], row[3]),
                                    ]:
                                        with ui.element("td"):
                                            ui.button(label).props(
                                                "rounded no-caps"
                                            ).classes(btn_classes).on(
                                                "click",
                                                lambda r=route: ui.navigate.to(r),
                                            )

                # Run — 2×3 with Print Config solo at bottom
                with ui.column().classes("items-center gap-2"):
                    ui.label("Run").classes(header_classes)
                    with ui.element("table").classes(
                        "border-separate border-spacing-[40px]"
                    ):
                        with ui.element("tbody"):
                            with ui.element("tr"):
                                with ui.element("td"):
                                    ui.button("Generate Schedules").props(
                                        "rounded no-caps"
                                    ).classes(btn_classes).on(
                                        "click",
                                        lambda: ui.navigate.to("/run_scheduler"),
                                    )
                                with ui.element("td"):
                                    ui.button("Display Schedules").props(
                                        "rounded no-caps"
                                    ).classes(btn_classes).on(
                                        "click",
                                        lambda: ui.navigate.to("/display_schedules"),
                                    )
                            with ui.element("tr"):
                                with ui.element("td"):
                                    ui.button("Load Configuration").props(
                                        "rounded no-caps"
                                    ).classes(btn_classes).on(
                                        "click", lambda: load_dialog.open()
                                    )
                                with ui.element("td"):
                                    ui.button("Export Configuration").props(
                                        "rounded no-caps"
                                    ).classes(btn_classes).on(
                                        "click", lambda: GUIView.export_configuration()
                                    )
                            with ui.element("tr"):
                                with (
                                    ui.element("td")
                                    .props("colspan=2")
                                    .classes("text-center")
                                ):
                                    ui.button("Print Configuration").props(
                                        "rounded no-caps"
                                    ).classes(btn_classes).on(
                                        "click", lambda: ui.navigate.to("/print_config")
                                    )

        with ui.dialog() as load_dialog:
            with (
                ui.card().classes("w-96 gap-4 load-dialog").style("background: white;")
            ):
                ui.label("Load Configuration (.json)").style(
                    "color: black !important; font-size: 1.1rem; font-weight: 600;"
                )
                status_label = ui.label("").style("color: black !important;")

                async def handle_upload(e):
                    """
                       The View's only job here is:
                         1. Write the raw file bytes to disk.
                         2. Tell the Controller the path.
                         3. React to success or failure.

                    All model construction and sub-controller wiring happens
                    inside Controller.load_config() — never here.
                    """
                    from models.config_model import ConfigModel
                    from models.faculty_model import FacultyModel
                    from models.course_model import CourseModel
                    from models.conflict_model import ConflictModel
                    from models.lab_model import LabModel
                    from models.room_model import RoomModel
                    from models.scheduler_model import SchedulerModel
                    from controllers.faculty_controller import FacultyController
                    from controllers.course_controller import CourseController
                    from controllers.conflict_controller import ConflictController
                    from controllers.lab_controller import LabController
                    from controllers.room_controller import RoomController
                    from controllers.schedule_controller import ScheduleController
                    from controllers.chatbot_controller import ChatbotController
                    from views.chatbot_gui_view import ChatbotGUIView
                    from views.course_gui_view import CourseGUIView
                    from views.faculty_gui_view import FacultyGUIView
                    from views.conflict_gui_view import ConflictGUIView
                    from views.lab_gui_view import LabGUIView
                    from views.room_gui_view import RoomGUIView
                    from views.schedule_gui_view import ScheduleGUIView
                    from views.schedule_gui_view import _state as _schedule_state

                    try:
                        real_name = e.file.name
                        file_path = real_name

                        with open(file_path, "wb") as f:
                            f.write(await e.file.read())

                        ctrl = GUIView.controller
                        # Use the GUIView instance as view — works whether or not
                        # a config was previously loaded
                        view = ctrl.view if (ctrl and ctrl.view) else GUIView()

                        new_config = ConfigModel(file_path)
                        new_faculty_model = FacultyModel(new_config)
                        new_course_model = CourseModel(new_config)
                        new_conflict_model = ConflictModel(new_config)
                        new_lab_model = LabModel(new_config)
                        new_room_model = RoomModel(new_config)
                        new_scheduler_model = SchedulerModel(new_config)

                        new_faculty_ctrl = FacultyController(new_faculty_model, view)
                        new_course_ctrl = CourseController(new_course_model, new_config)
                        new_conflict_ctrl = ConflictController(new_conflict_model, view)
                        new_lab_ctrl = LabController(new_lab_model, view)
                        new_room_ctrl = RoomController(new_room_model, view)
                        new_schedule_ctrl = ScheduleController(
                            new_scheduler_model, view
                        )
                        new_chatbot_ctrl = ChatbotController(
                            new_lab_model,
                            new_room_model,
                            new_course_model,
                            new_faculty_model,
                            new_conflict_model,
                        )

                        ctrl.config_model = new_config
                        ctrl.faculty_model = new_faculty_model
                        ctrl.course_model = new_course_model
                        ctrl.conflict_model = new_conflict_model
                        ctrl.lab_model = new_lab_model
                        ctrl.room_model = new_room_model
                        ctrl.scheduler_model = new_scheduler_model
                        ctrl.faculty_controller = new_faculty_ctrl
                        ctrl.course_controller = new_course_ctrl
                        ctrl.conflict_controller = new_conflict_ctrl
                        ctrl.lab_controller = new_lab_ctrl
                        ctrl.room_controller = new_room_ctrl
                        ctrl.schedule_controller = new_schedule_ctrl
                        ctrl.chatbot_controller = new_chatbot_ctrl
                        ctrl.view = view
                        ctrl.config_path = file_path

                        FacultyGUIView.faculty_model = new_faculty_model
                        FacultyGUIView.faculty_controller = new_faculty_ctrl

                        CourseGUIView.course_model = new_course_model
                        CourseGUIView.course_controller = new_course_ctrl

                        ConflictGUIView.conflict_model = new_conflict_model
                        ConflictGUIView.conflict_controller = new_conflict_ctrl

                        LabGUIView.lab_model = new_lab_model
                        LabGUIView.lab_controller = new_lab_ctrl
                        LabGUIView._lab_controller = new_lab_ctrl

                        RoomGUIView.room_model = new_room_model
                        RoomGUIView.room_controller = new_room_ctrl

                        _schedule_state._scheduler_model = new_scheduler_model
                        ScheduleGUIView.schedule_controller = new_schedule_ctrl

                        ChatbotGUIView._chatbot_controller = new_chatbot_ctrl

                        GUIView.config_path = file_path
                        GUIView.controller.config_path = file_path

                        GUIView.config_path = file_path
                        GUIView.controller.config_path = file_path

                        status_label.style("color: green !important;")
                        status_label.set_text(f"✓ Loaded: {e.file.name}")
                        ui.notify("Configuration loaded successfully!", type="positive")
                        load_dialog.close()

                    except Exception as ex:
                        status_label.style("color: red !important;")
                        status_label.set_text(f"Error: {ex}")
                        import os

                        try:
                            os.remove(file_path)
                        except Exception:
                            pass

                ui.upload(
                    label="Select JSON file",
                    auto_upload=True,
                    max_files=1,
                    on_upload=handle_upload,
                ).classes("w-full").style("color: black !important;")

                ui.button("Cancel").props("flat no-caps").style(
                    "color: black !important;"
                ).on("click", load_dialog.close)

    @staticmethod
    def export_configuration():
        """
        Exports the configuration file.
        Asks the Controller to save current in-memory state to disk, then downloads.
        """
        try:
            if GUIView.controller is None:
                return
            success = GUIView.controller.save_configuration()
            if success:
                import os

                if GUIView.controller is None:
                    return
                config_path = GUIView.controller.config_path
                real_name = os.path.basename(config_path)
                ui.download(config_path, real_name)
                ui.notify("Configuration exported successfully!", type="positive")
            else:
                ui.notify("Error saving configuration.", type="negative")
        except Exception as e:
            ui.notify(f"Failed to export configuration: {e}", type="negative")

    @ui.page("/print_config")
    @staticmethod
    def print_config():
        """
        Displays the GUI for printing the config file.

        If no configuration is loaded, shows a message and a Back button
        instead of attempting to render config data.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query("body").style("background-color: var(--q-primary)").classes(
            "dark:!bg-black"
        )

        # Adds shading/color to whatever item is active in the drop down in print config
        ui.add_css("""
            .print-config-expansion.q-expansion-item--expanded
                > .q-expansion-item__container
                > .q-item {
                background-color: #f3f4f6 !important;
            }
            body.body--dark .print-config-expansion.q-expansion-item--expanded
                > .q-expansion-item__container
                > .q-item {
                background-color: rgba(255, 255, 255, 0.1) !important;
            }
        """)

        # Read data through the Controller, not by holding a model reference.
        ctrl = GUIView.controller
        cm = ctrl.config_model if ctrl else None

        with ui.column().classes("w-full items-center pt-12 pb-12 gap-6"):
            ui.label("Configuration").classes(
                "text-4xl mb-10 !text-black dark:!text-white"
            )

            # Output if you press print config and no config file is currently loaded
            if cm is None:
                ui.label("No configuration loaded.").classes(
                    "text-xl italic !text-gray-500 dark:!text-gray-400"
                )
                ui.label(
                    "Return to the home page and use Load Configuration to load a file."
                ).classes("text-base !text-gray-400 dark:!text-gray-500")
                ui.button("Back").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("w-80 h-16 text-xl mt-6 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
                return

            with ui.expansion("Rooms", icon="meeting_room").classes(
                "w-3/4 !text-black dark:!text-white print-config-expansion"
            ):
                for room in cm.get_all_rooms():
                    ui.label(room).classes("!text-black dark:!text-white")

            with ui.expansion("Labs", icon="computer").classes(
                "w-3/4 !text-black dark:!text-white print-config-expansion"
            ):
                for lab in cm.get_all_labs():
                    ui.label(lab).classes("!text-black dark:!text-white")

            with ui.expansion("Courses", icon="book").classes(
                "w-3/4 !text-black dark:!text-white print-config-expansion"
            ):
                with ui.scroll_area().classes("w-full h-96"):
                    for course in cm.get_all_courses():
                        with ui.card().classes(
                            "w-full mb-2 !bg-white dark:!bg-gray-800"
                        ):
                            with ui.row().classes(
                                "w-full justify-between items-center"
                            ):
                                ui.label(course.course_id).classes(
                                    "font-bold text-lg !text-black dark:!text-white"
                                )
                                ui.label(f"{course.credits} credits").classes(
                                    "text-gray-500 dark:!text-gray-300"
                                )
                            with ui.row().classes("gap-4"):
                                ui.label(
                                    f"Rooms: {', '.join(course.room) or 'None listed'}"
                                ).classes("text-sm !text-black dark:!text-white")
                                ui.label(
                                    f"Labs: {', '.join(course.lab) or 'None'}"
                                ).classes("text-sm !text-black dark:!text-white")
                                ui.label(
                                    f"Faculty: {', '.join(course.faculty) or 'None listed'}"
                                ).classes("text-sm !text-black dark:!text-white")

            with ui.expansion("Faculty", icon="person").classes(
                "w-3/4 !text-black dark:!text-white print-config-expansion"
            ):
                for f in cm.get_all_faculty():
                    with ui.expansion(f.name).classes(
                        "w-full !text-black dark:!text-white print-config-expansion"
                    ):
                        ui.label(f"Max credits: {f.maximum_credits}").classes(
                            "!text-black dark:!text-white"
                        )
                        ui.label(f"Min credits: {f.minimum_credits}").classes(
                            "!text-black dark:!text-white"
                        )
                        ui.label(f"Max days: {f.maximum_days}").classes(
                            "!text-black dark:!text-white"
                        )
                        ui.label(
                            f"Unique course limit: {f.unique_course_limit}"
                        ).classes("!text-black dark:!text-white")
                        if f.mandatory_days:
                            ui.label(
                                f"Mandatory days: {', '.join(str(d) for d in f.mandatory_days)}"
                            ).classes("!text-black dark:!text-white")
                        for day, slots in f.times.items():
                            ui.label(
                                f"{day}: {', '.join(str(s) for s in slots) or 'Unavailable'}"
                            ).classes("!text-black dark:!text-white")
                        if f.course_preferences:
                            ui.label("Course preferences:").classes(
                                "font-semibold !text-black dark:!text-white"
                            )
                            for course, pref in f.course_preferences.items():
                                ui.label(f"  {course}: {pref}").classes(
                                    "!text-black dark:!text-white"
                                )
                        if f.room_preferences:
                            ui.label("Room preferences:").classes(
                                "font-semibold !text-black dark:!text-white"
                            )
                            for room, pref in f.room_preferences.items():
                                ui.label(f"  {room}: {pref}").classes(
                                    "!text-black dark:!text-white"
                                )
                        if f.lab_preferences:
                            ui.label("Lab preferences:").classes(
                                "font-semibold !text-black dark:!text-white"
                            )
                            for lab, pref in f.lab_preferences.items():
                                ui.label(f"  {lab}: {pref}").classes(
                                    "!text-black dark:!text-white"
                                )

            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/")
            )

    @ui.page("/time_config")
    @staticmethod
    # ─────────────────────────────────────────────
    # Main page
    # ─────────────────────────────────────────────

    def time_slot_config():
        """Full GUI for time slot configuration and class pattern management."""
        GUITheme.applyTheming()
        ui.query("body").style("background-color: var(--q-primary)").classes(
            "dark:!bg-black"
        )

        if not require_config(back_url="/"):
            return

        cm = getattr(GUIView.controller, "config_model", None)
        assert cm is not None

        time_config = time_config_data(cm.config.time_slot_config)
        _apply_css()

        ui.label("Time Slot Config").classes(
            "text-4xl mb-6 !text-black dark:!text-white text-center w-full"
        )

        days_container = ui.column().classes("w-full gap-4")
        patterns_container = ui.column().classes("w-full gap-4")

        def refresh_days():
            days_container.clear()
            render_days()

        def refresh_patterns():
            patterns_container.clear()
            render_patterns()

        # ── Days ──────────────────────────────────

        day_block_containers: dict = {}

        def render_days():
            day_block_containers.clear()
            with days_container:
                with ui.expansion("Available Days", icon="meeting_room").classes(
                    "w-full !text-black dark:!text-white time-config-expansion"
                ):
                    with ui.row().classes("w-full justify-between items-center mb-2"):
                        ui.label("Days").classes("text-lg !text-black dark:!text-white")
                        ui.button(icon="add").props("flat round").classes(
                            "!text-black dark:!text-white"
                        ).on(
                            "click",
                            lambda: _add_time_block_dialog(
                                time_config, render_day_blocks
                            ),
                        )
                    for day in time_config.get_days():
                        with ui.card().classes(
                            "w-full p-4 bg-gray-100 dark:bg-gray-800"
                        ):
                            ui.label(str(day)).classes(
                                "text-lg font-semibold mb-2 !text-black dark:!text-white"
                            )
                            day_block_containers[day] = ui.row().classes(
                                "w-full flex-wrap gap-4"
                            )
                        render_day_blocks(day)

        def render_day_blocks(day):
            container = day_block_containers[day]
            container.clear()
            blocks = time_config.get_time_blocks_for_day(day)
            with container:
                if not blocks:
                    ui.label("No time blocks available").classes(
                        "italic text-gray-500 dark:!text-gray-400"
                    )
                    return
                for i, b in enumerate(blocks):
                    with ui.card().classes("p-4 w-72 bg-gray-200 dark:bg-gray-700"):
                        ui.label(f"Block {i + 1}").classes(
                            "font-semibold !text-black dark:!text-white"
                        )
                        s_inp = _time_picker("Start Time", b.start)
                        e_inp = _time_picker("End Time", b.end)
                        sp_inp = _number_input("Spacing", b.spacing or 0)

                        def stage(d=day, idx=i, s=s_inp, e=e_inp, sp=sp_inp):
                            return _stage_time_block(time_config, d, idx, s, e, sp)

                        _bind_stage(
                            [s_inp, e_inp, sp_inp], ["blur", "blur", "blur"], stage
                        )
                        
                        ui.button(
                            icon="delete",
                            on_click=lambda d=day, idx=i: (
                                remove_last_block(d,idx)
                            ),
                        ).props("flat color=red").classes("mt-2")
                        
            def remove_last_block(d, idx):
                try:
                    time_config.remove_time_block(d, idx)
                except ValueError as e:
                    ui.notify(str(e), color="red")

                render_day_blocks(d),

        # ── Patterns ──────────────────────────────

        def render_patterns():
            with patterns_container:
                with ui.expansion("Class Patterns", icon="school").classes(
                    "w-full !text-black dark:!text-white time-config-expansion"
                ):
                    ui.button("Add Class Pattern", icon="add").props(
                        "flat round"
                    ).classes("!text-black dark:!text-white mb-2").on(
                        "click",
                        lambda: _add_class_pattern_dialog(
                            time_config, refresh_patterns
                        ),
                    )
                    classes = time_config.get_classes()
                    if not classes:
                        ui.label("No class patterns available").classes(
                            "italic text-gray-500 dark:!text-gray-400"
                        )
                        return
                    with ui.row().classes("w-full flex-wrap gap-4"):
                        for idx, cls in enumerate(classes):
                            with ui.card().classes("p-4 bg-gray-100 dark:bg-gray-800"):
                                with ui.row().classes(
                                    "w-full flex-nowrap gap-4 items-start"
                                ):
                                    _render_pattern_card(
                                        cls, idx, time_config, refresh_patterns
                                    )
                                    _render_meetings_row(
                                        cls, time_config, refresh_patterns
                                    )

        # ── Global save + bottom bar ───────────────

        def global_save():
            try:
                time_config.save()
                ui.notify("Changes saved successfully", color="positive")
            except Exception as ex:
                ui.notify(f"Error saving changes: {ex}", color="red")
        def reset_on_back():
            time_config.reset()
            ui.navigate.to("/")
        refresh_days()
        refresh_patterns()

        with ui.row().classes(
            "fixed bottom-6 left-1/2 -translate-x-1/2 flex gap-4 items-center"
        ):
            ui.button("Back").props(
                "rounded color=backbtn text-color=white no-caps"
            ).classes(
                "w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]"
            ).on("click", reset_on_back)
            ui.button("Save", icon="save").props(
                "rounded color=positive text-color=white no-caps"
            ).classes("w-80 h-16 text-xl transition-colors duration-300").on(
                "click", global_save
            )

    @staticmethod
    def runGUI():
        """
        Runs the GUI.

        Parameters:
            None
        Returns:
            None
        """
        ui.run(
            title="Scheduler", host="localhost", storage_secret="scheduler_secret_key"
        )


# Helpers for time_slot_config

# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────


def _apply_css():
    ui.add_css("""
        .q-field__label {
            color: rgba(0, 0, 0, 0.54) !important;
        }
        body.body--dark .q-field__label {
            color: rgba(255, 255, 255, 0.7) !important;
        }
        .time-config-expansion.q-expansion-item--expanded
            > .q-expansion-item__container > .q-item {
            background-color: #f3f4f6 !important;
        }
        body.body--dark .time-config-expansion.q-expansion-item--expanded
            > .q-expansion-item__container > .q-item {
            background-color: rgba(255, 255, 255, 0.1) !important;
        }
        .outline-checkbox .q-checkbox__bg {
            background-color: transparent !important;
            border: 2px solid black !important;
        }
        body.body--dark .outline-checkbox .q-checkbox__bg { border-color: white !important; }
        .outline-checkbox.q-checkbox--truthy .q-checkbox__bg,
        .outline-checkbox.q-checkbox--indeterminate .q-checkbox__bg {
            background-color: transparent !important;
        }
        .outline-checkbox .q-checkbox__svg { color: black; }
        body.body--dark .outline-checkbox .q-checkbox__svg { color: white; }
    """)


# ─────────────────────────────────────────────
# Input helpers
# ─────────────────────────────────────────────


def _time_picker(label: str, value: str | None = None):
    inp = ui.input(label=label, value=value or "").classes(
        "w-full !text-black dark:!text-white"
    )
    with inp.add_slot("append"):
        icon = ui.icon("access_time").classes(
            "cursor-pointer !text-black dark:!text-white"
        )
        with ui.menu().props(
            "no-parent-event anchor='top right' self='bottom right'"
        ) as menu:
            ui.time().bind_value(inp).props("color=black text-color=white no-caps")
            with ui.row().classes("justify-end"):
                ui.button("Close", on_click=menu.close).props("flat").classes(
                    "!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white"
                )
        icon.on("click", menu.open)
    return inp


def _number_input(label, value=0, min_val=0):
    return ui.number(label=label, value=value, min=min_val).classes(
        "w-full mb-2 !text-black dark:!text-white"
    )


def _checkbox(label, value=False):
    return ui.checkbox(text=label, value=value).classes(
        "!text-black dark:!text-white mb-2 outline-checkbox"
    )


def _btn_cancel(dialog):
    return ui.button("Cancel", on_click=dialog.close).classes(
        "!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white"
    )


# ─────────────────────────────────────────────
# Time helpers
# ─────────────────────────────────────────────


def _format_time(t: str) -> str | None:
    if not t:
        return None
    t = t.strip()
    m = re.match(r"^(\d):([0-5][0-9])$", t)
    return f"0{m.group(1)}:{m.group(2)}" if m else t


def _is_valid_time(t: str) -> bool:
    return bool(re.match(r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$", t))


# ─────────────────────────────────────────────
# Staging helpers
# ─────────────────────────────────────────────


def _bind_stage(inputs: list, events: list[str], callback):
    """Bind each input to the staging callback on its corresponding event."""
    for inp, event in zip(inputs, events):
        inp.on(event, callback)


def _stage_time_block(time_config, day, idx, s, e, sp):
    start_val, end_val = _format_time(s.value), _format_time(e.value)
    if not (
        start_val and end_val and _is_valid_time(start_val) and _is_valid_time(end_val)
    ):
        return
    try:
        spacing = int(sp.value)
    except (ValueError, TypeError):
        return
    time_config.update_time_block(
        day, idx, TimeBlock(start=start_val, end=end_val, spacing=spacing)
    )


def _stage_class_pattern(cls, credits_inp, disabled_inp, start_inp):
    cls.credits = credits_inp.value
    cls.disabled = disabled_inp.value
    cls.start_time = start_inp.value or None


def _stage_meeting(cls, idx, day_inp, start_inp, dur_inp, lab_inp):
    try:
        m = cls.meetings[idx]
        m.day, m.start_time, m.duration, m.lab = (
            day_inp.value,
            start_inp.value,
            dur_inp.value,
            lab_inp.value,
        )
    except Exception:
        pass


# ─────────────────────────────────────────────
# Dialogs
# ─────────────────────────────────────────────


def _add_time_block_dialog(time_config, on_added):
    with ui.dialog() as d, ui.card().classes("w-96 p-4 bg-gray-100 dark:bg-gray-800"):
        ui.label("Add Time Block").classes("text-xl mb-4 !text-black dark:!text-white")
        day_sel = ui.select(options=time_config.get_days(), label="Day").classes(
            "w-full mb-2 !text-black dark:!text-white"
        )
        start_inp = _time_picker("Start Time")
        end_inp = _time_picker("End Time")
        sp_inp = _number_input("Spacing", 0)
        with ui.row().classes("w-full justify-end gap-2"):
            _btn_cancel(d)
            ui.button(
                "Add",
                on_click=lambda: _submit_time_block(
                    d, time_config, day_sel, start_inp, end_inp, sp_inp, on_added
                ),
            ).classes("!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white")
    d.open()


def _submit_time_block(
    dialog, time_config, day_sel, start_inp, end_inp, sp_inp, on_added
):
    day = day_sel.value
    start = _format_time(start_inp.value)
    end = _format_time(end_inp.value)
    if not day:
        return ui.notify("Please select a day.", color="red")
    if not (start and end and _is_valid_time(start) and _is_valid_time(end)):
        return ui.notify("Times must be in HH:MM format (e.g., 08:00).", color="red")
    if tuple(map(int, end.split(":"))) <= tuple(map(int, start.split(":"))):
        return ui.notify("End time must be after start time.", color="red")
    try:
        spacing = int(sp_inp.value)
        if spacing <= 0:
            return ui.notify("Spacing must be greater than 0", color= "red")
    except (ValueError, TypeError):
        return ui.notify("Spacing must be an integer.", color="red")
    time_config.add_time_block(day, TimeBlock(start=start, end=end, spacing=spacing))
    dialog.close()
    on_added(day)


def _add_class_pattern_dialog(time_config, on_added):
    with ui.dialog() as d, ui.card().classes("w-96 p-4 bg-gray-100 dark:bg-gray-800"):
        ui.label("Add Class Pattern").classes(
            "text-xl mb-4 !text-black dark:!text-white"
        )
        credits_inp = _number_input("Credits", 0)
        disabled_inp = _checkbox("Disabled", False)
        start_inp = _time_picker("Start Time")
        ui.label("(This is optional)").classes(
            "text-xs italic text-gray-500 dark:text-gray-400 -mt-1 mb-2"
        )
        ui.label("Initial Meeting").classes("text-lg mt-6 !text-black dark:!text-white")
        day_inp = ui.select(options=time_config.get_days(), label="Day").classes(
            "w-full mb-2 !text-black dark:!text-white"
        )
        meet_start = _time_picker("Start Time")
        dur_inp = _number_input("Duration", 60, 1)
        lab_inp = _checkbox("Lab Meeting")
        with ui.row().classes("w-full justify-end gap-2"):
            _btn_cancel(d)
            ui.button(
                "Add",
                on_click=lambda: _submit_class_pattern(
                    d,
                    time_config,
                    credits_inp,
                    disabled_inp,
                    start_inp,
                    day_inp,
                    meet_start,
                    dur_inp,
                    lab_inp,
                    on_added,
                ),
            ).classes("!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white")
    d.open()


def _submit_class_pattern(
    dialog,
    time_config,
    credits_inp,
    disabled_inp,
    start_inp,
    day_inp,
    meet_start,
    dur_inp,
    lab_inp,
    on_added,
):
    try:
        credits = int(credits_inp.value)
    except (ValueError, TypeError):
        return ui.notify("Credits must be an integer.", color="red")
    start_val = None
    if start_inp.value:
        start_val = _format_time(start_inp.value)
        if start_val is None or not _is_valid_time(start_val):
            return ui.notify("Pattern start time must be in HH:MM format.", color="red")

    if not (day_inp.value and meet_start.value and dur_inp.value):
        return ui.notify("All meeting fields are required.", color="red")
    meet_start_val = _format_time(meet_start.value)
    if meet_start_val is None or not _is_valid_time(meet_start_val):
        return ui.notify("Meeting start time must be in HH:MM format.", color="red")
    try:
        time_config.add_class(
            ClassPattern(
                credits=credits,
                disabled=disabled_inp.value,
                start_time=start_val,
                meetings=[
                    Meeting(
                        day=day_inp.value,
                        start_time=meet_start_val,
                        duration=int(dur_inp.value),
                        lab=lab_inp.value,
                    )
                ],
            )
        )
    except Exception as ex:
        return ui.notify(f"Error adding class pattern: {ex}", color="red")
    dialog.close()
    on_added()


def _add_meeting_dialog(time_config, cls, on_added):
    with ui.dialog() as d, ui.card().classes("w-96 p-4 bg-gray-100 dark:bg-gray-800"):
        ui.label("Add Meeting").classes("text-xl mb-4 !text-black dark:!text-white")
        day_sel = ui.select(options=time_config.get_days(), label="Day").classes(
            "w-full mb-2 !text-black dark:!text-white"
        )
        start_inp = _time_picker("Start Time")
        dur_inp = _number_input("Duration", 60, 1)
        lab_inp = _checkbox("Lab Meeting")
        with ui.row().classes("w-full justify-end gap-2"):
            _btn_cancel(d)
            ui.button(
                "Add",
                on_click=lambda: _submit_meeting(
                    d, time_config, cls, day_sel, start_inp, dur_inp, lab_inp, on_added
                ),
            ).classes("!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white")
    d.open()


def _submit_meeting(
    dialog, time_config, cls, day_sel, start_inp, dur_inp, lab_inp, on_added
):
    if not (day_sel.value and start_inp.value and dur_inp.value):
        return ui.notify("Please fill all fields.", color="red")
    time_config.add_meeting(
        cls,
        Meeting(
            day=day_sel.value,
            start_time=start_inp.value,
            duration=int(dur_inp.value),
            lab=lab_inp.value,
        ),
    )
    dialog.close()
    on_added()


# ─────────────────────────────────────────────
# Pattern / Meeting card renderers
# (module-level so they don't bloat the closure)
# ─────────────────────────────────────────────


def _render_pattern_card(cls, idx, time_config, refresh_patterns):
    with ui.card().classes("p-4 bg-gray-200 dark:bg-gray-700 w-72 shrink-0"):
        credits_inp = _number_input("Credits", cls.credits)
        disabled_inp = _checkbox("Disabled", cls.disabled)
        start_inp = _time_picker("Start Time", cls.start_time)

        def stage(c=cls, cr=credits_inp, dis=disabled_inp, st=start_inp):
            return _stage_class_pattern(c, cr, dis, st)

        _bind_stage(
            [credits_inp, disabled_inp, start_inp],
            ["blur", "update:model-value", "blur"],
            stage,
        )
        with ui.row().classes("gap-2 mt-2"):
            ui.button("Add Meeting", icon="add").props("flat").classes(
                "!text-black dark:!text-white"
            ).on(
                "click",
                lambda c=cls: _add_meeting_dialog(time_config, c, refresh_patterns),
            )
            ui.button(
                icon="delete",
                on_click=lambda i=idx: (
                    time_config.remove_class(i),
                    refresh_patterns(),
                ),
            ).props("flat color=red")


def _render_meetings_row(cls, time_config, refresh_patterns):
    with ui.row().classes("flex-1 flex-nowrap overflow-x-auto gap-4"):
        for i, m in enumerate(cls.meetings):
            with ui.card().classes(
                "p-4 bg-gray-300 dark:bg-gray-600 min-w-[250px] shrink-0"
            ):
                day_inp = ui.select(
                    options=time_config.get_days(), value=m.day, label="Day"
                ).classes("mb-2 !text-black dark:!text-white")
                start_inp = _time_picker("Start Time", m.start_time)
                dur_inp = _number_input("Duration", m.duration, 1)
                lab_inp = _checkbox("Lab Meeting", m.lab)

                def stage(
                    c=cls, idx=i, d=day_inp, s=start_inp, dur=dur_inp, lab=lab_inp
                ):
                    return _stage_meeting(c, idx, d, s, dur, lab)

                _bind_stage(
                    [day_inp, start_inp, dur_inp, lab_inp],
                    ["update:model-value", "blur", "blur", "update:model-value"],
                    stage,
                )
                if len(cls.meetings) > 1:
                    ui.button(
                        icon="delete",
                        on_click=lambda c=cls, idx=i: (
                            time_config.remove_meeting(c, idx),
                            refresh_patterns(),
                        ),
                    ).props("flat color=red")


if __name__ in {"__main__", "__mp_main__"}:
    GUIView.runGUI()
