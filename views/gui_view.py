# views/gui_view.py
"""
GUIView - Graphical-user interface for all user interactions

This view class handles all files for the GUI that don't have
their own files (i.e. the landing page, the navigation page, and currently including
print config, run scheduler, and display schedules)
"""

from nicegui import ui
from views.faculty_gui_view import FacultyGUIView
from views.course_gui_view import CourseGUIView
from views.conflict_gui_view import ConflictGUIView
from views.lab_gui_view import LabGUIView
from views.schedule_gui_view import ScheduleGUIView
from views.room_gui_view import RoomGUIView
from views.gui_theme import GUITheme

class GUIView:
    config_path: str = '' 
    controller = None 

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
    
    _controller = None

    @classmethod
    def set_controller(cls, controller):
        """
        Sets the main application controller reference.
        """
        cls._controller = controller

    @staticmethod
    def runGUI(controller=None):
        """
        Runs the GUI.
                
        Parameters:
            controller: The main SchedulerController instance
        Returns:        
            None
        """
        if controller:
            GUIView.set_controller(controller)
        ui.run(reload=False)

if __name__ in {"__main__", "__mp_main__"}:
    GUIView.runGUI()