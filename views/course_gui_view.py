# views/course_gui_view.py
"""
CourseGUIView - Graphical-user interface for course interactions

This view class handles all GUI pages related to course management:
- /course        : Course hub with navigation buttons
- /course/add    : Add a new course (Under Construction)
- /course/modify : Modify an existing course
- /course/delete : Delete a course (Under Construction)
- /course/view   : View all courses
"""

from nicegui import ui
from views.gui_theme import GUITheme


class CourseGUIView:
    # Injected by main.py before ui.run()
    course_model      = None
    course_controller = None

    @ui.page('/course')
    @staticmethod
    def course():
        """
        Displays the Course hub page with navigation buttons.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            ui.label('Course').classes('text-4xl mb-10 !text-black dark:!text-white')

            ui.button('Add Course').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-courseBegin), var(--q-courseEnd)) !important;').on('click', lambda: ui.navigate.to('/course/add'))
            ui.button('Modify Course').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-courseBegin), var(--q-courseEnd)) !important;').on('click', lambda: ui.navigate.to('/course/modify'))
            ui.button('Delete Course').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-courseBegin), var(--q-courseEnd)) !important;').on('click', lambda: ui.navigate.to('/course/delete'))
            ui.button('View Course').props('rounded text-color=white no-caps').classes('w-80 h-16 text-xl').style('background: linear-gradient(135deg, var(--q-courseBegin), var(--q-courseEnd)) !important;').on('click', lambda: ui.navigate.to('/course/view'))
            ui.space()
            ui.button('Back').props('rounded color=backbtn text-color=white no-caps').classes('w-80 h-16 text-xl transition-colors duration-300 hover:!bg-[var(--q-backHover)]').on('click', lambda: ui.navigate.to('/'))

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
        ui.query('body').style('background-color: var(--q-add)').classes('dark:!bg-black')

        from views.gui_view import GUIView

        controller = GUIView.controller.course_controller
        config_model = GUIView.controller.config_model
        resources = controller.get_available_resources()

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans gap-6'):
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))
            ui.label('Add Course').classes('text-4xl mb-4 !text-black dark:!text-white')
            ui.label('To add a course enter at least a course ID and credits. When adding duplicate courses, multiple sections will be created.').classes('text-base !text-black dark:!text-white text-center max-w-xl mb-2')

            selected = {'dirty': False}

            @ui.refreshable
            def course_table():
                sections = controller.get_courses_with_sections()
                if not sections:
                    ui.label('No courses currently in configuration.').classes('text-gray-500 italic')
                    return
                with ui.scroll_area().classes('w-72 h-96 border rounded'):
                    with ui.column().classes('w-full gap-2'):
                        for label, _, course in sections:
                            with ui.expansion(label, icon='menu_book').classes('w-full'):
                                with ui.element('div').classes('grid grid-cols-2 gap-x-6 gap-y-1 text-sm pt-1 pb-1'):
                                    for lbl, val in [
                                        ('Credits', str(course.credits)),
                                        ('Rooms',   ', '.join(course.room    or []) or '—'),
                                        ('Labs',    ', '.join(course.lab     or []) or '—'),
                                        ('Faculty', ', '.join(course.faculty or []) or '—'),
                                    ]:
                                        ui.label(lbl).classes('text-gray-500 font-medium')
                                        ui.label(val)

            def handle_add():
                try:
                    course_id = course_id_input.value.strip() if course_id_input.value else ''
                    if not course_id:
                        result_label.set_text('Course ID is required.')
                        return

                    try:
                        credits = int(credits_input.value)
                    except (ValueError, TypeError):
                        result_label.set_text('Credits must be a valid number.')
                        return

                    data = {
                        'course_id': course_id,
                        'credits': credits,
                        'room': room_select.value or [],
                        'lab': lab_select.value or [],
                        'faculty': faculty_select.value or [],
                        'conflicts': []
                    }

                    success, message = controller.add_course(data)
                    result_label.set_text(message)

                    if success:
                        selected['dirty'] = True
                        save_label.set_text('You have unsaved changes. Click Save to Config to persist.')
                        save_label.classes(replace='text-lg text-orange-500')
                        config_model.save_feature('temp', 'courses')
                        course_id_input.set_value('')
                        credits_input.set_value(4)
                        room_select.set_value([])
                        lab_select.set_value([])
                        faculty_select.set_value([])
                        course_table.refresh()

                except Exception as e:
                    result_label.set_text(f'Error: {e}')

            def handle_save():
                success = config_model.save_feature('config', 'courses')
                if success:
                    selected['dirty'] = False
                    save_label.set_text('Configuration saved successfully.')
                    save_label.classes(replace='text-lg text-green-600')
                else:
                    save_label.set_text('Save failed. Check terminal for details.')
                    save_label.classes(replace='text-lg text-red-600')

            with ui.row().classes('justify-center items-start w-full gap-[150px]'):
                with ui.column().classes('items-center gap-4 pt-10'):
                    course_id_input = ui.input(label='Course ID (e.g. CMSC 161)').props('rounded outlined label-color=grey-7').classes('w-80')
                    credits_input = ui.number(label='Credits ', min=0, value=4).props('rounded outlined label-color=grey-7').classes('w-80')
                    room_select = ui.select(resources['rooms'], label='Rooms', multiple=True).props('rounded outlined label-color=grey-7').classes('w-80')
                    lab_select = ui.select(resources['labs'], label='Labs', multiple=True).props('rounded outlined label-color=grey-7').classes('w-80')
                    faculty_select = ui.select(resources['faculty'], label='Faculty', multiple=True).props('rounded outlined label-color=grey-7').classes('w-80')
                    result_label = ui.label('').classes('text-base')
                    save_label = ui.label('').classes('text-lg')
                    ui.button('Add Course').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', handle_add)
                    ui.button('Save to Config').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', handle_save)
                    ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/course'))

                with ui.column().classes('items-center gap-2'):
                    ui.label('Current Courses').classes('text-2xl !text-black dark:!text-white text-center')
                    course_table()

    @ui.page('/course/modify')
    @staticmethod
    def course_modify():
        """
        Displays the GUI for modifying an existing course.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)').classes('dark:!bg-black')
        from views.gui_view import GUIView
        model      = CourseGUIView.course_model
        controller = CourseGUIView.course_controller
        resources  = GUIView.controller.course_controller.get_available_resources()

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-4'):
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))
            ui.label('Modify Course').classes('text-4xl mb-6 !text-black dark:!text-white')

            sections = model.get_courses_with_sections() if model else []
            if not sections:
                ui.label('No courses on file.').classes('text-gray-600')
                ui.button('Back').props('rounded color=black text-color=white no-caps') \
                    .classes('w-80 h-16 text-xl mt-4 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/course'))
                return

            section_map = {label: (idx, course) for label, idx, course in sections}
            section_labels = [label for label, _, _ in sections]
            status = ui.label('').classes('text-sm !text-black dark:!text-white')
            save_label = ui.label('').classes('text-lg')

            with ui.card().classes('w-full max-w-lg p-6 gap-4'):
                selected_label = ui.select(section_labels, label='Section to Modify',
                                           value=section_labels[0]).props('label-color=grey-7').classes('w-full')

                info = ui.label('').classes('text-xs text-gray-500')

                def refresh_info():
                    entry = section_map.get(selected_label.value)
                    if entry:
                        _, course = entry
                        info.set_text(
                            f"Credits: {course.credits}  |  "
                            f"Rooms: {', '.join(course.room or [])}  |  "
                            f"Labs: {', '.join(course.lab or [])}  |  "
                            f"Faculty: {', '.join(course.faculty or [])}"
                        )

                refresh_info()
                selected_label.on('update:model-value', lambda _: refresh_info())

                ui.label(
                    'Leave blank/unselected to keep unchanged.  '
                    'Faculty: Name to add, -Name to remove.'
                ).classes('text-xs text-gray-400')

                credits_input = ui.number('New Credits', min=0, max=20).props('label-color=grey-7').classes('w-full')
                rooms_input   = ui.select(resources['rooms'], label='Rooms').props('label-color=grey-7').classes('w-full')
                labs_input    = ui.select(resources['labs'], label='Labs').props('label-color=grey-7').classes('w-full')
                faculty_input = ui.input('Faculty (add: Name, remove: -Name)').props('label-color=grey-7').classes('w-full')

                def do_modify():
                    entry = section_map.get(selected_label.value)
                    if not entry:
                        status.set_text('Section not found!')
                        return
                    section_idx, course = entry
                    cid = course.course_id

                    updates = {}

                    if credits_input.value is not None:
                        try:
                            c = int(credits_input.value)
                            if not (0 <= c <= 20):
                                status.set_text('⚠ Credits must be between 0 and 20.')
                                return
                            updates['credits'] = c
                        except (ValueError, TypeError):
                            status.set_text('⚠ Credits must be a valid number.')
                            return

                    if rooms_input.value is not None:
                        updates['room'] = [rooms_input.value]

                    if labs_input.value is not None:
                        updates['lab'] = [labs_input.value]

                    raw_faculty = faculty_input.value.strip()
                    if raw_faculty:
                        modifications = {'credits': '', 'room': '', 'lab': '', 'faculty': raw_faculty}
                        parsed = controller._parse_modifications(modifications, course)
                        if parsed is None:
                            status.set_text('⚠ Invalid faculty input.')
                            return
                        if 'faculty' in parsed:
                            updates['faculty'] = parsed['faculty']

                    if not updates:
                        status.set_text('No changes entered.')
                        return

                    ok = model.modify_course(cid, **updates)
                    if ok:
                        from views.gui_view import GUIView
                        GUIView.controller.config_model.save_feature('temp', 'courses')
                        status.set_text(f"'{selected_label.value}' updated in memory.")
                        save_label.set_text('You have unsaved changes. Click Save to Config to persist.')
                        save_label.classes(replace='text-lg text-orange-500')
                        credits_input.set_value(None)
                        rooms_input.set_value([])
                        labs_input.set_value([])
                        faculty_input.value = ''
                        new_sections = model.get_courses_with_sections()
                        section_map.clear()
                        section_map.update({lbl: (i, c) for lbl, i, c in new_sections})
                        refresh_info()
                    else:
                        status.set_text(f"⚠ Failed to update '{selected_label.value}'.")

                def do_save_to_config():
                    from views.gui_view import GUIView
                    success = GUIView.controller.config_model.save_feature('config', 'courses')
                    if success:
                        save_label.set_text('Configuration saved to file.')
                        save_label.classes(replace='text-lg text-green-600')
                    else:
                        save_label.set_text('Save failed. Check terminal for details.')
                        save_label.classes(replace='text-lg text-red-600')

                ui.button('Apply Changes').props('rounded color=black text-color=white no-caps').classes('w-full h-12 mt-2 dark:!bg-white dark:!text-black').on('click', do_modify)
                ui.button('Save to Config').props('rounded color=black text-color=white no-caps').classes('w-full h-12 dark:!bg-white dark:!text-black').on('click', do_save_to_config)

            status
            save_label
            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl mt-4 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/course'))

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
        from views.gui_view import GUIView

        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-delete)').classes('dark:!bg-black')

        controller = GUIView.controller.course_controller
        config_model = GUIView.controller.config_model
        existing_courses = controller.get_courses_with_sections()

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans gap-6'):
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))

            ui.label('Delete Course').classes('text-4xl mb-4 !text-black dark:!text-white')
            ui.label('Select a course to delete from the drop down below, but remember all references to the course will be permanently gone!').classes('text-lg !text-black dark:!text-white text-center max-w-xl')

            if not existing_courses:
                ui.label('There are no courses currently in the configuration.').classes('text-xl !text-black dark:!text-white')
                ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/course'))
                return

            status_label = ui.label('').classes('text-lg !text-black dark:!text-white')
            save_label = ui.label('').classes('text-lg !text-black dark:!text-white')

            section_options = {label: (course.course_id, index) for label, index, course in existing_courses}
            selected = {'value': None, 'dirty': False}

            select = ui.select(
                options=list(section_options.keys()),
                label='Select Course Section',
                on_change=lambda e: selected.update({'value': section_options[e.value]}) if e.value in section_options else selected.update({'value': None})
            ).props('label-color=grey-7').classes('w-full max-w-xl text-xl')

            def handle_delete():
                if not selected['value']:
                    status_label.set_text('Please select a course section to delete.')
                    return

                course_id, section_index = selected['value']

                with ui.dialog() as dialog, ui.card():
                    ui.label(f"Are you sure you want to delete '{select.value}'?").classes('text-lg')
                    with ui.row():
                        ui.button('Cancel', on_click=dialog.close).props('rounded color=black text-color=white no-caps')
                        def confirm_delete():
                            dialog.close()
                            success, message = controller.delete_course(course_id, section_index)
                            status_label.set_text(message)
                            if success:
                                selected['dirty'] = True
                                save_label.set_text('You have unsaved changes. Click Save to Config to persist.')
                                save_label.classes(replace='text-lg text-orange-500')
                                config_model.save_feature('temp', 'courses')
                                updated = controller.get_courses_with_sections()
                                new_options = {label: (course.course_id, index) for label, index, course in updated}
                                section_options.clear()
                                section_options.update(new_options)
                                select.options = list(new_options.keys())
                                select.value = None
                                select.update()
                        ui.button('Delete', on_click=confirm_delete).props('rounded color=red text-color=white no-caps')

                dialog.open()

            def handle_save():
                success = config_model.save_feature('config', 'courses')
                if success:
                    selected['dirty'] = False
                    save_label.set_text('Configuration saved to file.')
                    save_label.classes(replace='text-lg text-green-600')
                else:
                    save_label.set_text('Save failed. Check terminal for details.')
                    save_label.classes(replace='text-lg text-red-600')

            ui.button('Delete Course').props('rounded color=red text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', handle_delete)
            ui.button('Save to Config').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', handle_save)
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/course'))

    @ui.page('/course/view')
    @staticmethod
    def course_view():
        """
        Displays the GUI for viewing all courses.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)').classes('dark:!bg-black')
        model = CourseGUIView.course_model

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-4'):
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))
            ui.label('View Courses').classes('text-4xl mb-6 !text-black dark:!text-white')
            with ui.column().classes('w-full max-w-lg gap-3'):
                sections = model.get_courses_with_sections() if model else []
                if not sections:
                    ui.label('No courses on file.').classes('text-gray-600')
                else:
                    for label, _, course in sections:
                        with ui.expansion(label, icon='menu_book').classes('w-full'):
                            with ui.element('div').classes('grid grid-cols-2 gap-x-8 gap-y-2 text-sm pt-2 pb-2'):
                                for lbl, val in [
                                    ('Credits',   str(course.credits)),
                                    ('Rooms',     ', '.join(course.room or []) or '—'),
                                    ('Labs',      ', '.join(course.lab or []) or '—'),
                                    ('Faculty',   ', '.join(course.faculty or []) or '—'),
                                    ('Conflicts', ', '.join(course.conflicts or []) or '—'),
                                ]:
                                    ui.label(lbl).classes('text-gray-500 font-medium')
                                    ui.label(val)
            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl mt-4 dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/course'))