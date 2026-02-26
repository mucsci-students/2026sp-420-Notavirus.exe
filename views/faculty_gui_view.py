# views/faculty_gui_view.py
"""
FacultyGUIView - Graphical-user interface for faculty interactions

This view class handles all files for the GUI that are related to faculty.
"""
from nicegui import ui
from views.gui_theme import GUITheme

class FacultyGUIView:
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
        GUITheme.applyTheming()

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Faculty').classes('text-4xl mb-10 !text-black dark:!text-white')

            ui.button('Add Faculty').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-facultyBegin), var(--q-facultyEnd)) !important;').on('click', lambda: ui.navigate.to('/faculty/add'))
            ui.button('Modify Faculty').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-facultyBegin), var(--q-facultyEnd)) !important;').on('click', lambda: ui.navigate.to('/faculty/modify'))
            ui.button('Delete Faculty').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-facultyBegin), var(--q-facultyEnd)) !important;').on('click', lambda: ui.navigate.to('/faculty/delete'))
            ui.button('View Faculty').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-facultyBegin), var(--q-facultyEnd)) !important;').on('click', lambda: ui.navigate.to('/faculty/view'))
            ui.space()
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/faculty'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/faculty'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/faculty'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/faculty'))
