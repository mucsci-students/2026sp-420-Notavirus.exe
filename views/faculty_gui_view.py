# views/faculty_gui_view.py
"""
FacultyGUIView - Graphical-user interface for faculty interactions

This view class handles all GUI pages related to faculty management:
- /faculty       : Faculty hub with navigation buttons
- /faculty/add   : Add a new faculty member (Under Construction)
- /faculty/modify: Modify an existing faculty member (Under Construction)
- /faculty/delete: Delete an existing faculty member
- /faculty/view  : View all faculty members
"""
from nicegui import ui
from views.gui_theme import GUITheme


class FacultyGUIView:
    # Injected by main.py before ui.run()
    faculty_model      = None
    faculty_controller = None

    @ui.page('/faculty')
    @staticmethod
    def faculty():
        """
        Displays the Faculty hub page with navigation buttons.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            ui.label('Faculty').classes('text-4xl mb-10 text-black')
            ui.button('Add Faculty').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/add'))
            ui.button('Modify Faculty').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/modify'))
            ui.button('Delete Faculty').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/delete'))
            ui.button('View Faculty').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl mt-4').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/faculty/add')
    @staticmethod
    def faculty_add():
        """
        Displays the GUI for adding a faculty member.

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
                .classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))

    @ui.page('/faculty/modify')
    @staticmethod
    def faculty_modify():
        """
        Displays the GUI for modifying faculty.

        User first selects a faculty member from a dropdown, then sees
        all of their current information with structured button-based
        controls for making changes. Changes are in-memory until Save
        Configuration is clicked.

        Parameters:
            None
        Returns:
            None
        """
        from views.gui_view import GUIView

        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')

        controller = GUIView.controller.faculty_controller
        config_model = GUIView.controller.config_model
        all_faculty = controller.model.get_all_faculty()

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans gap-6'):
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10').on('click', lambda: ui.navigate.to('/'))

            ui.label('Modify Faculty').classes('text-4xl mb-4 text-black')
            ui.label('Select a Faculty member to modify their information. Press the "Save Configuration" button at the bottom of the editor page to permanently save your modifications to the original configuration file.').classes('text-lg text-black text-center max-w-xl')

            if not all_faculty:
                ui.label('There are no faculty in the configuration.').classes('text-xl text-black')
                ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))
                return

            faculty_options = {f.name: f for f in all_faculty}
            selected_faculty = {'value': None}
            form_card = ui.card().classes('w-full max-w-2xl')
            form_card.set_visibility(False)
            save_config_label = ui.label('').classes('text-lg text-black')

            def reload_form():
                try:
                    updated = controller.model.get_faculty_by_name(selected_faculty['value'].name)
                    selected_faculty['value'] = updated
                    faculty_options[updated.name] = updated
                    form_card.clear()
                    build_form(updated)
                except Exception as e:
                    print(f"DEBUG reload_form exception: {e}")

            def apply(field, value, feedback_label):
                f = selected_faculty['value']
                success = controller.model.modify_faculty(f.name, field, value)
                if success:
                    feedback_label.set_text('Updated successfully.')
                    feedback_label.classes(replace='text-md text-green-600')
                    reload_form()
                else:
                    feedback_label.set_text('Failed to update.')
                    feedback_label.classes(replace='text-md text-red-600')

            def build_form(f):
                with form_card:
                    with ui.column().classes('w-full gap-6 p-6'):

                        # --- Position Type ---
                        with ui.column().classes('w-full gap-2'):
                            ui.label('Position Type').classes('text-black font-bold text-lg')
                            is_fulltime = f.unique_course_limit >= 2
                            ui.label(f"Current: {'Full-time' if is_fulltime else 'Adjunct'} | Max Credits: {f.maximum_credits} | Course Limit: {f.unique_course_limit}").classes('text-black')
                            position_feedback = ui.label(' ').classes('text-md text-black')
                            with ui.row().classes('gap-4'):
                                ui.button('Set Full-time').props('rounded color=black text-color=white no-caps').on(
                                    'click', lambda: [
                                        controller.gui_set_position(selected_faculty['value'].name, True),
                                        position_feedback.set_text('Position set to Full-time.'),
                                        position_feedback.classes(replace='text-md text-green-600'),
                                        reload_form()
                                    ]
                                )
                                ui.button('Set Adjunct').props('rounded color=black text-color=white no-caps').on(
                                    'click', lambda: [
                                        controller.gui_set_position(selected_faculty['value'].name, False),
                                        position_feedback.set_text('Position set to Adjunct.'),
                                        position_feedback.classes(replace='text-md text-green-600'),
                                        reload_form()
                                    ]
                                )

                        ui.separator()

                        # --- Maximum Credits ---
                        with ui.column().classes('w-full gap-2'):
                            ui.label('Maximum Credits').classes('text-black font-bold text-lg')
                            ui.label(f"Current: {f.maximum_credits}").classes('text-black')
                            max_credits_feedback = ui.label('').classes('text-md text-black')
                            with ui.row().classes('gap-4 items-center'):
                                max_credits_input = ui.number(min=0, max=20, value=f.maximum_credits).classes('w-32')

                                def save_max_credits():
                                    success = controller.gui_set_maximum_credits(
                                        selected_faculty['value'].name, int(max_credits_input.value)
                                    )
                                    if success:
                                        max_credits_feedback.set_text('Maximum credits updated.')
                                        max_credits_feedback.classes(replace='text-md text-green-600')
                                    reload_form()

                                ui.button('Save').props('rounded color=black text-color=white no-caps').on('click', save_max_credits)

                        ui.separator()

                        # --- Minimum Credits ---
                        with ui.column().classes('w-full gap-2'):
                            ui.label('Minimum Credits').classes('text-black font-bold text-lg')
                            ui.label(f"Current: {f.minimum_credits}").classes('text-black')
                            min_credits_feedback = ui.label('').classes('text-md text-black')
                            with ui.row().classes('gap-4 items-center'):
                                min_credits_input = ui.number(min=0, max=f.maximum_credits, value=f.minimum_credits).classes('w-32')
                                ui.button('Save').props('rounded color=black text-color=white no-caps').on(
                                    'click', lambda: apply('minimum_credits', int(min_credits_input.value), min_credits_feedback))

                        ui.separator()

                        # --- Availability Times ---
                        with ui.column().classes('w-full gap-2'):
                            ui.label('Availability Times').classes('text-black font-bold text-lg')
                            ui.label('Current:').classes('text-black')
                            for day, ranges in f.times.items():
                                if ranges:
                                    times_str = ', '.join(str(r) for r in ranges)
                                    ui.label(f"  {day}: {times_str}").classes('text-black text-sm')
                                else:
                                    ui.label(f"  {day}: unavailable").classes('text-black text-sm')

                            ui.label('Add/Update a day:').classes('text-black mt-2')
                            times_feedback = ui.label('').classes('text-md text-black')
                            with ui.row().classes('gap-4 items-center flex-wrap'):
                                day_select = ui.select(
                                    options=['MON', 'TUE', 'WED', 'THU', 'FRI'],
                                    label='Day'
                                ).classes('w-32')
                                start_input = ui.input(label='Start (HH:MM)', value='09:00').classes('w-32')
                                end_input = ui.input(label='End (HH:MM)', value='17:00').classes('w-32')

                                def save_time():
                                    from scheduler import TimeRange as TR
                                    if not day_select.value:
                                        times_feedback.set_text('Please select a day.')
                                        times_feedback.classes(replace='text-md text-red-600')
                                        return
                                    try:
                                        new_times = dict(selected_faculty['value'].times)
                                        new_times[day_select.value] = [TR(start=start_input.value.strip(), end=end_input.value.strip())]
                                        apply('times', new_times, times_feedback)
                                    except Exception as ex:
                                        times_feedback.set_text(f'Invalid time format: {ex}')
                                        times_feedback.classes(replace='text-md text-red-600')

                                ui.button('Save Time').props('rounded color=black text-color=white no-caps').on('click', save_time)

                            def clear_day():
                                if not day_select.value:
                                    times_feedback.set_text('Please select a day.')
                                    times_feedback.classes(replace='text-md text-red-600')
                                    return
                                new_times = dict(selected_faculty['value'].times)
                                new_times[day_select.value] = []
                                apply('times', new_times, times_feedback)

                            ui.button('Mark Day Unavailable').props('rounded color=grey text-color=white no-caps').on('click', clear_day)

                        ui.separator()

                        # --- Course Preferences ---
                        with ui.column().classes('w-full gap-2'):
                            ui.label('Course Preferences').classes('text-black font-bold text-lg')
                            if f.course_preferences:
                                for course, weight in f.course_preferences.items():
                                    ui.label(f"  {course}: {weight}").classes('text-black text-sm')
                            else:
                                ui.label('  None').classes('text-black text-sm')

                            ui.label('Add/Update a course preference:').classes('text-black mt-2')
                            course_pref_feedback = ui.label('').classes('text-md text-black')
                            with ui.row().classes('gap-4 items-center flex-wrap'):
                                course_input = ui.input(label='Course ID (e.g. CMSC 161)').classes('w-48')
                                weight_input = ui.number(label='Weight (0-10)', min=0, max=10, value=5).classes('w-32')

                                def save_course_pref():
                                    course = course_input.value.strip()
                                    if not course:
                                        course_pref_feedback.set_text('Please enter a course ID.')
                                        course_pref_feedback.classes(replace='text-md text-red-600')
                                        return
                                    new_prefs = dict(selected_faculty['value'].course_preferences)
                                    new_prefs[course] = int(weight_input.value)
                                    apply('course_preferences', new_prefs, course_pref_feedback)

                                ui.button('Save').props('rounded color=black text-color=white no-caps').on('click', save_course_pref)

                            if f.course_preferences:
                                ui.label('Remove a course preference:').classes('text-black mt-2')
                                with ui.row().classes('gap-4 items-center'):
                                    remove_course_select = ui.select(
                                        options=list(f.course_preferences.keys()),
                                        label='Course to Remove'
                                    ).classes('w-48')

                                    def remove_course_pref():
                                        if not remove_course_select.value:
                                            return
                                        new_prefs = dict(selected_faculty['value'].course_preferences)
                                        new_prefs.pop(remove_course_select.value, None)
                                        apply('course_preferences', new_prefs, course_pref_feedback)

                                    ui.button('Remove').props('rounded color=red text-color=white no-caps').on('click', remove_course_pref)

                        ui.separator()

                        # --- Room Preferences ---
                        with ui.column().classes('w-full gap-2'):
                            ui.label('Room Preferences').classes('text-black font-bold text-lg')
                            if f.room_preferences:
                                for room, weight in f.room_preferences.items():
                                    ui.label(f"  {room}: {weight}").classes('text-black text-sm')
                            else:
                                ui.label('  None').classes('text-black text-sm')

                            ui.label('Add/Update a room preference:').classes('text-black mt-2')
                            room_pref_feedback = ui.label('').classes('text-md text-black')
                            available_rooms = list(GUIView.controller.config_model.config.config.rooms)
                            if available_rooms:
                                with ui.row().classes('gap-4 items-center flex-wrap'):
                                    room_select = ui.select(options=available_rooms, label='Room').classes('w-48')
                                    room_weight_input = ui.number(label='Weight (0-10)', min=0, max=10, value=5).classes('w-32')

                                    def save_room_pref():
                                        if not room_select.value:
                                            room_pref_feedback.set_text('Please select a room.')
                                            room_pref_feedback.classes(replace='text-md text-red-600')
                                            return
                                        new_prefs = dict(selected_faculty['value'].room_preferences)
                                        new_prefs[room_select.value] = int(room_weight_input.value)
                                        apply('room_preferences', new_prefs, room_pref_feedback)

                                    ui.button('Save').props('rounded color=black text-color=white no-caps').on('click', save_room_pref)

                                if f.room_preferences:
                                    ui.label('Remove a room preference:').classes('text-black mt-2')
                                    with ui.row().classes('gap-4 items-center'):
                                        remove_room_select = ui.select(
                                            options=list(f.room_preferences.keys()),
                                            label='Room to Remove'
                                        ).classes('w-48')

                                        def remove_room_pref():
                                            if not remove_room_select.value:
                                                return
                                            new_prefs = dict(selected_faculty['value'].room_preferences)
                                            new_prefs.pop(remove_room_select.value, None)
                                            apply('room_preferences', new_prefs, room_pref_feedback)

                                        ui.button('Remove').props('rounded color=red text-color=white no-caps').on('click', remove_room_pref)
                            else:
                                ui.label('No rooms available in configuration.').classes('text-black text-sm')

                        ui.separator()

                        # --- Lab Preferences ---
                        with ui.column().classes('w-full gap-2'):
                            ui.label('Lab Preferences').classes('text-black font-bold text-lg')
                            if f.lab_preferences:
                                for lab, weight in f.lab_preferences.items():
                                    ui.label(f"  {lab}: {weight}").classes('text-black text-sm')
                            else:
                                ui.label('  None').classes('text-black text-sm')

                            ui.label('Add/Update a lab preference:').classes('text-black mt-2')
                            lab_pref_feedback = ui.label('').classes('text-md text-black')
                            available_labs = list(GUIView.controller.config_model.config.config.labs)
                            if available_labs:
                                with ui.row().classes('gap-4 items-center flex-wrap'):
                                    lab_select = ui.select(options=available_labs, label='Lab').classes('w-48')
                                    lab_weight_input = ui.number(label='Weight (0-10)', min=0, max=10, value=5).classes('w-32')

                                    def save_lab_pref():
                                        if not lab_select.value:
                                            lab_pref_feedback.set_text('Please select a lab.')
                                            lab_pref_feedback.classes(replace='text-md text-red-600')
                                            return
                                        new_prefs = dict(selected_faculty['value'].lab_preferences)
                                        new_prefs[lab_select.value] = int(lab_weight_input.value)
                                        apply('lab_preferences', new_prefs, lab_pref_feedback)

                                    ui.button('Save').props('rounded color=black text-color=white no-caps').on('click', save_lab_pref)

                                if f.lab_preferences:
                                    ui.label('Remove a lab preference:').classes('text-black mt-2')
                                    with ui.row().classes('gap-4 items-center'):
                                        remove_lab_select = ui.select(
                                            options=list(f.lab_preferences.keys()),
                                            label='Lab to Remove'
                                        ).classes('w-48')

                                        def remove_lab_pref():
                                            if not remove_lab_select.value:
                                                return
                                            new_prefs = dict(selected_faculty['value'].lab_preferences)
                                            new_prefs.pop(remove_lab_select.value, None)
                                            apply('lab_preferences', new_prefs, lab_pref_feedback)

                                        ui.button('Remove').props('rounded color=red text-color=white no-caps').on('click', remove_lab_pref)
                            else:
                                ui.label('No labs available in configuration.').classes('text-black text-sm')

            def on_select(e):
                if not e.value or e.value not in faculty_options:
                    form_card.set_visibility(False)
                    return
                f = faculty_options[e.value]
                selected_faculty['value'] = f
                form_card.clear()
                form_card.set_visibility(True)
                build_form(f)

            def handle_save():
                success = config_model.safe_save()
                if success:
                    save_config_label.set_text('Configuration saved successfully.')
                    save_config_label.classes(replace='text-lg text-green-600')
                else:
                    save_config_label.set_text('Save failed. Check terminal for details.')
                    save_config_label.classes(replace='text-lg text-red-600')

            ui.select(
                options=list(faculty_options.keys()),
                label='Select Faculty Member',
                on_change=on_select
            ).classes('w-full max-w-2xl text-xl')

            form_card
            save_config_label
            ui.button('Save Configuration').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl mt-4').on('click', handle_save)
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))

    @ui.page('/faculty/delete')
    @staticmethod
    def faculty_delete():
        """
        Displays the GUI for deleting a faculty member.

        Loads all faculty from FacultyModel and displays them as cards.
        Each card has a Delete button that opens a confirmation dialog
        before calling model.delete_faculty(). The list refreshes after
        each deletion.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-delete)')

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-4'):
            ui.label('Delete Faculty').classes('text-4xl mb-6 text-black')

            container = ui.column().classes('w-full max-w-lg gap-3 items-center')
            status    = ui.label('').classes('text-sm')

            def build(c):
                """Clears and rebuilds the faculty card list."""
                c.clear()
                model        = FacultyGUIView.faculty_model
                faculty_list = model.get_all_faculty() if model else []

                with c:
                    if not faculty_list:
                        ui.label('No faculty to delete.').classes('text-gray-600')
                        return

                    for faculty in faculty_list:
                        is_ft     = faculty.maximum_credits >= 12
                        tag_label = 'Full Time' if is_ft else 'Adjunct'

                        with ui.card().classes('w-full px-5 py-4'):
                            with ui.row().classes('w-full items-center justify-between'):
                                with ui.column().classes('gap-1'):
                                    ui.label(faculty.name).classes('text-base font-semibold')
                                    ui.label(
                                        f'{tag_label}  ·  Max {faculty.maximum_credits} credits  ·  '
                                        f'Limit {faculty.unique_course_limit} courses'
                                    ).classes('text-xs text-gray-500')

                                def make_handler(name, m, sl):
                                    """
                                    Returns a delete handler for the given faculty name.

                                    Parameters:
                                        name (str): Faculty name to delete
                                        m: FacultyModel instance
                                        sl: Status label to update after deletion
                                    Returns:
                                        function: Click handler that opens confirmation dialog
                                    """
                                    def _delete():
                                        with ui.dialog() as dlg, ui.card().classes('p-8 gap-4 items-center text-center'):
                                            ui.label(f"Delete '{name}'?").classes('text-xl font-bold')
                                            ui.label('This will also remove them from any course assignments.') \
                                                .classes('text-sm text-gray-500')
                                            with ui.row().classes('gap-4 mt-4'):
                                                ui.button('Cancel', on_click=dlg.close) \
                                                    .props('rounded color=black text-color=white no-caps')

                                                def confirm(d=dlg, n=name, mod=m, s=sl):
                                                    """Confirms deletion and refreshes the list."""
                                                    ok = mod.delete_faculty(n)
                                                    d.close()
                                                    s.set_text(f"✓ '{n}' deleted." if ok
                                                               else f"⚠ Could not delete '{n}'.")
                                                    build(container)

                                                ui.button('Delete', on_click=confirm) \
                                                    .props('rounded color=red text-color=white no-caps')
                                        dlg.open()
                                    return _delete

                                ui.button('Delete', on_click=make_handler(faculty.name, model, status)) \
                                    .props('flat color=red no-caps')

            build(container)
            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl mt-4').on('click', lambda: ui.navigate.to('/faculty'))

    @ui.page('/faculty/view')
    @staticmethod
    def faculty_view():
        """
        Displays the GUI for viewing all faculty members.

        Loads all faculty from FacultyModel and displays each as an
        expandable card showing position, credits, course limit, and preferences.

        Parameters:
            None
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        model = FacultyGUIView.faculty_model

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-4'):
            ui.label('View Faculty').classes('text-4xl mb-6 text-black')
            with ui.column().classes('w-full max-w-lg gap-3'):
                faculty_list = model.get_all_faculty() if model else []
                if not faculty_list:
                    ui.label('No faculty on file.').classes('text-gray-600')
                else:
                    for faculty in faculty_list:
                        is_ft = faculty.maximum_credits >= 12
                        with ui.expansion(faculty.name, icon='person').classes('w-full'):
                            with ui.element('div').classes('grid grid-cols-2 gap-x-8 gap-y-2 text-sm pt-2 pb-2'):
                                for lbl, val in [
                                    ('Position',     'Full Time' if is_ft else 'Adjunct'),
                                    ('Max Credits',  str(faculty.maximum_credits)),
                                    ('Min Credits',  str(faculty.minimum_credits)),
                                    ('Course Limit', str(faculty.unique_course_limit)),
                                    ('Max Days',     str(faculty.maximum_days)),
                                ]:
                                    ui.label(lbl).classes('text-gray-500 font-medium')
                                    ui.label(val)
                                if faculty.course_preferences:
                                    ui.label('Course Prefs').classes('text-gray-500 font-medium')
                                    ui.label(', '.join(faculty.course_preferences.keys()))
            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl mt-4').on('click', lambda: ui.navigate.to('/faculty'))