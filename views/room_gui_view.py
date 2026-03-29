# views/room_gui_view.py
"""
RoomGUIView - Graphical-user interface for room interactions

  MVC rules followed in this file:
    - No class-level model or controller attributes.
    - No Model methods are called directly.
    - All data operations go through GUIView.controller.room_controller.
    - Save orchestration is delegated to GUIView.controller methods.
"""

from nicegui import ui
from views.gui_theme import GUITheme
from views.gui_utils import require_config
#    Views should never import Controller classes directly.


class RoomGUIView:
    # Class for Room GUI View

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

        Allows the user to enter a room name and number. Save stores the
        room in memory only as a preview. Save to Config adds to memory
        if not already added, then writes to the configuration file.

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
            ui.label(
                "Enter a room name and number below. Press Save to preview in memory, or Save to Config to save permanently."
            ).classes("text-lg !text-black dark:!text-white text-center max-w-xl")

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

            def handle_save():
                """Add to memory via Controller."""
                success, message = controller.add_room(room_input.value)
                result_label.set_text(message)
                if success:
                    refresh_rooms()

            def handle_save_to_config():
                """Add to memory if needed, then persist via Controller."""
                existing = controller.get_all_rooms()
                if room_input.value and room_input.value not in existing:
                    success, message = controller.add_room(room_input.value)
                    if not success:
                        result_label.set_text(message)
                        return
                if GUIView.controller is None:
                    return
                success = GUIView.controller.save_to_config("all")
                if success:
                    result_label.set_text("Room saved to config file.")
                    refresh_rooms()
                else:
                    result_label.set_text("Config save failed.")

            ui.button("Save to Config").on("click", handle_save_to_config).props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black")
            ui.button("Save").on("click", handle_save).props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black")
            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/room")
            )

    @ui.page("/room/modify")
    @staticmethod
    def room_modify():
        """
        Displays the GUI for modifying a room.

        Allows the user to select an existing room and enter a new name.
        Save stores the change in memory only as a preview. Save to Config
        modifies in memory if not already modified, then writes to the
        configuration file.

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
                "Select a room to modify, then enter a new name. Press Save to preview in memory, or Save to Config to save permanently."
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
                """Modify in memory via Controller."""
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
                    refresh_select()

            def handle_save_to_config():
                """Modify in memory if needed, then persist via Controller."""
                if not new_name.value or not new_name.value.strip():
                    result_label.set_text("New room name cannot be empty.")
                    return
                existing = controller.get_all_rooms()
                if selected_room.value and selected_room.value in existing:
                    success, message = controller.modify_room(
                        selected_room.value, new_name.value
                    )
                    if not success:
                        result_label.set_text(message)
                        return
                if GUIView.controller is None:
                    return
                success = GUIView.controller.save_to_config("all")
                if success:
                    result_label.set_text("Room saved to config file.")
                    refresh_select()
                else:
                    result_label.set_text("Config save failed.")

            ui.button("Save to Config").on("click", handle_save_to_config).props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black")
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

        Allows the user to select a room and delete it from memory.
        Save to Config writes the deletion permanently to the configuration file.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/room"):
            return
        from views.gui_view import GUIView

        ui.add_css("""
            .body--dark .q-field__control { background-color: #383838 !important; border-color: white !important; }
            .body--dark .q-field__native, .body--dark .q-field__label,
            .body--dark .q-field__input, .body--dark .q-select__dropdown-icon { color: white !important; }
            .body--dark .q-item__label { color: white !important; }
        """)

        if GUIView.controller is None:
            return
        controller = GUIView.controller.room_controller
        rooms = controller.get_all_rooms()

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
            ui.label(
                'Select a room to delete. Press "Save to Config" to permanently save. You must press Delete before saving to remove the room.'
            ).classes("text-lg !text-black dark:!text-white text-center max-w-xl")

            selected_room = (
                ui.select(rooms, label="Select Room to Delete")
                .props("rounded outlined color=black")
                .classes("w-80")
            )
            result_label = ui.label("").classes(
                "text-base !text-black dark:!text-white"
            )
            save_label = ui.label("").classes("text-lg")

            def delete():
                success, message = controller.delete_room(selected_room.value)
                result_label.set_text(message)
                if success:
                    save_label.set_text(
                        "You have unsaved changes. Click Save to Config to persist."
                    )
                    save_label.classes(replace="text-lg text-orange-500")
                    updated_rooms = controller.get_all_rooms()
                    selected_room.set_options(updated_rooms)
                    selected_room.set_value(None)

            def save_to_config():
                if GUIView.controller is None:
                    return
                success = GUIView.controller.save_to_config("all")
                if success:
                    save_label.set_text("Configuration saved to file.")
                    save_label.classes(replace="text-lg text-green-600")
                else:
                    save_label.set_text("Save failed. Check terminal for details.")
                    save_label.classes(replace="text-lg text-red-600")

            ui.button("Delete").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", delete
            )
            ui.button("Save to Config").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl dark:!bg-white dark:!text-black").on(
                "click", save_to_config
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
        Displays the GUI for viewing all rooms.

        Loads all rooms from the controller and displays each as a card.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        if not require_config(back_url="/room"):
            return
        from views.gui_view import GUIView

        # Was previously accessing model, now accesses controller
        if GUIView.controller is None:
            return
        controller = GUIView.controller.room_controller
        rooms = controller.get_all_rooms()

        with ui.column().classes("w-full items-center pt-12 pb-12 gap-4"):
            with ui.row().classes("w-full max-w-2xl justify-start"):
                ui.button("Home").props(
                    "rounded color=black text-color=white no-caps"
                ).classes("h-10 dark:!bg-white dark:!text-black").on(
                    "click", lambda: ui.navigate.to("/")
                )
            ui.label("View Rooms").classes("text-4xl mb-6 !text-black dark:!text-white")
            if not rooms:
                ui.label("No rooms in configuration.").classes(
                    "text-gray-600 dark:!text-gray-300"
                )
            else:
                with ui.column().classes("w-full max-w-2xl gap-3"):
                    for room in rooms:
                        with ui.card().classes("w-full px-5 py-4"):
                            ui.label(room).classes(
                                "text-base font-semibold !text-black dark:!text-white"
                            )
            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-80 h-16 text-xl mt-4 dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to("/room")
            )
