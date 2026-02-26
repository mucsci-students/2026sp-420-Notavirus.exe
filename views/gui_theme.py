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
            facultyBegin='#a855f7', #Light Purple
            facultyEnd='#7c3aed', #Dark Purple
            courseBegin='#f0be41', #Orange/Gold
            courseEnd='#c48f08', #Orange/Gold
            roomBegin='#4cede7', #Cyan
            roomEnd='#3fbab4', #Cyan
            conflictBegin='#eb0e19', #Red
            conflictEnd='#a80a12', #Red
            labBegin='#19fa11', #Green
            labEnd='#13b80d', #Green
        )