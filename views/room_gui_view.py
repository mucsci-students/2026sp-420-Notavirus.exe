# views/room_gui_view.py
"""
RoomGUIView - Graphical-user interface for room interactions

This view class handles all files for the GUI that are related to rooms.
"""
from nicegui import ui
from views.gui_theme import GUITheme

class RoomGUIView:
    @ui.page('/room')
    @staticmethod
    def room():
        """
        Displays the GUI for room.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Room').classes('text-4xl mb-10 !text-black dark:!text-white')

            ui.button('Add Room').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-roomBegin), var(--q-roomEnd)) !important;').on('click', lambda: ui.navigate.to('/room/add'))
            ui.button('Modify Room').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-roomBegin), var(--q-roomEnd)) !important;').on('click', lambda: ui.navigate.to('/room/modify'))
            ui.button('Delete Room').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-roomBegin), var(--q-roomEnd)) !important;').on('click', lambda: ui.navigate.to('/room/delete'))
            ui.button('View Room').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-roomBegin), var(--q-roomEnd)) !important;').on('click', lambda: ui.navigate.to('/room/view'))
            ui.space()
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/room/add')
    @staticmethod
    def room_add():
        """
        Displays the GUI for adding a room.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/room'))

    @ui.page('/room/modify')
    @staticmethod
    def room_modify():
        """
        Displays the GUI for modifying a room.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/room'))

    @ui.page('/room/delete')
    @staticmethod
    def room_delete():
        """
        Displays the GUI for deleting a room.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/room'))

    @ui.page('/room/view')
    @staticmethod
    def room_view():
        """
        Displays the GUI for viewing a room.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/room'))
