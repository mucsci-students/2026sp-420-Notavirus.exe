# views/schedule_gui_view.py
"""
ScheduleGUIView - Graphical-user interface for schedule interactions

This view class handles all files for the GUI that are related to schedules.
"""
from nicegui import ui
from views.gui_theme import GUITheme

class ScheduleGUIView:
    @ui.page('/run_scheduler')
    @staticmethod
    def run_scheduler():
        """
        Displays the GUI for running the scheduler.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/display_schedules')
    @staticmethod
    def display_schedules():
        """
        Displays the GUI for displaying schedules.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))