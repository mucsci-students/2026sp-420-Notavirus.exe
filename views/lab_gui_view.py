# views/lab_gui_view.py
"""
LabGUIView - Graphical-user interface for lab interactions

This view class handles all files for the GUI that are related to labs.
"""
from nicegui import ui

from views.gui_theme import GUITheme

class LabGUIView:
    _lab_controller = None
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
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Lab').classes('text-4xl mb-10 text-black')

            ui.button('Add Lab').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/add'))
            ui.button('Modify Lab').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/modify'))
            ui.button('Delete Lab').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/delete'))
            ui.button('View Lab').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

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
        ui.query('body').style('background-color: var(--q-add)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab'))

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
        ui.query('body').style('background-color: var(--q-modify)')

        labs = LabGUIView._lab_controller.model.get_all_labs() if LabGUIView._lab_controller else []

        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Modify Lab').classes('text-4xl mb-10 text-black')

            existing_lab = ui.select(labs, label='Select Lab to Modify').props('rounded outlined').classes('w-80')
            modified_lab = ui.input(label='Modified Lab').props('rounded outlined').classes('w-80')

            result_label = ui.label('').classes('text-base')

            def save():
                try:
                    success, message = LabGUIView._lab_controller.gui_modify_lab(
                        existing_lab.value, modified_lab.value.strip()
                    )
                    result_label.set_text(message)
                    if success:
                        existing_lab.set_options(LabGUIView._lab_controller.model.get_all_labs())
                        modified_lab.set_value('')

                except Exception as e:
                    result_label.set_text(f'Error: {e}')
            ui.button('Save').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', save)
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab'))

    controller = None

    @classmethod
    def setup(cls, controller):
        """
        Injects the controller into the GUI View.
        """
        cls.controller = controller

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
        ui.query('body').style('background-color: var(--q-delete)')
        
        # Load labs from controller
        if LabGUIView.controller:
            initial_labs = LabGUIView.controller.get_all_labs()
        else:
            initial_labs = []

        # State to track modifications before saving
        state = {
            'labs': list(initial_labs),
            'deleted_labs': [],
            'selected_labs': []
        }

        def on_delete():
            if state['selected_labs']:
                for lab in state['selected_labs']:
                    if lab in state['labs']:
                        state['labs'].remove(lab)
                        state['deleted_labs'].append(lab)
                state['selected_labs'] = []
                update_lab_list()

        def on_save():
            if not state['deleted_labs']:
                ui.notify('No changes to save.', type='info')
                return
                
            if LabGUIView.controller and LabGUIView.controller.delete_labs_gui(state['deleted_labs']):
                ui.notify('Changes saved successfully!', type='positive')
                state['deleted_labs'] = []
                ui.navigate.to('/lab')
            else:
                ui.notify('Error saving changes.', type='negative')

        def on_cancel():
            if state['deleted_labs']:
                with ui.dialog() as dialog, ui.card():
                    ui.label('Are you sure you want to discard your changes?').classes('text-lg')
                    with ui.row().classes('w-full justify-end mt-4'):
                        ui.button('No', on_click=dialog.close).props('flat text-color=black')
                        ui.button('Yes', on_click=lambda: (dialog.close(), ui.navigate.to('/lab'))).props('color=red text-color=white')
                dialog.open()
            else:
                ui.navigate.to('/lab')

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            ui.label('Delete Lab').classes('text-4xl mb-10 text-black')
            
            # The list box (scrollable)
            with ui.card().classes('w-96 h-80 border-2 border-black shadow-none p-0'):
                with ui.scroll_area().classes('w-full h-full p-4'):
                    list_container = ui.column().classes('w-full')

            def update_lab_list():
                list_container.clear()
                with list_container:
                    if not state['labs']:
                        ui.label('No labs available.').classes('text-gray-500 m-auto mt-4')
                    else:
                        for lab in state['labs']:
                            checked = lab in state['selected_labs']
                            def toggle(e, l=lab):
                                if e.value:
                                    if l not in state['selected_labs']:
                                        state['selected_labs'].append(l)
                                else:
                                    if l in state['selected_labs']:
                                        state['selected_labs'].remove(l)
                            ui.checkbox(lab, value=checked, on_change=toggle).classes('w-full text-lg')
            
            update_lab_list()
            
            # Delete button (centered below list)
            ui.button('Delete').props('rounded color=red text-color=white no-caps').classes('w-40 h-10 text-lg mt-6 shadow-none').on('click', on_delete)
            
            ui.space().classes('h-10') # Spacer
            
            # Cancel and Save Buttons
            with ui.row().classes('gap-12 mt-4'):
                ui.button('Cancel').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', on_cancel)
                ui.button('Save').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', on_save)

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
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab'))
