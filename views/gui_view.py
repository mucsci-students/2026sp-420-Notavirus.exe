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
    def time_slot_config():
        """
        Full GUI for time slot configuration and class pattern management:
        - Days / time blocks
        - Class patterns
        - Meetings (add/edit/delete)
        """
        GUITheme.applyTheming()
        ui.query("body").style("background-color: var(--q-primary)").classes(
            "dark:!bg-black"
        )

        if not require_config(back_url="/"):
            return

        cm = getattr(GUIView.controller, "config_model", None)
        assert cm is not None

        time_config = time_config_data(cm.config.time_slot_config)

        ui.label("Time Slot Config").classes(
            "text-4xl mb-6 !text-black dark:!text-white text-center w-full"
        )
        days_container = ui.column().classes("w-full gap-4")
        patterns_container = ui.column().classes("w-full gap-4")

        # -----------------------------
        # Helper UI Elements
        # -----------------------------
        def time_picker(label: str, value: str | None = None):
            with ui.element("div").classes("relative w-full"):
                inp = ui.input(label=label, value=value or "").classes(
                    "w-full !text-black dark:!text-white"
                )

                with ui.menu().props(
                    "no-parent-event anchor='top right' self='top left'"
                ) as menu:
                    ui.time().bind_value(inp).props(
                        "color=black text-color=white no-caps"
                    )
                    with ui.row().classes("justify-end"):
                        ui.button("Close", on_click=menu.close).props("flat").classes(
                            "!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white"
                        )

                # Icon to open menu
                with inp.add_slot("append"):
                    ui.icon("access_time").on("click", menu.open).classes(
                        "cursor-pointer !text-black dark:!text-white"
                    )

            return inp

        def number_input(label, value=0, min_val=0):
            return ui.number(label=label, value=value, min=min_val).classes(
                "w-full mb-2 !text-black dark:!text-white"
            )

        ui.add_css("""
            .q-field__label {
                color: rgba(0, 0, 0, 0.54) !important;
            }
            body.body--dark .q-field__label {
                color: rgba(255, 255, 255, 0.7) !important;
            }
            .time-config-expansion.q-expansion-item--expanded
                > .q-expansion-item__container
                > .q-item {
                background-color: #f3f4f6 !important;
            }
            body.body--dark .time-config-expansion.q-expansion-item--expanded
                > .q-expansion-item__container
                > .q-item {
                background-color: rgba(255, 255, 255, 0.1) !important;
            }
            .outline-checkbox .q-checkbox__bg {
                background-color: transparent !important;
                border: 2px solid black !important;
            }
            body.body--dark .outline-checkbox .q-checkbox__bg {
                border-color: white !important;
            }
            .outline-checkbox.q-checkbox--truthy .q-checkbox__bg,
            .outline-checkbox.q-checkbox--indeterminate .q-checkbox__bg {
                background-color: transparent !important;
            }
            .outline-checkbox .q-checkbox__svg {
                color: black;
            }
            body.body--dark .outline-checkbox .q-checkbox__svg {
                color: white;
            }
        """)

        def checkbox(label, value=False):
            return ui.checkbox(text=label, value=value).classes(
                "!text-black dark:!text-white mb-2 outline-checkbox"
            )

        # -----------------------------
        # Refresh functions
        # -----------------------------
        def refresh_days():
            days_container.clear()
            render_days()

        def refresh_patterns():
            patterns_container.clear()
            render_patterns()

        # -----------------------------
        # Rendering
        # -----------------------------
        day_expansions = {}

        def render_days():
            day_expansions.clear()
            with days_container:
                with ui.expansion("Available Days", icon="meeting_room").classes(
                    "w-full !text-black dark:!text-white time-config-expansion"
                ):
                    with ui.row().classes("w-full justify-between items-center mb-2"):
                        ui.label("Days").classes("text-lg !text-black dark:!text-white")
                        ui.button(icon="add").props("flat round").classes(
                            "!text-black dark:!text-white"
                        ).on("click", add_time_block)

                    for day, blocks in time_config.get_all_time_slots().items():
                        # Create expansion for each day
                        exp = ui.expansion(str(day)).classes(
                            "w-full !text-black dark:!text-white time-config-expansion"
                        )

                        # Create the inner container **as a child of the expansion**
                        with exp:
                            block_container = ui.column()
                            day_expansions[day] = block_container

                        # Initial render of blocks inside this container
                        render_day_blocks(day)

        def render_day_blocks(day):
            container = day_expansions[day]
            container.clear()
            blocks = time_config.get_all_time_slots().get(day, [])

            with container:
                if not blocks:
                    ui.label("No time blocks available").classes(
                        "italic text-gray-500 dark:!text-gray-400"
                    )
                    return

                for i, b in enumerate(blocks, start=1):
                    # Each time block is its own expansion
                    with ui.expansion(f"Time Slot {i}").classes(
                        "w-full !text-black dark:!text-white time-config-expansion"
                    ):
                        with ui.card().classes(
                            "w-full p-4 bg-gray-100 dark:bg-gray-800"
                        ):
                            s_input = time_picker("Start Time", b.start)
                            e_input = time_picker("End Time", b.end)
                            sp_input = number_input("Spacing", b.spacing or 0)

                            with ui.row().classes("gap-2 mt-2"):
                                ui.button(
                                    "Save",
                                    on_click=lambda d=day, idx=i - 1, s=s_input, e=e_input, sp=sp_input: (
                                        save_time_block(d, idx, s, e, sp)
                                    ),
                                ).classes(
                                    "!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white"
                                )
                                ui.button(
                                    icon="delete",
                                    on_click=lambda d=day, idx=i - 1: delete_time_block(
                                        d, idx
                                    ),
                                ).props("flat color=red")

        def render_patterns():
            """
            Renders all class patterns under a single "Class Patterns" expandable.
            Each pattern has its own expandable and contains meetings.
            """
            with patterns_container:
                with ui.expansion("Class Patterns", icon="school").classes(
                    "w-full !text-black dark:!text-white time-config-expansion"
                ):
                    # Add Class Pattern button
                    ui.button("Add Class Pattern", icon="add").props(
                        "flat round"
                    ).classes("!text-black dark:!text-white mb-2").on(
                        "click", add_class_pattern
                    )

                    classes = time_config.get_classes()
                    if not classes:
                        ui.label("No class patterns available").classes(
                            "italic text-gray-500 dark:!text-gray-400"
                        )

                    for idx, cls in enumerate(classes, start=1):
                        # Each individual pattern expandable
                        with ui.expansion(f"Pattern {idx}").classes(
                            "w-full !text-black dark:!text-white time-config-expansion"
                        ):
                            with ui.card().classes(
                                "w-full p-4 bg-gray-100 dark:bg-gray-800"
                            ):
                                # Editable pattern fields
                                credits_input = number_input("Credits", cls.credits)
                                disabled_input = checkbox("Disabled", cls.disabled)
                                start_input = time_picker("Start Time", cls.start_time)

                                with ui.row().classes("gap-2 mt-2"):
                                    ui.button(
                                        "Save",
                                        on_click=lambda c=cls, cr=credits_input, dis=disabled_input, st=start_input: (
                                            save_class_pattern(c, cr, dis, st)
                                        ),
                                    ).classes(
                                        "!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white"
                                    )
                                    ui.button(
                                        icon="delete",
                                        on_click=lambda i=idx - 1: delete_class_pattern(
                                            i
                                        ),
                                    ).props("flat color=red")

                                # Meetings expansion under the pattern
                                with ui.expansion("Meetings").classes(
                                    "w-full !text-black dark:!text-white mt-2 time-config-expansion"
                                ):
                                    # Add Meeting button
                                    ui.button("Add Meeting", icon="add").props(
                                        "flat round"
                                    ).classes("!text-black dark:!text-white mb-2").on(
                                        "click", lambda c=cls: add_meeting(c)
                                    )

                                    for i, m in enumerate(cls.meetings):
                                        with ui.card().classes(
                                            "w-full p-4 bg-gray-200 dark:bg-gray-700"
                                        ):
                                            day_input = ui.select(
                                                options=time_config.get_days(),
                                                value=m.day,
                                                label="Day",
                                            ).classes(
                                                "w-full mb-2 !text-black dark:!text-white"
                                            )
                                            start_input = time_picker(
                                                "Start Time", m.start_time
                                            )
                                            dur_input = number_input(
                                                "Duration", m.duration, 1
                                            )
                                            lab_input = checkbox("Lab Meeting", m.lab)

                                            with ui.row().classes("gap-2 mt-2"):
                                                ui.button(
                                                    "Save",
                                                    on_click=lambda cls=cls, idx=i, di=day_input, st=start_input, dur=dur_input, lab=lab_input: (
                                                        save_meeting(
                                                            cls, idx, di, st, dur, lab
                                                        )
                                                    ),
                                                ).classes(
                                                    "!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white"
                                                )

                                                # Only show delete button if more than one meeting
                                                if len(cls.meetings) > 1:
                                                    ui.button(
                                                        icon="delete",
                                                        on_click=lambda cls=cls, idx=i: (
                                                            delete_meeting(cls, idx)
                                                        ),
                                                    ).props("flat color=red")

        # -----------------------------
        # Add Class Pattern Dialog (with one meeting)
        # -----------------------------
        def add_class_pattern():
            with (
                ui.dialog() as d,
                ui.card().classes("w-96 p-4 bg-gray-100 dark:bg-gray-800"),
            ):
                ui.label("Add Class Pattern").classes(
                    "text-xl mb-4 !text-black dark:!text-white"
                )

                # Empty pattern fields
                credits_input = number_input("Credits", 0)
                disabled_input = checkbox("Disabled", False)
                start_input = time_picker("Start Time")
                ui.label("(This is optional)").classes(
                    "text-xs italic text-gray-500 dark:text-gray-400 -mt-1 mb-2"
                )

                # Initial meeting fields (must have at least one meeting)
                ui.label("Initial Meeting").classes(
                    "text-lg mt-6 !text-black dark:!text-white"
                )
                day_input = ui.select(
                    options=time_config.get_days(), label="Day"
                ).classes("w-full mb-2 !text-black dark:!text-white")
                start_meeting_input = time_picker("Start Time")
                dur_input = number_input("Duration", 60, 1)
                lab_input = checkbox("Lab Meeting")

                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button("Cancel", on_click=d.close).classes(
                        "!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white"
                    )
                    ui.button(
                        "Add",
                        on_click=lambda: add_class_pattern_submit(
                            d,
                            credits_input,
                            disabled_input,
                            start_input,
                            day_input,
                            start_meeting_input,
                            dur_input,
                            lab_input,
                        ),
                    ).classes(
                        "!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white"
                    )
            d.open()

        # -----------------------------
        # Submit new class pattern with one meeting
        # -----------------------------
        def add_class_pattern_submit(
            dialog,
            credits_input,
            disabled_input,
            start_input,
            day_input,
            start_meeting_input,
            dur_input,
            lab_input,
        ):
            # Validate credits
            try:
                credits_val = int(credits_input.value)
            except (ValueError, TypeError):
                ui.notify("Credits must be an integer", color="red")
                return

            # Validate pattern start time
            if start_input.value:
                start_val = format_time(start_input.value)
                if not is_valid_time(start_val):
                    ui.notify("Pattern start time must be in HH:MM format", color="red")
                    return

            # Validate meeting inputs
            if (
                not day_input.value
                or not start_meeting_input.value
                or not dur_input.value
            ):
                ui.notify("All meeting fields are required", color="red")
                return

            start_meeting_val = format_time(start_meeting_input.value)
            if not is_valid_time(start_meeting_val):
                ui.notify("Meeting start time must be in HH:MM format", color="red")
                return

            try:
                # Create pattern
                new_pattern = ClassPattern(
                    credits=credits_val,
                    disabled=disabled_input.value,
                    start_time=start_val,
                    meetings=[
                        Meeting(
                            day=day_input.value,
                            start_time=start_meeting_val,
                            duration=dur_input.value,
                            lab=lab_input.value,
                        )
                    ],
                )
                time_config.add_class(new_pattern)
            except Exception as ex:
                ui.notify(f"Error adding class pattern: {ex}", color="red")
                return

            dialog.close()
            refresh_patterns()

        # -----------------------------
        # Actions
        # -----------------------------
        def add_time_block():
            with (
                ui.dialog() as d,
                ui.card().classes("w-96 p-4 bg-gray-100 dark:bg-gray-800"),
            ):
                ui.label("Add Time Block").classes(
                    "text-xl mb-4 !text-black dark:!text-white"
                )
                day_select = ui.select(
                    options=time_config.get_days(), label="Day"
                ).classes("w-full mb-2 !text-black dark:!text-white")
                start_input = time_picker("Start Time")
                end_input = time_picker("End Time")
                spacing_input = number_input("Spacing", 0)
                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button("Cancel", on_click=d.close).classes(
                        "!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white"
                    )
                    ui.button(
                        "Add",
                        on_click=lambda d=d, ds=day_select, s=start_input, e=end_input, sp=spacing_input: (
                            add_time_block_submit(d, ds, s, e, sp)
                        ),
                    ).classes(
                        "!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white"
                    )
            d.open()
            # Fix single-digit hours by adding leading zero

        # Must be at the top-level of time_slot_config() so all functions can use it
        def format_time(t: str):
            if not t:
                return None
            t = t.strip()
            # Add leading zero if single-digit hour (e.g., "8:00" -> "08:00")
            match = re.match(r"^(\d):([0-5][0-9])$", t)
            if match:
                t = f"0{match.group(1)}:{match.group(2)}"
            return t

        def is_valid_time(t: str) -> bool:
            pattern = r"^([0-1][0-9]|2[0-3]):[0-5][0-9]$"
            return bool(re.match(pattern, t))

        def add_time_block_submit(dialog, day_sel, start_inp, end_inp, sp_inp):
            day_val = day_sel.value
            start_val = format_time(start_inp.value)
            end_val = format_time(end_inp.value)
            spacing_val = sp_inp.value

            # Validate that a day is selected
            if not day_val:
                ui.notify("Please select a day to add the time block.", color="red")
                return

            # Validate time strings
            if (
                not start_val
                or not end_val
                or not is_valid_time(start_val)
                or not is_valid_time(end_val)
            ):
                ui.notify(
                    "Start and End times must be in HH:MM format (e.g., 08:00)",
                    color="red",
                )
                return

            # Check that end time is after start time
            start_hour, start_min = map(int, start_val.split(":"))
            end_hour, end_min = map(int, end_val.split(":"))
            if (end_hour, end_min) <= (start_hour, start_min):
                ui.notify("The end time cannot be before the start time", color="red")
                return

            # Validate spacing
            try:
                spacing_val = int(spacing_val)
            except (ValueError, TypeError):
                ui.notify("Spacing must be an integer", color="red")
                return

            # Add the new time block
            try:
                time_config.add_time_block(
                    day_val,
                    TimeBlock(start=start_val, end=end_val, spacing=spacing_val),
                )
            except Exception as ex:
                ui.notify(f"Error adding time block: {ex}", color="red")
                return

            # Only close dialog if everything is valid
            dialog.close()
            render_day_blocks(day_val)

        def save_time_block(day, idx, s_input, e_input, sp_input):
            start_val = format_time(s_input.value)
            end_val = format_time(e_input.value)
            spacing_val = sp_input.value

            if (
                not start_val
                or not end_val
                or not is_valid_time(start_val)
                or not is_valid_time(end_val)
            ):
                ui.notify(
                    "Start and End times must be in HH:MM format (e.g., 08:00)",
                    color="red",
                )
                return

            try:
                spacing_val = int(spacing_val)
            except (ValueError, TypeError):
                ui.notify("Spacing must be an integer", color="red")
                return

            try:
                time_config.update_time_block(
                    day,
                    idx,
                    TimeBlock(start=start_val, end=end_val, spacing=spacing_val),
                )
            except Exception as ex:
                ui.notify(f"Error saving time block: {ex}", color="red")
                return

            render_day_blocks(day)

        def delete_time_block(day, idx):
            time_config.remove_time_block(day, idx)
            render_day_blocks(day)

        def save_class_pattern(cls, cr_input, dis_input, st_input):
            cls.credits = cr_input.value
            cls.disabled = dis_input.value
            cls.start_time = st_input.value or None
            refresh_patterns()

        def add_meeting(cls):
            with (
                ui.dialog() as d,
                ui.card().classes("w-96 p-4 bg-gray-100 dark:bg-gray-800"),
            ):
                ui.label("Add Meeting").classes(
                    "text-xl mb-4 !text-black dark:!text-white"
                )
                day_sel = ui.select(
                    options=time_config.get_days(), label="Day"
                ).classes("w-full mb-2 !text-black dark:!text-white")
                start_inp = time_picker("Start Time")
                dur_inp = number_input("Duration", 60, 1)
                lab_chk = checkbox("Lab Meeting")
                with ui.row().classes("w-full justify-end gap-2"):
                    ui.button("Cancel", on_click=d.close)
                    ui.button(
                        "Add",
                        on_click=lambda d=d, c=cls, ds=day_sel, st=start_inp, dur=dur_inp, lab=lab_chk: (
                            add_meeting_submit(d, c, ds, st, dur, lab)
                        ),
                    )
            d.open()

        def add_meeting_submit(dialog, cls, day_sel, start_inp, dur_inp, lab_chk):
            if not day_sel.value or not start_inp.value or not dur_inp.value:
                ui.notify("Please fill all fields", color="red")
                return
            time_config.add_meeting(
                cls,
                Meeting(
                    day=day_sel.value,
                    start_time=start_inp.value,
                    duration=dur_inp.value,
                    lab=lab_chk.value,
                ),
            )
            dialog.close()
            refresh_patterns()

        def delete_class_pattern(idx):
            time_config.remove_class(idx)
            refresh_patterns()

        def delete_meeting(cls, idx):
            time_config.remove_meeting(cls, idx)
            refresh_patterns()

        def save_meeting(cls, idx, day_input, start_input, dur_input, lab_input):
            try:
                meeting = cls.meetings[idx]
                meeting.day = day_input.value
                meeting.start_time = start_input.value
                meeting.duration = dur_input.value
                meeting.lab = lab_input.value
                refresh_patterns()
            except Exception as ex:
                ui.notify(f"Error saving meeting: {ex}", color="red")

        # -----------------------------
        # Initial render
        # -----------------------------
        refresh_days()
        refresh_patterns()

        ui.button("Back").props(
            "rounded color=backbtn text-color=white no-caps"
        ).classes(
            "w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)] fixed bottom-6 left-1/2 -translate-x-1/2"
        ).on("click", lambda: ui.navigate.to("/"))

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


if __name__ in {"__main__", "__mp_main__"}:
    GUIView.runGUI()
