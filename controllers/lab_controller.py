# controllers/lab_controller.py
"""
LabController - Coordinates lab-related workflows

This controller class manages all lab workflows including:
- Adding new labs
- Modifying existing labs
- Deleting labs
- Validating lab data
"""


class LabController:
    """
    Controller for lab operations.
    
    Coordinates between LabModel (data) and CLIView (UI) to
    implement complete lab workflows.
    
    Attributes:
        model: LabModel instance
        view: CLIView instance
    """
    
    def __init__(self, lab_model, view):
        """
        Initialize LabController.
        
        Parameters:
            lab_model (LabModel): Model for lab data operations
            view (CLIView): View for user interface
        
        Returns:
            None
        """
        self.model = lab_model
        self.view = view
    
    def add_lab(self):
        """
        Complete workflow for adding a new lab.
        
        Steps:
        1. Display existing labs
        2. Get lab name from user
        3. Confirm
        4. Add via Model
        5. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Display existing labs
            existing_labs = self.model.get_all_labs()
            self.view.display_lab_list(existing_labs)
            
            # Step 2: Get lab name
            lab_name = self.view.get_lab_name_input()
            
            # Step 3: Confirm
            if not self.view.confirm("Is this information correct?"):
                # Ask if they want to restart
                if self.view.confirm("Would you like to restart adding the lab?"):
                    return self.add_lab()  # Recursive restart
                else:
                    self.view.display_message("Lab addition cancelled.")
                    return
            
            # Step 4: Add via model
            success = self.model.add_lab(lab_name)
            
            # Step 5: Display result
            if success:
                self.view.display_message(f"Lab '{lab_name}' added successfully.")
            else:
                self.view.display_error(f"Lab '{lab_name}' already exists.")
        
        except Exception as e:
            self.view.display_error(f"Failed to add lab: {e}")
    
    def delete_lab(self):
        """
        Complete workflow for deleting a lab.
        
        Steps:
        1. Display list of labs
        2. Get lab selection from user
        3. Confirm deletion
        4. Delete via Model
        5. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Get labs
            all_labs = self.model.get_all_labs()
            
            if not all_labs:
                self.view.display_message("No labs exist. Cannot delete a lab.")
                return
            
            # Display numbered list
            self.view.display_numbered_labs(all_labs)
            
            # Step 2: Get selection
            selection = self.view.get_lab_selection(len(all_labs))
            
            if selection == -1:
                self.view.display_message("Quitting deleting a lab.")
                return
            
            lab_name = all_labs[selection]
            
            # Step 3: Confirm deletion
            if not self.view.confirm(f"Are you sure you want to delete {lab_name}?"):
                self.view.display_message("Quitting deleting a lab.")
                return
            
            # Step 4: Delete via model
            success = self.model.delete_lab(lab_name)
            
            # Step 5: Display result
            if success:
                self.view.display_message("Lab deleted.")
            else:
                self.view.display_error("Failed to delete lab.")
        
        except Exception as e:
            self.view.display_error(f"Failed to delete lab: {e}")
    
    def modify_lab(self):
        """
        Complete workflow for modifying a lab.
        
        Steps:
        1. Display list of labs
        2. Get lab to modify
        3. Get new name
        4. Display affected courses/faculty
        5. Confirm modification
        6. Apply via Model
        7. Display result
        
        Parameters:
            None
        
        Returns:
            None
        """
        try:
            # Step 1: Get labs
            all_labs = self.model.get_all_labs()
            
            if not all_labs:
                self.view.display_message("No labs available.")
                return
            
            # Display current labs
            print("\n--- Modify Lab ---")
            print(f"Current labs: {', '.join(all_labs)}")
            
            # Step 2: Get lab to modify
            old_name = self.view.get_lab_to_modify(all_labs)
            
            if old_name is None:
                self.view.display_message("Cancelled.")
                return
            
            # Step 3: Get new name
            new_name = self.view.get_new_lab_name(old_name, all_labs)
            
            if new_name is None:
                return
            
            # Step 4: Display affected items
            affected_courses = self.model.get_affected_courses(old_name)
            affected_faculty = self.model.get_affected_faculty(old_name)
            
            self.view.display_lab_modification_summary(
                old_name,
                new_name,
                affected_courses,
                affected_faculty
            )
            
            # Step 5: Confirm
            if not self.view.confirm("Proceed with these changes?"):
                self.view.display_message("Cancelled, no changes made.")
                return
            
            # Step 6: Apply modification
            success = self.model.modify_lab(old_name, new_name)
            
            # Step 7: Display result
            if success:
                self.view.display_message(f"Lab successfully updated to '{new_name}'.")
            else:
                self.view.display_error("Failed to modify lab.")
        
        except Exception as e:
            self.view.display_error(f"Failed to modify lab: {e}")

    def get_all_labs(self) -> list[str]:
        """
        Retrieves all labs from the model for the GUI.
                
        Parameters:
            None        
        Returns:
            list[str]: A list of lab names.
        """
        return self.model.get_all_labs()

    def delete_labs_gui(self, labs_to_delete: list[str]) -> bool:
        """
        Deletes a list of labs from the model for the GUI.
                
        Parameters:
            labs_to_delete (list[str]): List of lab names to delete.
        Returns:
            bool: True if all deletions were successful, False otherwise.
        """
        success = True
        for lab in labs_to_delete:
            if not self.model.delete_lab(lab):
                success = False
        return success