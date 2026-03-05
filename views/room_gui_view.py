# views/room_gui_view.py
"""
RoomGUIView - Graphical-user interface for room interactions

This view class handles all files for the GUI that are related to rooms.
"""
from nicegui import ui
from views.gui_theme import GUITheme
from controllers.room_controller import RoomController


class RoomGUIView:
    

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
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Room').classes('text-4xl mb-10 text-black')

            ui.button('Add Room').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/room/add'))
            ui.button('Modify Room').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/room/modify'))
            ui.button('Delete Room').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/room/delete'))
            ui.button('View Room').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/room/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

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
        def handle_add():
            success = RoomGUIView.room_controller.model.add_room(room_input.value)

            if success:
                result_label.set_text("Room added successfully.")
                
            else:
                result_label.set_text("Room already exists or invalid.")
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-add)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Add Room').classes('text-3xl')

            # Display existing rooms
            rooms = RoomGUIView.room_controller.model.get_all_rooms()
            ui.label("Existing Rooms:")
            with ui.list():
                for r in rooms:
                    ui.item(r)
            # Input
            room_input = ui.input("Room name and number")

            result_label = ui.label()
            ui.button("Save to config").on("click", handle_add).props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl')
            ui.button("Save").on("click", handle_add).props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/room'))




    @ui.page('/room/modify')
    @staticmethod
    def room_modify():

        def handle_modify():
                if not selected_room.value:
                    result_label.set_text("Select a room first.")
                    return

                success = RoomGUIView.room_controller.model.modify_room(
                    selected_room.value,
                    new_name.value
                )

                if success:
                    result_label.set_text("Room modified.")
                    
                else:
                    result_label.set_text("Modification failed.")

        GUITheme.applyTheming()

        with ui.column().classes('gap-6 items-center w-full'):

            ui.label('Modify Room').classes('text-3xl')

            rooms = RoomGUIView.room_controller.model.get_all_rooms()

            selected_room = ui.select(options=rooms, label="Select Room")
            new_name = ui.input("New Room Name")

            result_label = ui.label()

            
            ui.button("Save to Config").on("click", handle_modify).props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl')
            ui.button("Save").on("click", handle_modify).props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/room'))

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
        ui.query('body').style('background-color: var(--q-delete)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
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
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/room'))
