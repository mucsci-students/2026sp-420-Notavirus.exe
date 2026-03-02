# views/room_gui_view.py
"""
RoomGUIView - Graphical-user interface for room interactions

This view class handles all files for the GUI that are related to rooms.
"""
from nicegui import ui
from views.gui_theme import GUITheme
from controllers.room_controller import RoomController


class RoomGUIView:
    """
    initiate the view with the controller
    and the pages with access to the controller
    
    """

    def __init__(self, controller):
        self.controller = controller
        ui.page('/room')(self.room)
        ui.page('/room/add')(self.room_add)
        ui.page('/room/modify')(self.room_modify)


    
    def room(self):
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

    
    def room_add(self):
        """
        Displays the GUI for adding a room.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-add)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Add Room').classes('text-3xl')

            # Display existing rooms
            rooms = self.controller.model.get_all_rooms()
            ui.label("Existing Rooms:")
            with ui.list():
                for r in rooms:
                    ui.item(r)
            # Input
            room_input = ui.input("Room name and number")

            result_label = ui.label()

        def handle_add():
            success = self.controller.model.add_room(room_input.value)

            if success:
                result_label.set_text("Room added successfully.")
                
            else:
                result_label.set_text("Room already exists or invalid.")

        ui.button("Save to config").on("click", handle_add).props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl')
        ui.button("save").on("click", handle_add).props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl')
        ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/room'))

    
    def room_modify(self):

        GUITheme.applyTheming()

        with ui.column().classes('gap-6 items-center w-full'):

            ui.label('Modify Room').classes('text-3xl')

            rooms = self.controller.model.get_all_rooms()

            selected_room = ui.select(options=rooms, label="Select Room")
            new_name = ui.input("New Room Name")

            result_label = ui.label()

            def handle_modify():
                if not selected_room.value:
                    result_label.set_text("Select a room first.")
                    return

                success = self.controller.model.modify_room(
                    selected_room.value,
                    new_name.value
                )

                if success:
                    result_label.set_text("Room modified.")
                    
                else:
                    result_label.set_text("Modification failed.")

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
