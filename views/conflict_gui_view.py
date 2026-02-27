# views/conflict_gui_view.py
"""
ConflictGUIView - Graphical-user interface for conflict interactions

This view class handles all files for the GUI that are related to conflicts.
"""
import asyncio
from nicegui import ui
from views.gui_theme import GUITheme

class ConflictGUIView:
    @ui.page('/conflict')
    @staticmethod
    def conflict():
        """
        Displays the GUI for Conflict.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            # Title
            ui.label('Conflict').classes('text-4xl mb-10 text-black')

            ui.button('Add Conflict').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict/add'))
            ui.button('Modify Conflict').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict/modify'))
            ui.button('Delete Conflict').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict/delete'))
            ui.button('View Conflict').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/conflict/add')
    @staticmethod
    def conflict_add():
        """
        Displays the GUI for adding a conflict.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-add)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict'))

    @ui.page('/conflict/modify')
    @staticmethod
    def conflict_modify():
        """
        Displays the GUI for modifying a conflict.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict'))

    @ui.page('/conflict/delete')
    @staticmethod
    def conflict_delete():
        from views.gui_view import GUIView
        from models.scheduler_model import SchedulerModel

        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-delete)')

        controller = GUIView.controller.conflict_controller
        scheduler_model = SchedulerModel(GUIView.controller.config_model)
        existing_conflicts = controller.gui_get_all_conflicts()

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans gap-6'):
            ui.label('Delete Conflict').classes('text-4xl mb-4 text-black')

            if not existing_conflicts:
                ui.label('There are no conflicts currently in the configuration.').classes('text-xl text-black')
                ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict'))
                return

            sections_loaded = {'done': False}
            scheduler_status = ui.label('').classes('text-lg text-black')

            with ui.expansion('View Existing Conflicts', icon='today').classes('w-full max-w-xl') as expansion:
                section_grid = ui.grid(columns=2).classes('w-full gap-2 p-4')
                with section_grid:
                    ui.label('Course 1 Sections').classes('font-bold text-black')
                    ui.label('Course 2 Sections').classes('font-bold text-black')

            async def on_expand():
                if sections_loaded['done']:
                    return
                scheduler_status.set_text('⏳ Running scheduler to load sections...')
                scheduler_status.update()
                await asyncio.sleep(0.5)
                try:
                    section_map = controller.gui_get_section_map(scheduler_model)
                    with section_grid:
                        for c1, c2 in existing_conflicts:
                            sections1 = ', '.join(sorted(section_map.get(c1, {c1})))
                            sections2 = ', '.join(sorted(section_map.get(c2, {c2})))
                            ui.label(sections1).classes('text-black')
                            ui.label(sections2).classes('text-black')
                    scheduler_status.set_text('Sections loaded successfully!')
                    scheduler_status.classes(replace='text-sm')
                    sections_loaded['done'] = True
                except Exception as e:
                    scheduler_status.set_text(f'⚠️ Could not load sections: {e}')
            
            expansion.on('click', on_expand)

            ui.label('Enter section IDs to delete a conflict (e.g. CMSC 140.01):').classes('text-lg text-black')
            course_id_1 = ui.input('First Section ID').props('rounded outlined').classes('w-80')
            course_id_2 = ui.input('Conflicting Section ID').props('rounded outlined').classes('w-80')

            feedback = ui.label('').classes('text-lg')

            confirm_card = ui.card().classes('w-full max-w-xl items-center')
            confirm_card.set_visibility(False)

            with confirm_card:
                confirm_label = ui.label('').classes('text-xl text-black text-center')
                with ui.row().classes('gap-4 justify-center mt-2'):

                    def on_confirm():
                        s1 = course_id_1.value.strip()
                        s2 = course_id_2.value.strip()
                        success, message = controller.gui_delete_conflict(s1, s2)
                        feedback.set_text(message)
                        feedback.classes(replace=f'text-lg {"text-green-600" if success else "text-red-600"}')
                        confirm_card.set_visibility(False)

                    def on_cancel():
                        feedback.set_text("Conflict deletion cancelled.")
                        feedback.classes(replace='text-lg text-black')
                        confirm_card.set_visibility(False)

                    ui.button('Confirm Delete').props('rounded color=red text-color=white no-caps').classes('w-48 h-12 text-lg').on('click', on_confirm)
                    ui.button('Cancel').props('rounded color=black text-color=white no-caps').classes('w-48 h-12 text-lg').on('click', on_cancel)

            def on_validate():
                s1 = course_id_1.value.strip()
                s2 = course_id_2.value.strip()
                valid, error = controller.gui_validate_delete(s1, s2)
                if not valid:
                    feedback.set_text(error)
                    feedback.classes(replace='text-lg text-red-600')
                    confirm_card.set_visibility(False)
                    return
                confirm_label.set_text(f"Delete conflict between '{s1}' and '{s2}'?")
                feedback.set_text('')
                confirm_card.set_visibility(True)

            ui.button('Check Conflict').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', on_validate)
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict'))

    @ui.page('/conflict/view')
    @staticmethod
    def conflict_view():
        """
        Displays the GUI for viewing a conflict.
                
        Parameters:
            None        
        Returns:        
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict'))
