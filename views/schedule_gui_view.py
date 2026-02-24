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
        pass
