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
        dark = ui.dark_mode().bind_value(app.storage.user, 'dark_mode')
        ui.button(icon='brightness_4', on_click=dark.toggle).props('flat round').classes('absolute top-4 right-4 z-50 !text-black dark:!text-white')

        # Fix dropdown text color for light/dark mode.
        # q-field--dark is on the field element in dark mode (confirmed via DevTools).
        # q-menu--dark / q-dark are on the menu popup in dark mode (confirmed via console).
        # html.dark does NOT reliably exist at runtime, so we avoid it.
        ui.add_head_html('''
        <style>
            /* Dark mode: selected value in field */
            .q-field--dark .q-field__native span {
                color: #ffffff !important;
            }

            /* Light mode: selected value in field - only when NOT dark */
            .q-field:not(.q-field--dark) .q-field__native span {
                color: #000000 !important;
            }

            /* Dark mode: dropdown popup background and text */
            .q-menu.q-dark,
            .q-menu.q-menu--dark {
                background: #000000 !important;
                color: #ffffff !important;
            }
            .q-menu.q-dark *,
            .q-menu.q-menu--dark * {
                color: #ffffff !important;
            }

            /* Light mode: dropdown popup */
            .q-menu:not(.q-dark):not(.q-menu--dark) {
                background: #ffffff !important;
                color: #000000 !important;
            }
            .q-menu:not(.q-dark):not(.q-menu--dark) * {
                color: #000000 !important;
            }
        </style>
        ''')

        ui.colors(
            primary='#FFFFFF',
            backbtn= '#a0a0a0', #Grey
            backHover='#808080', #Darker grey
            facultyBegin='#8095e4', #Light Purple
            facultyEnd='#a855f7', #Dark Purple
            courseBegin='#EDC54E', #Orange
            courseEnd='#ED764E', #Orange
            roomBegin='#4EEDA0', #Cyan/Green
            roomEnd='#4EEAED', #Cyan
            conflictBegin='#f94680', #Red
            conflictEnd='#eb0e19', #Red
            labBegin='#1bc0ba', #Green
            labEnd='#19fa11', #Green
        )