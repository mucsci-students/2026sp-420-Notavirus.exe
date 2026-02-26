# views/lab_gui_view.py
"""
LabGUIView - Graphical-user interface for lab interactions

This view class handles all files for the GUI that are related to labs.
"""
from nicegui import ui
from views.gui_theme import GUITheme

class LabGUIView:
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
        GUITheme.applyTheming()
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Lab').classes('text-4xl mb-10 !text-black dark:!text-white')

            ui.button('Add Lab').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-labBegin), var(--q-labEnd)) !important;').on('click', lambda: ui.navigate.to('/lab/add'))
            ui.button('Modify Lab').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-labBegin), var(--q-labEnd)) !important;').on('click', lambda: ui.navigate.to('/lab/modify'))
            ui.button('Delete Lab').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-labBegin), var(--q-labEnd)) !important;').on('click', lambda: ui.navigate.to('/lab/delete'))
            ui.button('View Lab').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-labBegin), var(--q-labEnd)) !important;').on('click', lambda: ui.navigate.to('/lab/view'))
            ui.space()
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/lab'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/lab'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/lab'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/lab'))
