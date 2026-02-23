# views/gui_view.py
"""
GUIView - Graphical-user interface for all user interactions

This view class handles all user input/output for the GUI across
all features: faculty, courses, conflicts, labs, courses, and scheduling.
"""

from nicegui import ui

class GUIView:
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

    @ui.page('/')
    @staticmethod
    def home():
        # Set light blue background matching the mockup
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')        
        # Center the main column
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            
            # Title
            ui.label('Scheduler').classes('text-4xl mb-10 text-black')
            
            # Row 1
            with ui.row().classes('gap-12 mb-4'):
                ui.button('Faculty').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))
                ui.button('course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course'))
                
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


    @ui.page('/faculty')
    @staticmethod
    def faculty():
        """
        Displays the GUI for Faculty.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Faculty').classes('text-4xl mb-10 text-black')

            ui.button('Add Faculty').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/add'))
            ui.button('Modify Faculty').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/modify'))
            ui.button('Delete Faculty').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/delete'))
            ui.button('View Faculty').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/course')
    @staticmethod
    def course():
        """
        Displays the GUI for course.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            
            # Title
            ui.label('course').classes('text-4xl mb-10 text-black')

            ui.button('Add course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/add'))
            ui.button('Modify course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/modify'))
            ui.button('Delete course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/delete'))
            ui.button('View course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/course')
    @staticmethod
    def course():
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            
            # Title
            ui.label('Course').classes('text-4xl mb-10 text-black')

            ui.button('Add Course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/add'))
            ui.button('Modify Course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/modify'))
            ui.button('Delete Course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/delete'))
            ui.button('View Course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/conflict')
    @staticmethod
    def conflict():
        """
        Displays the GUI for Conflict.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            
            # Title
            ui.label('Conflict').classes('text-4xl mb-10 text-black')

            ui.button('Add Conflict').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict/add'))
            ui.button('Modify Conflict').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict/modify'))
            ui.button('Delete Conflict').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict/delete'))
            ui.button('View Conflict').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/lab')
    @staticmethod
    def lab():
        """
        Displays the GUI for Lab.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            
            # Title
            ui.label('Lab').classes('text-4xl mb-10 text-black')

            ui.button('Add Lab').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/add'))
            ui.button('Modify Lab').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/modify'))
            ui.button('Delete Lab').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/delete'))
            ui.button('View Lab').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

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
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

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
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

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
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

    @ui.page('/faculty/add')
    @staticmethod
    def faculty_add():
        """
        Displays the GUI for adding faculty.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

    @ui.page('/faculty/modify')
    @staticmethod
    def faculty_modify():
        """
        Displays the GUI for modifying faculty.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

    @ui.page('/faculty/delete')
    @staticmethod
    def faculty_delete():
        """
        Displays the GUI for deleting faculty.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

    @ui.page('/faculty/view')
    @staticmethod
    def faculty_view():
        """
        Displays the GUI for viewing faculty.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass
    
    @ui.page('/course/add')
    @staticmethod
    def course_add():
        """
        Displays the GUI for adding a course.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-add)')
        pass

    @ui.page('/course/modify')
    @staticmethod
    def course_modify():
        """
        Displays the GUI for modifying a course.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')
        pass

    @ui.page('/course/delete')
    @staticmethod
    def course_delete():
        """
        Displays the GUI for deleting a course.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-delete)')
        pass

    @ui.page('/course/view')
    @staticmethod
    def course_view():
        """
        Displays the GUI for viewing a course.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

    @ui.page('/course/add')
    @staticmethod
    def course_add():
        """
        Displays the GUI for adding a course.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-add)')
        pass

    @ui.page('/course/modify')
    @staticmethod
    def course_modify():
        """
        Displays the GUI for modifying a course.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')
        pass

    @ui.page('/course/delete')
    @staticmethod
    def course_delete():
        """
        Displays the GUI for deleting a course.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-delete)')
        pass

    @ui.page('/course/view')
    @staticmethod
    def course_view():
        """
        Displays the GUI for viewing a course.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

    @ui.page('/conflict/add')
    @staticmethod
    def conflict_add():
        """
        Displays the GUI for adding a conflict.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-add)')
        pass

    @ui.page('/conflict/modify')
    @staticmethod
    def conflict_modify():
        """
        Displays the GUI for modifying a conflict.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')
        pass

    @ui.page('/conflict/delete')
    @staticmethod
    def conflict_delete():
        """
        Displays the GUI for deleting a conflict.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-delete)')
        pass

    @ui.page('/conflict/view')
    @staticmethod
    def conflict_view():
        """
        Displays the GUI for viewing a conflict.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

    @ui.page('/lab/add')
    @staticmethod
    def lab_add():
        """
        Displays the GUI for adding a lab.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-add)')
        pass

    @ui.page('/lab/modify')
    @staticmethod
    def lab_modify():
        """
        Displays the GUI for modifying a lab.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')
        pass

    @ui.page('/lab/delete')
    @staticmethod
    def lab_delete():
        """
        Displays the GUI for deleting a lab.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-delete)')
        pass

    @ui.page('/lab/view')
    @staticmethod
    def lab_view():
        """
        Displays the GUI for viewing a lab.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

    @ui.page('/schedule/view')
    @staticmethod
    def schedule_view():
        """
        Displays the GUI for viewing a schedule.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUIView.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

# Start the application
ui.run()