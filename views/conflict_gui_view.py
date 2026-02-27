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
        """
        Displays the GUI for deleting a conflict.
        
        By default, displays conflicts as section pairs (e.g. CMSC 140.01 ↔ CMSC 161.01)
        and deletes only that specific section pair's conflict.
        When the 'Sort course conflicts without section preference' toggle is enabled,
        conflicts are collapsed to base course pairs (e.g. CMSC 140 ↔ CMSC 161)
        and deleting will remove that conflict across all sections.

        Parameters:
            None        
        Returns:        
            None
        """
        from views.gui_view import GUIView

        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-delete)')

        controller = GUIView.controller.conflict_controller
        course_model = GUIView.controller.course_model

        courses_with_sections = course_model.get_courses_with_sections()
        section_label_map = {i: label for label, i, _ in courses_with_sections}

        existing_conflicts = controller.gui_get_all_conflicts()

        def build_section_options():
            return controller.gui_get_conflict_labels(existing_conflicts, section_label_map)

        def build_base_options():
            seen = set()
            result = {}
            for c1, c2, i1, i2 in existing_conflicts:
                key = tuple(sorted([c1, c2]))
                if key not in seen:
                    seen.add(key)
                    label = f"{key[0]}  ↔  {key[1]}"
                    result[label] = (key[0], key[1], None, None)
            return result

        conflict_options = build_section_options()

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans gap-6'):
            ui.label('Delete Conflict').classes('text-4xl mb-4 text-black')
            ui.label('Select a conflict depicted by course sections or toggle the menu option down below to ignore sections and remove all conflicts associated with two courses.').classes('text-lg text-black text-center max-w-xl')

            if not existing_conflicts:
                ui.label('There are no conflicts currently in the configuration.').classes('text-xl text-black')
                ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict'))
                return

            feedback = ui.label('').classes('text-lg')
            selected = {'value': None}

            select = ui.select(
                options=list(conflict_options.keys()),
                label='Select Conflict to Delete',
                on_change=lambda e: selected.update({'value': conflict_options.get(e.value)})
            ).classes('w-full max-w-xl text-xl')

            def on_toggle(e):
                selected['value'] = None
                select.value = None
                conflict_options.clear()
                if e.value:
                    conflict_options.update(build_base_options())
                else:
                    conflict_options.update(build_section_options())
                select.options = list(conflict_options.keys())
                select.update()
                feedback.set_text('')

            ui.switch(
                'Sort course conflicts without section preference',
                on_change=on_toggle
            ).classes('text-black')

            confirm_card = ui.card().classes('w-full max-w-xl items-center bg-transparent shadow-none')
            confirm_card.set_visibility(False)

            with confirm_card:
                confirm_label = ui.label('').classes('text-xl text-black text-center')
                with ui.row().classes('gap-4 justify-center mt-2'):

                    def on_confirm():
                        if not selected['value']:
                            return
                        c1, c2, i1, i2 = selected['value']
                        label = select.value
                        s1 = section_label_map.get(i1, c1) if i1 is not None else c1
                        s2 = section_label_map.get(i2, c2) if i2 is not None else c2
                        success, message = controller.gui_delete_conflict(s1, s2, i1, i2)
                        feedback.set_text(message)
                        feedback.classes(replace=f'text-lg {"text-black-600" if success else "text-red-600"}')
                        confirm_card.set_visibility(False)
                        if success:
                            existing_conflicts.clear()
                            existing_conflicts.extend(controller.gui_get_all_conflicts())
                            new_options = build_base_options() if i1 is None else build_section_options()
                            conflict_options.clear()
                            conflict_options.update(new_options)
                            select.options = list(new_options.keys())
                            select.value = None
                            select.update()
                            selected['value'] = None

                    def on_cancel():
                        feedback.set_text('Conflict deletion cancelled.')
                        feedback.classes(replace='text-lg text-black')
                        confirm_card.set_visibility(False)

                    ui.button('Confirm Delete').props('rounded color=red text-color=white no-caps').classes('w-48 h-12 text-lg').on('click', on_confirm)
                    ui.button('Cancel').props('rounded color=black text-color=white no-caps').classes('w-48 h-12 text-lg').on('click', on_cancel)

            def on_validate():
                if not selected['value']:
                    feedback.set_text('Please select a conflict to delete.')
                    feedback.classes(replace='text-lg text-red-600')
                    confirm_card.set_visibility(False)
                    return
                c1, c2, i1, i2 = selected['value']
                valid, error = controller.gui_validate_delete(i1, i2, existing_conflicts) if i1 is not None else (True, '')
                if not valid:
                    feedback.set_text(error)
                    feedback.classes(replace='text-lg text-red-600')
                    confirm_card.set_visibility(False)
                    return
                confirm_label.set_text(f"Delete conflict: {select.value}?")
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