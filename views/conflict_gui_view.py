# views/conflict_gui_view.py
"""
ConflictGUIView - Graphical-user interface for conflict interactions

This view class handles all GUI pages related to conflict management:
- /conflict        : Conflict hub with navigation buttons
- /conflict/add    : Add a conflict between two courses
- /conflict/modify : Modify an existing conflict
- /conflict/delete : Delete a conflict
- /conflict/view   : View all conflicts
"""
import asyncio
from nicegui import ui
from views.gui_theme import GUITheme
from views.gui_utils import require_config


class ConflictGUIView:
    conflict_model = None
    conflict_controller = None

    @ui.page('/conflict')
    @staticmethod
    def conflict():
        GUITheme.applyTheming()
        if not require_config(back_url='/'):
            return
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            ui.label('Conflict').classes('text-4xl mb-10 !text-black dark:!text-white')
            ui.button('Add Conflict').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-conflictBegin), var(--q-conflictEnd)) !important;').on('click', lambda: ui.navigate.to('/conflict/add'))
            ui.button('Modify Conflict').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-conflictBegin), var(--q-conflictEnd)) !important;').on('click', lambda: ui.navigate.to('/conflict/modify'))
            ui.button('Delete Conflict').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-conflictBegin), var(--q-conflictEnd)) !important;').on('click', lambda: ui.navigate.to('/conflict/delete'))
            ui.button('View Conflict').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-conflictBegin), var(--q-conflictEnd)) !important;').on('click', lambda: ui.navigate.to('/conflict/view'))
            ui.space()
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/conflict/add')
    @staticmethod
    def conflict_add():
        GUITheme.applyTheming()
        if not require_config(back_url='/conflict'):
            return
        from views.gui_view import GUIView
        ui.query('body').style('background-color: var(--q-add)').classes('dark:!bg-black')

        model = ConflictGUIView.conflict_model

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-4'):
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))
            ui.label('Add Conflict').classes('text-4xl mb-6 !text-black dark:!text-white')

            all_courses = model.config_model.get_all_courses() if model else []
            if not all_courses:
                ui.label('No courses available.').classes('!text-black dark:!text-white')
                ui.button('Back').props('rounded color=black text-color=white no-caps').classes('dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/conflict'))
                return

            course_map = {}
            course_counts = {}
            for c in all_courses:
                cid = c.course_id
                course_counts[cid] = course_counts.get(cid, 0) + 1
                label = f"{cid}.{course_counts[cid]:02d}"
                course_map[label] = c
            labels = list(course_map.keys())

            course_a = ui.select(labels, label='Course A', value=labels[0]).props('label-color=grey-7').classes('w-full max-w-md')
            course_b = ui.select(labels, label='Course B', value=labels[1] if len(labels) > 1 else labels[0]).props('label-color=grey-7').classes('w-full max-w-md')

            status = ui.label('').classes('text-sm !text-black dark:!text-white')

            def section_conflict_exists(label_a, label_b):
                obj_a = course_map[label_a]
                obj_b = course_map[label_b]
                return (obj_b.course_id in obj_a.conflicts or obj_a.course_id in obj_b.conflicts)

            def preview():
                label_a = course_a.value
                label_b = course_b.value
                if not label_a or not label_b:
                    return
                course_id_a = course_map[label_a].course_id
                course_id_b = course_map[label_b].course_id
                if label_a == label_b or course_id_a == course_id_b:
                    status.set_text('⚠ Cannot conflict a course with itself.')
                    return
                if section_conflict_exists(label_a, label_b):
                    status.set_text(f'⚠ Conflict already exists between {label_a} and {label_b}.')
                else:
                    status.set_text(f'✓ No conflict exists between {label_a} and {label_b}.')

            preview()
            course_a.on('update:model-value', lambda _: preview())
            course_b.on('update:model-value', lambda _: preview())

            def do_add():
                label_a = course_a.value
                label_b = course_b.value
                course_id_a = course_map[label_a].course_id
                course_id_b = course_map[label_b].course_id
                if label_a == label_b or course_id_a == course_id_b:
                    status.set_text('⚠ Cannot conflict a course with itself.')
                    return
                if section_conflict_exists(label_a, label_b):
                    status.set_text(f'⚠ Conflict already exists between {label_a} and {label_b}.')
                    return
                try:
                    ok = model.add_conflict(course_id_a, course_id_b)
                    if ok:
                        fresh_courses = model.config_model.get_all_courses()
                        fresh_counts: dict[str, int] = {}
                        for c in fresh_courses:
                            cid = c.course_id
                            fresh_counts[cid] = fresh_counts.get(cid, 0) + 1
                            fresh_label = f"{cid}.{fresh_counts[cid]:02d}"
                            if fresh_label in course_map:
                                course_map[fresh_label] = c
                        preview()
                        status.set_text(f'✓ Conflict added between {label_a} and {label_b}.')
                    else:
                        status.set_text('⚠ Failed to add conflict.')
                except Exception as e:
                    status.set_text(f'Error: {e}')

            ui.button('Add Conflict').props('rounded color=black text-color=white no-caps').classes('w-80 h-12 dark:!bg-white dark:!text-black').on('click', do_add)
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl mt-4 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/conflict'))

    @ui.page('/conflict/modify')
    @staticmethod
    def conflict_modify():
        from views.gui_view import GUIView

        GUITheme.applyTheming()
        if not require_config(back_url='/conflict'):
            return

        controller = GUIView.controller.conflict_controller
        course_model = GUIView.controller.course_model
        config_model = GUIView.controller.config_model

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

        all_courses = config_model.get_all_courses()
        course_map = {}
        course_counts = {}
        for c in all_courses:
            cid = c.course_id
            course_counts[cid] = course_counts.get(cid, 0) + 1
            label = f"{cid}.{course_counts[cid]:02d}"
            course_map[label] = c
        all_section_labels = list(course_map.keys())
        all_base_labels = sorted({c.course_id for c in all_courses})

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans gap-6'):
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded no-caps').classes('h-10 !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))

            ui.label('Modify Conflict').classes('text-4xl mb-4 !text-black dark:!text-white')
            ui.label('Select an existing conflict and choose the new classes you want to conflict.').classes('text-lg !text-black dark:!text-white text-center max-w-xl')

            if not existing_conflicts:
                ui.label('There are no conflicts currently in the configuration.').classes('text-xl !text-black dark:!text-white')
                ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/conflict'))
                return

            feedback = ui.label('').classes('text-lg')
            selected = {'value': None, 'is_base': False}

            def update_selection(e):
                val = conflict_options.get(e.value)
                if val:
                    selected['value'] = val
                    c1, c2, i1, i2 = val
                    s1 = section_label_map.get(i1, c1) if i1 is not None else c1
                    s2 = section_label_map.get(i2, c2) if i2 is not None else c2
                    current_labels = new_course_a.options
                    match_a = s1 if s1 in current_labels else next((l for l in current_labels if l == c1 or l.startswith(c1 + '.')), None)
                    match_b = s2 if s2 in current_labels else next((l for l in current_labels if l == c2 or l.startswith(c2 + '.')), None)
                    new_course_a.value = match_a
                    new_course_b.value = match_b

            select_existing = ui.select(
                options=list(conflict_options.keys()),
                label='Select Conflict to Modify',
                on_change=update_selection
            ).props('label-color=grey-7').classes('w-full max-w-xl text-xl')

            with ui.row().classes('gap-4 w-full max-w-xl justify-center items-center mt-2'):
                new_course_a = ui.select(all_section_labels, label='New Course A').props('label-color=grey-7').classes('w-64 max-w-xs')
                new_course_b = ui.select(all_section_labels, label='New Course B').props('label-color=grey-7').classes('w-64 max-w-xs')

            def on_toggle(e):
                selected['value'] = None
                selected['is_base'] = e.value
                select_existing.value = None
                new_course_a.value = None
                new_course_b.value = None
                conflict_options.clear()
                if e.value:
                    conflict_options.update(build_base_options())
                    new_course_a.options = all_base_labels
                    new_course_b.options = all_base_labels
                else:
                    conflict_options.update(build_section_options())
                    new_course_a.options = all_section_labels
                    new_course_b.options = all_section_labels
                select_existing.options = list(conflict_options.keys())
                select_existing.update()
                new_course_a.update()
                new_course_b.update()
                feedback.set_text('')

            ui.switch('Sort course conflicts without section preference', on_change=on_toggle).classes('!text-black dark:!text-white')

            def on_modify():
                if not selected['value']:
                    feedback.set_text('Please select a conflict to modify.')
                    feedback.classes(replace='text-lg text-red-600')
                    return
                c1, c2, i1, i2 = selected['value']
                old_c1 = section_label_map.get(i1, c1) if i1 is not None else c1
                old_c2 = section_label_map.get(i2, c2) if i2 is not None else c2
                new_c1 = new_course_a.value
                new_c2 = new_course_b.value
                if not new_c1 or not new_c2:
                    feedback.set_text('Please select both new courses.')
                    feedback.classes(replace='text-lg text-red-600')
                    return
                success, message = controller.gui_modify_conflict(old_c1, old_c2, new_c1, new_c2, i1=i1, i2=i2)
                feedback.set_text(message)
                feedback.classes(replace=f'text-lg {"!text-black dark:!text-white" if success else "text-red-600"}')
                if success:
                    existing_conflicts.clear()
                    existing_conflicts.extend(controller.gui_get_all_conflicts())
                    new_options = build_base_options() if selected['is_base'] else build_section_options()
                    conflict_options.clear()
                    conflict_options.update(new_options)
                    select_existing.options = list(new_options.keys())
                    select_existing.value = None
                    select_existing.update()
                    selected['value'] = None
                    new_course_a.value = None
                    new_course_b.value = None

            ui.button('Modify Conflict').props('rounded no-caps').classes('w-80 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', on_modify)
            ui.button('Back').props('rounded no-caps').classes('w-80 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/conflict'))

    @ui.page('/conflict/delete')
    @staticmethod
    def conflict_delete():
        from views.gui_view import GUIView

        GUITheme.applyTheming()
        if not require_config(back_url='/conflict'):
            return
        ui.query('body').style('background-color: var(--q-delete)').classes('dark:!bg-black')

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
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))

            ui.label('Delete Conflict').classes('text-4xl mb-4 !text-black dark:!text-white')
            ui.label('Select a conflict depicted by course sections or toggle the menu option down below to ignore sections and remove all conflicts associated with two courses. You must check the conflict first to delete it.').classes('text-lg !text-black dark:!text-white text-center max-w-xl')

            if not existing_conflicts:
                ui.label('There are no conflicts currently in the configuration.').classes('text-xl !text-black dark:!text-white')
                ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/conflict'))
                return

            feedback = ui.label('').classes('text-lg')
            selected = {'value': None}

            select = ui.select(
                options=list(conflict_options.keys()),
                label='Select Conflict to Delete',
                on_change=lambda e: selected.update({'value': conflict_options.get(e.value)})
            ).props('label-color=grey-7').classes('w-full max-w-xl text-xl')

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

            ui.switch('Sort course conflicts without section preference', on_change=on_toggle).classes('!text-black dark:!text-white')

            confirm_card = ui.card().classes('w-full max-w-xl items-center bg-transparent shadow-none')
            confirm_card.set_visibility(False)

            with confirm_card:
                confirm_label = ui.label('').classes('text-xl !text-black dark:!text-white text-center')
                with ui.row().classes('gap-4 justify-center mt-2'):

                    def on_confirm():
                        if not selected['value']:
                            return
                        c1, c2, i1, i2 = selected['value']
                        s1 = section_label_map.get(i1, c1) if i1 is not None else c1
                        s2 = section_label_map.get(i2, c2) if i2 is not None else c2
                        success, message = controller.gui_delete_conflict(s1, s2, i1, i2)
                        feedback.set_text(message)
                        feedback.classes(replace=f'text-lg {"!text-black dark:!text-white" if success else "text-red-600"}')
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
                        feedback.classes(replace='text-lg !text-black dark:!text-white')
                        confirm_card.set_visibility(False)

                    ui.button('Confirm Delete').props('rounded color=red text-color=white no-caps').classes('w-48 h-12 text-lg').on('click', on_confirm)
                    ui.button('Cancel').props('rounded color=black text-color=white no-caps').classes('w-48 h-12 text-lg dark:!bg-white dark:!text-black').on('click', on_cancel)

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

            ui.button('Check Conflict').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', on_validate)
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/conflict'))

    @ui.page('/conflict/view')
    @staticmethod
    def conflict_view():
        GUITheme.applyTheming()
        if not require_config(back_url='/conflict'):
            return
        from views.gui_view import GUIView
        ui.query('body').style('background-color: var(--q-primary)').classes('dark:!bg-black')
        model = ConflictGUIView.conflict_model

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-4'):
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))
            ui.label('View Conflicts').classes('text-4xl mb-6 !text-black dark:!text-white')

            all_courses = model.config_model.get_all_courses() if model else []
            if not all_courses:
                ui.label('No courses available.')
                return

            course_label_map = {}
            course_counts = {}
            for c in all_courses:
                cid = c.course_id
                course_counts[cid] = course_counts.get(cid, 0) + 1
                course_label_map[id(c)] = f"{cid}.{course_counts[cid]:02d}"

            course_id_to_labels: dict[str, list[str]] = {}
            for c in all_courses:
                lbl = course_label_map[id(c)]
                course_id_to_labels.setdefault(c.course_id, []).append(lbl)

            groups: dict = {}
            for course in all_courses:
                if not course.conflicts:
                    continue
                key = frozenset(course.conflicts)
                if key not in groups:
                    resolved_conflicts = []
                    for conflict_id in sorted(course.conflicts):
                        section_labels = course_id_to_labels.get(conflict_id, [conflict_id])
                        resolved_conflicts.append(', '.join(section_labels))
                    groups[key] = {'labels': [], 'conflicts': resolved_conflicts}
                groups[key]['labels'].append(course_label_map[id(course)])

            if not groups:
                ui.label('No conflicts defined.').classes('text-gray-600')
            else:
                with ui.column().classes('w-full max-w-2xl gap-3'):
                    for key, group in groups.items():
                        with ui.card().classes('w-full px-5 py-4 !bg-white dark:!bg-white'):
                            ui.label(', '.join(group['labels'])).classes('font-semibold text-base !text-black')
                            ui.label('conflicts with:').classes('text-xs text-gray-500')
                            for conflict_display in group['conflicts']:
                                with ui.row().classes('items-center gap-2 ml-2'):
                                    ui.label('↔').classes('text-gray-500 text-xs')
                                    ui.label(conflict_display).classes('text-sm !text-black')

            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl mt-4 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/conflict'))