# views/faculty_gui_view.py
from nicegui import ui
from gui_theme import GUITheme

class FacultyGUIView:
    @ui.page('/faculty')
    @staticmethod
    def faculty():
        """
        Displays the GUI for Faculty.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Faculty').classes('text-4xl mb-10 text-black')

            ui.button('Add Faculty').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/add'))
            ui.button('Modify Faculty').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/modify'))
            ui.button('Delete Faculty').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/delete'))
            ui.button('View Faculty').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/faculty/add')
    @staticmethod
    def faculty_add():
        """
        Displays the GUI for adding faculty.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

    @ui.page('/faculty/modify')
    @staticmethod
    def faculty_modify():
        """
        Displays the GUI for modifying faculty.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

    @ui.page('/faculty/delete')
    @staticmethod
    def faculty_delete():
        """
        Displays the GUI for deleting faculty.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass

    @ui.page('/faculty/view')
    @staticmethod
    def faculty_view():
        """
        Displays the GUI for viewing faculty.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass