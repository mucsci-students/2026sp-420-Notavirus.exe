#views/gui_theme.py
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