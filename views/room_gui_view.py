# views/room_gui_view.py
"""
RoomGUIView - Graphical-user interface for room interactions

This view class handles all files for the GUI that are related to rooms.
"""
from nicegui import ui
from views.gui_theme import GUITheme

class RoomGUIView:
    room_model = None
    room_controller = None

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
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/room'))

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
        from views.gui_view import GUIView

        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)').classes('dark:!bg-black')
        
        config_model = GUIView.controller.config_model

        with ui.column().classes('gap-6 items-center w-full'):
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))
            ui.label('Under Construction!').classes('text-4xl mb-10 !text-black dark:!text-white')

            save_label = ui.label('').classes('text-base')

            def handle_save():
                success = config_model.save_feature('config', 'rooms')
                if success:
                    save_label.set_text('Configuration saved successfully.')
                    save_label.classes(replace='text-base text-green-600')
                else:
                    save_label.set_text('Save failed. Check terminal for details.')
                    save_label.classes(replace='text-base text-red-600')

            ui.button('Save Configuration').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', handle_save)
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/room'))

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

        rooms = RoomGUIView.room_controller.model.get_all_rooms() if RoomGUIView.room_controller else []

        with ui.column().classes('gap-6 items-center w-full'):
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10').on('click', lambda: ui.navigate.to('/'))
            ui.label('Delete Room').classes('text-4xl mb-10 text-black')

            selected_room = ui.select(rooms, label='Select Room to Delete').props('rounded outlined').classes('w-80')

            result_label = ui.label('').classes('text-base')

            def delete():
                try:
                    success, message = RoomGUIView.room_controller.gui_delete_room(
                        selected_room.value
                    )
                    result_label.set_text(message)
                    if success:
                        updated_rooms = RoomGUIView.room_controller.model.get_all_rooms()
                        selected_room.set_options(updated_rooms)
                        selected_room.set_value(None)

                except Exception as e:
                    result_label.set_text(f'Error: {e}')

            ui.button('Delete').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', delete)
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/room'))

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
        ui.query('body').style('background-color: var(--q-primary)').classes('dark:!bg-black')
        with ui.column().classes('w-full items-center pt-12 pb-12 gap-4'):
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))
            ui.label('View Rooms').classes('text-4xl mb-6 !text-black dark:!text-white')

            rooms = RoomGUIView.room_model.get_all_rooms() if RoomGUIView.room_model else []

            if not rooms:
                ui.label('No rooms in configuration.').classes('text-gray-600')
            else:
                with ui.column().classes('w-full max-w-2xl gap-3'):
                    for room in rooms:
                        with ui.card().classes('w-full px-5 py-4'):
                            ui.label(room).classes('text-base font-semibold')

            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl mt-4 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/room'))
