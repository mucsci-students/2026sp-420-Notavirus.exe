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

        Changes are in-memory until Save Configuration is clicked.

        Parameters:
            None
        Returns:
            None
        """
        from views.gui_view import GUIView

        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')

        labs = LabGUIView._lab_controller.model.get_all_labs() if LabGUIView._lab_controller else []
        config_model = GUIView.controller.config_model

        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Modify Lab').classes('text-4xl mb-10 text-black')

            existing_lab = ui.select(labs, label='Select Lab to Modify').props('rounded outlined').classes('w-80')
            modified_lab = ui.input(label='Modified Lab').props('rounded outlined').classes('w-80')

            result_label = ui.label('').classes('text-base')
            save_label = ui.label('').classes('text-base')

            def save():
                try:
                    success, message = LabGUIView._lab_controller.gui_modify_lab(
                        existing_lab.value, modified_lab.value.strip()
                    )
                    result_label.set_text(message)
                    if success:
                        existing_lab.set_options(LabGUIView._lab_controller.model.get_all_labs())
                        modified_lab.set_value('')
                        save_label.set_text('You have unsaved changes. Click Save Configuration to persist.')
                        save_label.classes(replace='text-base text-orange-500')
                except Exception as e:
                    result_label.set_text(f'Error: {e}')

            def handle_save():
                success = config_model.safe_save()
                if success:
                    save_label.set_text('Configuration saved successfully.')
                    save_label.classes(replace='text-base text-green-600')
                else:
                    save_label.set_text('Save failed. Check terminal for details.')
                    save_label.classes(replace='text-base text-red-600')

            ui.button('Save').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', save)
            ui.button('Save Configuration').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', handle_save)
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab'))

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
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab'))

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