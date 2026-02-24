# views/lab_gui_view.py
from nicegui import ui
from gui_theme import GUITheme

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
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Lab').classes('text-4xl mb-10 text-black')

            ui.button('Add Lab').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/add'))
            ui.button('Modify Lab').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/modify'))
            ui.button('Delete Lab').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/delete'))
            ui.button('View Lab').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/lab/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

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
        pass

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
        pass

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
        pass

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
        pass
