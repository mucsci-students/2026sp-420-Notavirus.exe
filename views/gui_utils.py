# views/gui_utils.py
"""
GUIUtils - Shared utility functions for GUI views.
"""

from nicegui import ui


def require_config(back_url: str = "/") -> bool:
    """
    Checks whether a configuration has been loaded.

    If no configuration is loaded, renders a 'no config' message on the
    current page with a Load Configuration button and a Back button, then
    returns False. The calling page function should return immediately after
    a False result.

    Parameters:
        back_url (str): The URL the Back button navigates to. Defaults to '/'.
    Returns:
        bool: True if a config is loaded, False if the no-config UI was rendered.
    """
    from views.gui_view import GUIView

    if GUIView.controller is not None and GUIView.controller.config_model is not None:
        return True

    # Styling for load a configuration button when a configuration is not already loaded
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
        .load-dialog .q-uploader__list,
        .load-dialog .q-uploader__subtitle {
            display: none !important;
        }
        .load-dialog .q-uploader__header-content .q-uploader__subtitle {
            display: none !important;
        }
        .load-dialog .q-uploader__header {
            background: #f5f5f5 !important;
            color: black !important;
        }
        .load-dialog .q-uploader__title {
            color: black !important;
        }
    """)

    with ui.column().classes("w-full items-center pt-24 pb-12 gap-6"):
        ui.icon("folder_off").classes("text-6xl text-gray-400 dark:text-gray-500")
        ui.label("No Configuration Loaded").classes(
            "text-2xl !text-black dark:!text-white"
        )
        ui.label("Please load a configuration file to continue.").classes(
            "text-base !text-gray-500 dark:!text-gray-400"
        )

        load_dialog = ui.dialog()
        with load_dialog:
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

                    All model construction and sub-controller wiring is the
                    Controller's responsibility (load_config does that work).
                    """
                    import os

                    try:
                        file_path = os.path.join(os.getcwd(), e.file.name)
                        with open(file_path, "wb") as f:
                            f.write(await e.file.read())

                        from views.gui_view import GUIView

                        if GUIView.controller is None:
                            return
                        success, message = GUIView.controller.load_config(file_path)

                        if success:
                            status_label.style("color: green !important;")
                            status_label.set_text(f"✓ Loaded: {e.file.name}")
                            ui.notify(
                                "Configuration loaded successfully!", type="positive"
                            )
                            load_dialog.close()
                            ui.navigate.reload()
                        else:
                            status_label.style("color: red !important;")
                            status_label.set_text(message)

                    except Exception as ex:
                        status_label.style("color: red !important;")
                        status_label.set_text(f"Error: {ex}")

                ui.upload(
                    label="Select JSON file",
                    auto_upload=True,
                    max_files=1,
                    on_upload=handle_upload,
                ).classes("w-full")
                ui.button("Cancel").props("flat no-caps").style(
                    "color: black !important;"
                ).on("click", load_dialog.close)

        with ui.row().classes("gap-4"):
            ui.button("Load Configuration").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-56 h-14 text-lg dark:!bg-white dark:!text-black").on(
                "click", load_dialog.open
            )
            ui.button("Back").props(
                "rounded color=black text-color=white no-caps"
            ).classes("w-56 h-14 text-lg dark:!bg-white dark:!text-black").on(
                "click", lambda: ui.navigate.to(back_url)
            )

    return False
