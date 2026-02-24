# views/schedule_gui_view.py
from nicegui import ui
from gui_theme import GUITheme

class ScheduleGUIView:
    @ui.page('/schedule/view')
    @staticmethod
    def schedule_view():
        """
        Displays the GUI for viewing a schedule.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))
