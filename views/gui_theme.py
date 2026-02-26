#views/gui_theme.py
"""
GUITheme - Graphical-user interface theme

This view class handles all files for the GUI that are related to themes.
"""
from nicegui import ui

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
        ui.colors(
            primary='#c6d2fb',
            add='#bfecac',
            modify='#ffeb99',
            delete='#ff9999',
        )