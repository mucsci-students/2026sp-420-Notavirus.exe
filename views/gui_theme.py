# views/gui_theme.py
"""
GUITheme - Graphical-user interface theme

This view class handles all files for the GUI that are related to themes.
"""

from nicegui import ui, app


class GUITheme:
    @staticmethod
    def applyTheming():
        """
        Sets up standard colors.

        Parameters:
            None
        Returns:
            None
        """
        dark = ui.dark_mode().bind_value(app.storage.user, "dark_mode")
        ui.button(icon="brightness_4", on_click=dark.toggle).props(
            "flat round"
        ).classes("absolute top-4 right-4 z-50 !text-black dark:!text-white")

        ui.add_head_html("""
        <style>
            /* Selected value text in field */
            .q-field--dark .q-field__native span {
                color: #ffffff !important;
            }
            .q-field:not(.q-field--dark) .q-field__native span {
                color: #000000 !important;
            }

            /* Dropdown popup - dark mode */
            .q-menu.q-dark,
            .q-menu.q-menu--dark {
                background: #000000 !important;
                color: #ffffff !important;
            }
            .q-menu.q-dark *,
            .q-menu.q-menu--dark * {
                color: #ffffff !important;
            }

            /* Dropdown popup - light mode */
            .q-menu:not(.q-dark):not(.q-menu--dark) .q-item__label,
            .q-menu:not(.q-dark):not(.q-menu--dark) .q-item__section {
                color: #000000 !important;
            }

            /* Toggle track - inactive state (both modes) */
            .q-toggle__track {
                opacity: 0.5 !important;
                background: #808080 !important;
            }

            /* Toggle track - active state */
            .q-toggle__inner--truthy .q-toggle__track {
                opacity: 1 !important;
                background: #808080 !important;
            }

            /* Toggle thumb - light mode off */
            .q-field:not(.q-field--dark) .q-toggle__thumb:before,
            .q-toggle:not(.q-toggle--dark) .q-toggle__thumb:before {
                background: #ffffff !important;
            }
        </style>
        """)

        ui.colors(
            primary="#FFFFFF",
            backbtn="#a0a0a0",  # Grey
            backHover="#808080",  # Darker grey
            facultyBegin="#8095e4",  # Light Purple
            facultyEnd="#a855f7",  # Dark Purple
            courseBegin="#EDC54E",  # Orange
            courseEnd="#ED764E",  # Orange
            roomBegin="#4EEDA0",  # Cyan/Green
            roomEnd="#4EEAED",  # Cyan
            conflictBegin="#f94680",  # Red
            conflictEnd="#eb0e19",  # Red
            labBegin="#1bc0ba",  # Green
            labEnd="#19fa11",  # Green
        )
