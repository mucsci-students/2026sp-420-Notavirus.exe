# views/gui_view.py
"""
GUIView - Graphical-user interface for all user interactions

This view class handles all user input/output for the GUI across
all features: faculty, courses, conflicts, labs, courses, and scheduling.
"""

from nicegui import ui
from faculty_gui_view import FacultyGUIView
from course_gui_view import CourseGUIView
from conflict_gui_view import ConflictGUIView
from lab_gui_view import LabGUIView
from schedule_gui_view import ScheduleGUIView
from faculty_gui_view import FacultyGUIView
from room_gui_view import RoomGUIView
from gui_theme import GUITheme

class GUIView:
    @ui.page('/')
    @staticmethod
    def home():
        # Set light blue background matching the mockup
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')        
        # Center the main column
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            
            # Title
            ui.label('Scheduler').classes('text-4xl mb-10 text-black')
            
            # Row 1
            with ui.row().classes('gap-12 mb-4'):
                ui.button('Faculty').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))
                ui.button('Room').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/room'))
                
            # Row 2
            with ui.row().classes('gap-12 mb-4'):
                ui.button('Course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course'))
                ui.button('Conflict').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict'))
                
            # Row 3 (Lab)
            with ui.row().classes('mb-12'):
                ui.button('Lab').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab'))
                
            # Wide buttons vertically stacked
            with ui.column().classes('gap-6 items-center w-full'):
                ui.button('Print Config').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/print_config'))
                ui.button('Run Scheduler').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/run_scheduler'))
                ui.button('Display Schedules').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/display_schedules'))


    @ui.page('/print_config')
    @staticmethod
    def print_config():
        """
        Displays the GUI for printing the config file.
                
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

ui.run()