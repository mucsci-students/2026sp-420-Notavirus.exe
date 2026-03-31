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
            None
        Returns:
            None
        """
        dark = ui.dark_mode().bind_value(app.storage.user, "dark_mode")
        ui.button(icon="brightness_4", on_click=dark.toggle).props(
            "flat round"
        ).classes("absolute top-4 right-4 z-50 !text-black dark:!text-white")

        # Dark mode toggle button — pinned to the top-right corner of every page
        ui.button(icon="brightness_4", on_click=dark.toggle).props(
            "flat round"
        ).classes("absolute top-4 right-4 z-50 !text-black dark:!text-white")

        # Build the chat drawer and get a reference to toggle it
        from views.chatbot_gui_view import ChatbotGUIView

        drawer = ChatbotGUIView.add_floating_chat()

        # AI robot button — pinned to the bottom-left corner of every page
        # 'fixed' keeps it in place even when the user scrolls
        # z-50 ensures it appears on top of other page elements
        def _open_chat():
            drawer.show()
            app.storage.user["chat_open"] = True

        with ui.element("div").classes("fixed bottom-6 left-6 z-50"):
            # Round button styled black in light mode, white in dark mode
            with (
                ui.button(on_click=_open_chat)
                .props("round")
                .classes("w-14 h-14 !bg-black dark:!bg-white")
            ):
                # Tabler Icons "robot-2" SVG drawn inline
                # stroke="currentColor" means the icon inherits the button's text color
                # so it is white on black in light mode and black on white in dark mode
                ui.html(
                    sanitize=False,
                    content="""
                    <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28"
                         viewBox="0 0 24 24" fill="none" stroke="currentColor"
                         stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"
                         class="!text-white dark:!text-black">
                        <rect x="4" y="8" width="16" height="12" rx="3"/>
                        <circle cx="9" cy="14" r="1.5" fill="currentColor" stroke="none"/>
                        <circle cx="15" cy="14" r="1.5" fill="currentColor" stroke="none"/>
                        <path d="M9.5 17.5h5"/>
                        <path d="M12 8V5M10 5h4"/>
                        <path d="M2 14h2M20 14h2"/>
                    </svg>
                """,
                )

        # Inject global CSS styles that apply to every page
        # These fix Quasar component colors in both light and dark mode
        ui.add_head_html("""
        <style>
            /* Text color inside dropdown/select fields */
            .q-field--dark .q-field__native span {
                color: #ffffff !important;  /* white text in dark mode */
            }
            .q-field:not(.q-field--dark) .q-field__native span {
                color: #000000 !important;  /* black text in light mode */
            }

            /* Dropdown popup background and text — dark mode */
            .q-menu.q-dark,
            .q-menu.q-menu--dark {
                background: #000000 !important;
                color: #ffffff !important;
            }
            .q-menu.q-dark *,
            .q-menu.q-menu--dark * {
                color: #ffffff !important;
            }

            /* Dropdown popup text — light mode */
            .q-menu:not(.q-dark):not(.q-menu--dark) .q-item__label,
            .q-menu:not(.q-dark):not(.q-menu--dark) .q-item__section {
                color: #000000 !important;
            }

            /* Toggle switch track color — inactive (both modes) */
            /* Toggle switch track color — inactive (both modes) */
            .q-toggle__track {
                opacity: 0.5 !important;
                background: #808080 !important;
            }

            /* Toggle switch track color — active/on state */
            .q-toggle__inner--truthy .q-toggle__track {
                opacity: 1 !important;
                background: #808080 !important;
            }

            /* Toggle switch thumb color — light mode, off state */
            .q-field:not(.q-field--dark) .q-toggle__thumb:before,
            .q-toggle:not(.q-toggle--dark) .q-toggle__thumb:before {
                background: #ffffff !important;
            }
        </style>
        """)

        # Define the app's color palette used by Quasar components throughout the UI
        # Define the app's color palette used by Quasar components throughout the UI
        ui.colors(
            primary="#FFFFFF",
            backbtn="#a0a0a0",  # Grey — used for Back buttons
            backHover="#808080",  # Darker grey — Back button hover state
            facultyBegin="#8095e4",  # Light purple — Faculty button gradient start
            facultyEnd="#a855f7",  # Dark purple — Faculty button gradient end
            courseBegin="#EDC54E",  # Yellow/orange — Course button gradient start
            courseEnd="#ED764E",  # Orange — Course button gradient end
            roomBegin="#4EEDA0",  # Cyan/green — Room button gradient start
            roomEnd="#4EEAED",  # Cyan — Room button gradient end
            conflictBegin="#f94680",  # Pink/red — Conflict button gradient start
            conflictEnd="#eb0e19",  # Red — Conflict button gradient end
            labBegin="#1bc0ba",  # Teal — Lab button gradient start
            labEnd="#19fa11",  # Bright green — Lab button gradient end
        )
