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
    @ui.page('/')
    @staticmethod
    def home():
        # Set light blue background matching the mockup
        GUITheme.applyTheming()
        # Center the main column
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            
            # Title
            ui.label('Scheduler').classes('text-4xl mb-10 !text-black dark:!text-white')
            
            # Row 1
            with ui.row().classes('gap-12 mb-4'):
                ui.button('Faculty').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/faculty'))
                ui.button('Room').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/room'))
                
            # Row 2
            with ui.row().classes('gap-12 mb-4'):
                ui.button('Course').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/course'))
                ui.button('Conflict').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/conflict'))
                
            # Row 3 (Lab)
            with ui.row().classes('mb-12'):
                ui.button('Lab').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/lab'))
                
            # Wide buttons vertically stacked
            with ui.column().classes('gap-6 items-center w-full'):
                ui.button('Print Config').props('rounded no-caps').classes('w-80 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/print_config'))
                ui.button('Run Scheduler').props('rounded no-caps').classes('w-80 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/run_scheduler'))
                ui.button('Display Schedules').props('rounded no-caps').classes('w-80 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/display_schedules'))


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
        cm = GUIView.controller.config_model

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-6'):
            ui.label('Configuration').classes('text-4xl mb-10 text-black')

            with ui.expansion('Rooms', icon='meeting_room').classes('w-3/4'):
                for room in cm.get_all_rooms():
                    ui.label(room)

            with ui.expansion('Labs', icon='computer').classes('w-3/4'): 
                for lab in cm.get_all_labs():
                    ui.label(lab)

            with ui.expansion('Courses', icon='book').classes('w-3/4'):
                with ui.scroll_area().classes('w-full h-64'):
                    for course in cm.get_all_courses():
                        with ui.card().classes('w-full mb-2'):
                            with ui.row().classes('w-full justify-between items-center'):
                                ui.label(course.course_id).classes('font-bold text-lg')
                                ui.label(f'{course.credits} credits').classes('text-gray-500')
                            with ui.row().classes('gap-4'):
                                ui.label(f'Rooms: {", ".join(course.room) or "Any"}').classes('text-sm')
                                ui.label(f'Labs: {", ".join(course.lab) or "None"}').classes('text-sm')
                                ui.label(f'Faculty: {", ".join(course.faculty) or "Any"}').classes('text-sm')

            with ui.expansion('Faculty', icon='person').classes('w-3/4'):
                for f in cm.get_all_faculty():
                    with ui.expansion(f.name).classes('w-full'):
                        ui.label(f'Max credits: {f.maximum_credits}')
                        ui.label(f'Min credits: {f.minimum_credits}')

                        for day, slots in f.times.items():
                            ui.label(f'{day}: {", ".join(str(s) for s in slots) or "Unavailable"}')

            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))
    
    @staticmethod
    def runGUI():
        """
        Runs the GUI.
                
        Parameters:
            None        
        Returns:        
            None
        """
        ui.run(title='Scheduler', storage_secret='scheduler_secret_key')

if __name__ in {"__main__", "__mp_main__"}:
    GUIView.runGUI()