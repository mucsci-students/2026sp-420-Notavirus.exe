# views/course_gui_view.py
"""
CourseGUIView - Graphical-user interface for course interactions

This view class handles all files for the GUI that are related to courses.
"""
from nicegui import ui
from views.gui_theme import GUITheme

class CourseGUIView:
    @ui.page('/course')
    @staticmethod
    def course():
        """
        Displays the GUI for Course.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Course').classes('text-4xl mb-10 !text-black dark:!text-white')

            ui.button('Add Course').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-courseBegin), var(--q-courseEnd)) !important;').on('click', lambda: ui.navigate.to('/course/add'))
            ui.button('Modify Course').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-courseBegin), var(--q-courseEnd)) !important;').on('click', lambda: ui.navigate.to('/course/modify'))
            ui.button('Delete Course').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-courseBegin), var(--q-courseEnd)) !important;').on('click', lambda: ui.navigate.to('/course/delete'))
            ui.button('View Course').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-courseBegin), var(--q-courseEnd)) !important;').on('click', lambda: ui.navigate.to('/course/view'))
            ui.space()
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/course'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/course'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/course'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/course'))
