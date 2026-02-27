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
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            ui.label('Course').classes('text-4xl mb-10 text-black')
            for label, route in [
                ('Add Course',    '/course/add'),
                ('Modify Course', '/course/modify'),
                ('Delete Course', '/course/delete'),
                ('View Course',   '/course/view'),
            ]:
                ui.button(label).props('rounded color=black text-color=white no-caps') \
                    .classes('w-80 h-16 text-xl mb-2').on('click', lambda r=route: ui.navigate.to(r))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl mt-4').on('click', lambda: ui.navigate.to('/'))

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
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/course'))

    @ui.page('/course/modify')
    @staticmethod
    def course_modify():
        """
        Displays the GUI for modifying an existing course.

        Loads all course sections from CourseModel and displays a dropdown
        showing section labels (e.g. CMSC 161.01, CMSC 161.02) so individual
        sections can be targeted. Shows current values for the selected section.

        Credits: enter a number to change, blank to keep.
        Rooms/Labs: enter comma-separated values to replace, blank to keep,
                    prefix with - to remove a specific entry (e.g. -Roddy 136).
        Faculty: add by name, remove with -Name prefix.

        Calls controller._parse_modifications() then model.modify_course().

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')
        model      = CourseGUIView.course_model
        controller = CourseGUIView.course_controller

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-4'):
            ui.label('Modify Course').classes('text-4xl mb-6 text-black')

            sections = model.get_courses_with_sections() if model else []
            if not sections:
                ui.label('No courses on file.').classes('text-gray-600')
                ui.button('Back').props('rounded color=black text-color=white no-caps') \
                    .classes('w-80 h-16 text-xl mt-4').on('click', lambda: ui.navigate.to('/course'))
                return

            # Build label -> (index, course) mapping so we can look up by section label
            section_map = {label: (idx, course) for label, idx, course in sections}
            section_labels = [label for label, _, _ in sections]
            status = ui.label('').classes('text-sm')

            with ui.card().classes('w-full max-w-lg p-6 gap-4'):
                selected_label = ui.select(section_labels, label='Section to Modify',
                                           value=section_labels[0]).classes('w-full')

                # Shows current values for the selected section
                info = ui.label('').classes('text-xs text-gray-500')

                def refresh_info():
                    """Updates the info label with current values of the selected section."""
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
                    'Leave blank to keep unchanged.  '
                    'Rooms/Labs: comma-separated to replace, -Name to remove one.  '
                    'Faculty: Name to add, -Name to remove.'
                ).classes('text-xs text-gray-400')

                credits_input = ui.input('New Credits').classes('w-full')
                rooms_input   = ui.input('Rooms (e.g. Roddy 136, Roddy 140  or  -Roddy 136)').classes('w-full')
                labs_input    = ui.input('Labs (e.g. Linux  or  -Mac)').classes('w-full')
                faculty_input = ui.input('Faculty (add: Name, remove: -Name)').classes('w-full')

                def do_modify():
                    """
                    Reads inputs, parses modifications, and applies them to the
                    selected section via the model.

                    Parameters:
                        None
                    Returns:
                        None
                    """
                    entry = section_map.get(selected_label.value)
                    if not entry:
                        status.set_text('⚠ Section not found.')
                        return
                    section_idx, course = entry
                    cid = course.course_id

                    updates = {}

                    # Credits: only update if field is non-empty
                    raw_credits = credits_input.value.strip()
                    if raw_credits:
                        try:
                            c = int(raw_credits)
                            if c < 0:
                                status.set_text('⚠ Credits cannot be negative.')
                                return
                            updates['credits'] = c
                        except ValueError:
                            status.set_text(f"⚠ '{raw_credits}' is not a valid number.")
                            return

                    # Rooms: blank = keep, otherwise parse add/remove
                    raw_rooms = rooms_input.value.strip()
                    if raw_rooms:
                        changes = [r.strip() for r in raw_rooms.split(',') if r.strip()]
                        current = list(course.room or [])
                        for change in changes:
                            if change.startswith('-'):
                                name = change[1:].strip()
                                if name in current:
                                    current.remove(name)
                            else:
                                if change not in current:
                                    current.append(change)
                        updates['room'] = current

                    # Labs: blank = keep, otherwise parse add/remove
                    raw_labs = labs_input.value.strip()
                    if raw_labs:
                        changes = [l.strip() for l in raw_labs.split(',') if l.strip()]
                        current = list(course.lab or [])
                        for change in changes:
                            if change.startswith('-'):
                                name = change[1:].strip()
                                if name in current:
                                    current.remove(name)
                            else:
                                if change not in current:
                                    current.append(change)
                        updates['lab'] = current

                    # Faculty: reuse controller's existing parse logic
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
                        status.set_text('ℹ No changes entered.')
                        return

                    ok = model.modify_course(cid, **updates)
                    if ok:
                        status.set_text(f"✓ '{selected_label.value}' updated successfully.")
                        credits_input.value = rooms_input.value = labs_input.value = faculty_input.value = ''
                        # Refresh section map with updated data
                        new_sections = model.get_courses_with_sections()
                        section_map.clear()
                        section_map.update({lbl: (i, c) for lbl, i, c in new_sections})
                        refresh_info()
                    else:
                        status.set_text(f"⚠ Failed to update '{selected_label.value}'.")

                ui.button('Apply Changes', on_click=do_modify) \
                    .props('rounded color=black text-color=white no-caps').classes('w-full h-12 mt-2')

            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl mt-4').on('click', lambda: ui.navigate.to('/course'))

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
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/course'))

    @ui.page('/course/view')
    @staticmethod
    def course_view():
        """
        Displays the GUI for viewing all courses.

        Loads all course sections from CourseModel and displays each as an
        expandable card showing credits, rooms, labs, faculty, and conflicts.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        model = CourseGUIView.course_model

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-4'):
            ui.label('View Courses').classes('text-4xl mb-6 text-black')
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
                .classes('w-80 h-16 text-xl mt-4').on('click', lambda: ui.navigate.to('/course'))