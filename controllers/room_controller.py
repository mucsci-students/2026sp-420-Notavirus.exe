# controllers/room_controller.py
"""
RoomController - Coordinates room-related workflows

This controller class manages all room workflows including:
- Adding new rooms
- Modifying existing rooms
- Deleting rooms
- Validating room data
"""


class RoomController:
    """
    Controller for room operations.
    
    Coordinates between RoomModel (data) and CLIView (UI) to
    implement complete room workflows.
    
    Attributes:
        model: RoomModel instance
        view: CLIView instance
    """
    
    def __init__(self, room_model, view):
        """
        Initialize RoomController.
        
        Parameters:
            room_model (RoomModel): Model for room data operations
            view (CLIView): View for user interface
        
        Returns:
            None
        """
        self.model = room_model
        self.view = view
    
    def add_room(self):
        """
        Complete workflow for adding new room(s).
        
        Allows user to add multiple rooms in one session.
        
        Steps:
        1. Get room information (building + number)
        2. Validate and add via Model
        3. Ask if user wants to add another
        4. Repeat until done
        
        Parameters:
            None
        
        Returns:
            None
        """
        while True:
            try:
                # Step 1: Get room name
                room_name = self.view.get_room_input()
                
                # Validate not blank
                if not room_name.strip():
                    self.view.display_error("Room cannot be blank.")
                    continue
                
                # Step 2: Add via model
                success = self.model.add_room(room_name)
                
                if success:
                    self.view.display_message("Room added.")
                else:
                    self.view.display_error(f"Room '{room_name}' already exists.")
                
                # Step 3: Ask if user wants to add another
                if not self.view.confirm("Add another room?"):
                    break
            
            except Exception as e:
                self.view.display_error(f"Failed to add room: {e}")
                break
    
    def delete_room(self):
        """
        Complete workflow for deleting a room.
        
        Steps:
        1. Display list of rooms
        2. Get room name from user
        3. Confirm deletion
        4. Delete via Model
        5. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Get rooms
            all_rooms = self.model.get_all_rooms()
            
            if not all_rooms:
                self.view.display_message("There are no rooms in the configuration.")
                return
            
            # Display numbered list
            self.view.display_numbered_rooms(all_rooms)
            
            # Step 2: Get room name
            room_name = self.view.get_room_name_for_deletion()
            
            # Check if room exists
            if not self.model.room_exists(room_name):
                self.view.display_error(f"No room '{room_name}' found. No changes were made.")
                return
            
            # Step 3: Confirm deletion
            if not self.view.confirm(f"Are you sure you want to delete room '{room_name}'?"):
                self.view.display_message("Deletion cancelled.")
                return
            
            # Step 4: Delete via model
            success = self.model.delete_room(room_name)
            
            # Step 5: Display result
            if success:
                self.view.display_message(f"Room '{room_name}' has been successfully deleted.")
            else:
                self.view.display_error("Failed to delete room.")
        
        except Exception as e:
            self.view.display_error(f"Failed to delete room: {e}")
    
    def modify_room(self):
        """
        Complete workflow for modifying room(s).
        
        Allows user to modify multiple rooms in one session.
        Can modify either the building name or room number.
        
        Steps:
        1. Get room to modify
        2. Ask what to modify (building or number)
        3. Get new value
        4. Build new room name
        5. Apply via Model
        6. Ask if user wants to modify another
        7. Repeat until done
        
        Parameters:
            None
        
        Returns:
            None
        """
        while True:
            try:
                # Step 1: Get room to modify
                room_name = self.view.get_room_input()
                
                # Check if room exists
                if not self.model.room_exists(room_name):
                    self.view.display_error(f"Room '{room_name}' does not exist. Cannot modify.")
                    
                    # Ask if they want to try another
                    if not self.view.confirm("Modify another room?"):
                        break
                    continue
                
                # Step 2: Ask what to modify
                modify_choice = self.view.get_room_modify_choice()
                
                # Step 3 & 4: Get new value and build new room name
                building, number = self._split_room_name(room_name)
                
                if modify_choice == "building":
                    new_building = self.view.get_room_building_input()
                    new_room_name = self._build_room_name(new_building, number)
                elif modify_choice == "number":
                    new_number = self.view.get_room_number_input()
                    new_room_name = self._build_room_name(building, new_number)
                else:
                    self.view.display_error("Invalid modification choice.")
                    continue
                
                # Step 5: Apply modification
                success = self.model.modify_room(room_name, new_room_name)
                
                if success:
                    self.view.display_message(f"Room modified from '{room_name}' to '{new_room_name}'.")
                else:
                    self.view.display_error(f"Cannot update to '{new_room_name}'. Room already exists or modification failed.")
                
                # Step 6: Ask if user wants to modify another
                if not self.view.confirm("Modify another room?"):
                    break
            
            except Exception as e:
                self.view.display_error(f"Failed to modify room: {e}")
                break
    
    def _split_room_name(self, room_name: str) -> tuple[str, str]:
        """
        Split room name into building and number.
        
        Parameters:
            room_name (str): Full room name (e.g., "Roddy 140")
        
        Returns:
            tuple[str, str]: (building, number)
        """
        parts = room_name.partition(" ")
        return (parts[0], parts[2])
    
    def _build_room_name(self, building: str, number: str) -> str:
        """
        Build room name from building and number.
        
        Parameters:
            building (str): Building name
            number (str): Room number
        
        Returns:
            str: Full room name (e.g., "Roddy 140")
        """
        return f"{building.capitalize()} {number}"