# views/course_gui_view.py
from nicegui import ui
from gui_theme import GUITheme

class CourseGUIView:
    @ui.page('/course')
    @staticmethod
    def course():
        """
        Displays the GUI for Course.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Course').classes('text-4xl mb-10 text-black')

            ui.button('Add Course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/add'))
            ui.button('Modify Course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/modify'))
            ui.button('Delete Course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/delete'))
            ui.button('View Course').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-40 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/course/add')
    @staticmethod
    def course_add():
        """
        Displays the GUI for adding a course.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-add)')
        pass

    @ui.page('/course/modify')
    @staticmethod
    def course_modify():
        """
        Displays the GUI for modifying a course.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')
        pass

    @ui.page('/course/delete')
    @staticmethod
    def course_delete():
        """
        Displays the GUI for deleting a course.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-delete)')
        pass

    @ui.page('/course/view')
    @staticmethod
    def course_view():
        """
        Displays the GUI for viewing a course.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        pass
