# views/conflict_gui_view.py
"""
ConflictGUIView - Graphical-user interface for conflict interactions

This view class handles all files for the GUI that are related to conflicts.
"""
from nicegui import ui
from views.gui_theme import GUITheme

class ConflictGUIView:
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
        GUITheme.applyTheming()
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Conflict').classes('text-4xl mb-10 !text-black dark:!text-white')

            ui.button('Add Conflict').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-conflictBegin), var(--q-conflictEnd)) !important;').on('click', lambda: ui.navigate.to('/conflict/add'))
            ui.button('Modify Conflict').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-conflictBegin), var(--q-conflictEnd)) !important;').on('click', lambda: ui.navigate.to('/conflict/modify'))
            ui.button('Delete Conflict').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-conflictBegin), var(--q-conflictEnd)) !important;').on('click', lambda: ui.navigate.to('/conflict/delete'))
            ui.button('View Conflict').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-conflictBegin), var(--q-conflictEnd)) !important;').on('click', lambda: ui.navigate.to('/conflict/view'))
            ui.space()
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/conflict'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/conflict'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/conflict'))

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
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/conflict'))
