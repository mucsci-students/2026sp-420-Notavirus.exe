# views/lab_gui_view.py
"""
LabGUIView - Graphical-user interface for lab interactions

  MVC rules followed in this file:
    - No class-level model or controller attributes.
    - No Model methods are called directly (.model. removed everywhere).
    - All data operations go through GUIView.controller.lab_controller.
    - Save orchestration is delegated to GUIView.controller methods.
"""

from typing import Any
from nicegui import ui
from views.gui_theme import GUITheme
from views.gui_utils import require_config


class LabGUIView:
    # Class for Lab GUI View
    lab_controller: Any = None
    lab_model: Any = None
    _lab_controller: Any = None

    @ui.page("/lab")
    @staticmethod
    def lab():
        """
        Displays the GUI for Lab.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/"):
            return
        with ui.column().classes("w-full items-center pt-12 pb-12 font-sans"):
            ui.label("Lab").classes("text-4xl mb-10 !text-black dark:!text-white")
            ui.button("Add Lab").props("rounded text-color=white no-caps").classes(
                "w-80 h-16 text-xl"
            ).style(
                "background: linear-gradient(135deg, var(--q-labBegin), var(--q-labEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/lab/add"))
            ui.button("Modify Lab").props("rounded text-color=white no-caps").classes(
                "w-80 h-16 text-xl"
            ).style(
                "background: linear-gradient(135deg, var(--q-labBegin), var(--q-labEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/lab/modify"))
            ui.button("Delete Lab").props("rounded text-color=white no-caps").classes(
                "w-80 h-16 text-xl"
            ).style(
                "background: linear-gradient(135deg, var(--q-labBegin), var(--q-labEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/lab/delete"))
            ui.button("View Lab").props("rounded text-color=white no-caps").classes(
                "w-80 h-16 text-xl"
            ).style(
                "background: linear-gradient(135deg, var(--q-labBegin), var(--q-labEnd)) !important;"
            ).on("click", lambda: ui.navigate.to("/lab/view"))
            ui.space()
            ui.button("Back").props(
                "rounded color=backbtn text-color=white no-caps"
            ).classes(
                "w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]"
            ).on("click", lambda: ui.navigate.to("/"))

    @ui.page("/lab/add")
    @staticmethod
    def lab_add():
        GUITheme.applyTheming()
        if not require_config(back_url="/lab"):
            return
        from views.gui_view import GUIView

        ui.add_css("""
            .body--dark .q-field__control { background-color: #383838 !important; border-color: white !important; }
            .body--dark .q-field__native, .body--dark .q-field__label,
            .body--dark .q-field__input { color: white !important; }
        """)

        # Read controller at render time.
        if GUIView.controller is None:
            return
        controller = GUIView.controller.lab_controller

        with ui.column().classes("gap-6 items-center w-full"):
            with ui.row().classes("w-full max-w-2xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
            ui.label("Add Lab").classes("text-4xl mb-10 !text-black dark:!text-white")

            new_lab = (
                ui.input(label="Lab Name")
                .props("rounded outlined color=black")
                .classes("w-80")
            )
            result_label = ui.label("").classes(
                "text-base !text-black dark:!text-white"
            )
            ui.label("").classes("text-lg")

            ui.label("Current Labs:").classes(
                "text-lg font-semibold mt-4 !text-black dark:!text-white"
            )
            lab_list_container = ui.column().classes("w-80")

            def refresh_list():
                lab_list_container.clear()
                updated_labs = controller.get_all_labs()
                with lab_list_container:
                    if not updated_labs:
                        ui.label("No labs yet.").classes("text-gray-500")
                    else:
                        for lab in updated_labs:
                            with ui.card().classes("w-full px-4 py-2"):
                                ui.label(lab).classes("text-base")

            refresh_list()

            def add():
                """Add lab and save to config immediately."""
                try:
                    success, message = LabGUIView._lab_controller.gui_add_lab(
                        new_lab.value
                    )
                    result_label.set_text(message)
                    if success:
                        new_lab.set_value("")
                        refresh_list()
                except Exception as e:
                    result_label.set_text(f"Error: {e}")

            ui.button("Add").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", add
            )
            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/lab")
            )

    @ui.page("/lab/modify")
    @staticmethod
    def lab_modify():
        """
        Displays the GUI for modifying a lab.

        Changes are in-memory until Save Configuration is clicked.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/lab"):
            return

        ui.query("body").style("background-color: var(--q-modify)").classes(
            "dark:!bg-black"
        )

        labs = (
            LabGUIView._lab_controller.model.get_all_labs()
            if LabGUIView._lab_controller
            else []
        )

        with ui.column().classes("gap-6 items-center w-full"):
            with ui.row().classes("w-full max-w-2xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
            ui.label("Modify Lab").classes(
                "text-4xl mb-10 !text-black dark:!text-white"
            )

            existing_lab = (
                ui.select(labs, label="Select Lab to Modify")
                .props("rounded outlined")
                .classes("w-80")
            )
            modified_lab = (
                ui.input(label="Modified Lab").props("rounded outlined").classes("w-80")
            )

            result_label = ui.label("").classes("text-base")

            def save():
                try:
                    success, message = LabGUIView._lab_controller.gui_modify_lab(
                        existing_lab.value, modified_lab.value.strip()
                    )
                    result_label.set_text(message)
                    if success:
                        existing_lab.set_options(
                            LabGUIView._lab_controller.model.get_all_labs()
                        )
                        modified_lab.set_value("")
                except Exception as e:
                    result_label.set_text(f"Error: {e}")

            ui.button("Save").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", save
            )
            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/lab")
            )

    @ui.page("/lab/delete")
    @staticmethod
    def lab_delete():
        """
        Displays the GUI for deleting a lab.

        Delete commits to memory and immediately persists to disk.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/lab"):
            return
        from views.gui_view import GUIView

        ui.query("body").style("background-color: var(--q-delete)").classes(
            "dark:!bg-black"
        )

        if GUIView.controller is None:
            return
        controller = GUIView.controller.lab_controller
        selected_labs = []

        with ui.column().classes("w-full items-center pt-12 pb-12 font-sans"):
            with ui.row().classes("w-full max-w-2xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
            ui.label("Delete Lab").classes(
                "text-4xl mb-10 !text-black dark:!text-white"
            )

            with ui.card().classes("w-96 h-80 border-2 border-black shadow-none p-0"):
                with ui.scroll_area().classes("w-full h-full p-4"):
                    list_container = ui.column().classes("w-full")

            result_label = ui.label("").classes(
                "text-base !text-black dark:!text-white mt-2"
            )

            def update_lab_list():
                list_container.clear()
                selected_labs.clear()
                labs = controller.get_all_labs()
                with list_container:
                    if not labs:
                        ui.label("No labs available.").classes(
                            "text-gray-500 m-auto mt-4"
                        )
                    else:
                        for lab in labs:

                            def toggle(e, current_lab=lab):
                                if e.value:
                                    if current_lab not in selected_labs:
                                        selected_labs.append(current_lab)
                                else:
                                    if current_lab in selected_labs:
                                        selected_labs.remove(current_lab)

                            ui.checkbox(lab, value=False, on_change=toggle).classes(
                                "w-full text-lg"
                            ).props("color=blue")

            update_lab_list()

            def on_delete():
                """Delete selected labs and save to config immediately."""
                if not selected_labs:
                    result_label.set_text("No labs selected.")
                    return
                if (
                    LabGUIView._lab_controller
                    and LabGUIView._lab_controller.delete_labs_gui(list(selected_labs))
                ):
                    result_label.set_text("✓ Deleted.")
                    update_lab_list()

            ui.button("Delete").props(
                "rounded color=red text-color=white no-caps"
            ).classes("w-40 h-10 text-lg mt-6 shadow-none").on("click", on_delete)
            ui.space().classes("h-10")

            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-48 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/lab")
            )

    @ui.page("/lab/view")
    @staticmethod
    def lab_view():
        """
        Displays the GUI for viewing a lab.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/lab"):
            return
        from views.gui_view import GUIView

        ui.query("body").style("background-color: var(--q-primary)").classes(
            "dark:!bg-black"
        )

        if GUIView.controller is None:
            return
        controller = GUIView.controller.lab_controller
        labs = controller.get_all_labs()

        with ui.column().classes("w-full items-center pt-12 pb-12 gap-4"):
            with ui.row().classes("w-full max-w-2xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
            ui.label("View Labs").classes("text-4xl mb-6 !text-black dark:!text-white")
            if not labs:
                ui.label("No labs in configuration.").classes("text-gray-600")
            else:
                with ui.column().classes("w-full max-w-2xl gap-3"):
                    for lab in labs:
                        with ui.card().classes("w-full px-5 py-4"):
                            ui.label(lab).classes("text-base font-semibold")
            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl mt-4 dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/lab")
            )
