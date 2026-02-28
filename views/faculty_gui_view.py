# views/faculty_gui_view.py
"""
FacultyGUIView - Graphical-user interface for faculty interactions

This view class handles all files for the GUI that are related to faculty.
"""
from nicegui import ui
from views.gui_theme import GUITheme

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

            ui.button('Add Faculty').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/add'))
            ui.button('Modify Faculty').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/modify'))
            ui.button('Delete Faculty').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/delete'))
            ui.button('View Faculty').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

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
        ui.query('body').style('background-color: var(--q-add)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))

    @ui.page('/faculty/modify')
    @staticmethod
    def faculty_modify():
        """
        Displays the GUI for modifying faculty.

        User first selects a faculty member from a dropdown, then sees
        all of their current information with structured button-based
        controls for making changes.

        Parameters:
            None
        Returns:
            None
        """
        from views.gui_view import GUIView

        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')

        controller = GUIView.controller.faculty_controller
        all_faculty = controller.model.get_all_faculty()

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans gap-6'):
            # Home button at top
            with ui.row().classes('w-full max-w-2xl justify-start'):
                ui.button('Home').props('rounded color=black text-color=white no-caps').classes('h-10').on('click', lambda: ui.navigate.to('/'))

            ui.label('Modify Faculty').classes('text-4xl mb-4 text-black')

            if not all_faculty:
                ui.label('There are no faculty in the configuration.').classes('text-xl text-black')
                ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))
                return

            faculty_options = {f.name: f for f in all_faculty}
            selected_faculty = {'value': None}
            form_card = ui.card().classes('w-full max-w-2xl')
            form_card.set_visibility(False)

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
                    feedback_label.set_text(f"Updated successfully.")
                    feedback_label.classes(replace='text-md text-green-600')
                    reload_form()
                else:
                    feedback_label.set_text(f"Failed to update.")
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
                                def set_fulltime():
                                    name = selected_faculty['value'].name
                                    controller.model.modify_faculty(name, 'unique_course_limit', 2)
                                    if selected_faculty['value'].maximum_credits <= 4:
                                        controller.model.modify_faculty(name, 'maximum_credits', 12)
                                    position_feedback.set_text("Position set to Full-time.")
                                    position_feedback.classes(replace='text-md text-green-600')
                                    reload_form()

                                def set_adjunct():
                                    name = selected_faculty['value'].name
                                    controller.model.modify_faculty(name, 'unique_course_limit', 1)
                                    if selected_faculty['value'].maximum_credits > 4:
                                        if selected_faculty['value'].minimum_credits > 4:
                                            controller.model.modify_faculty(name, 'minimum_credits', 4)
                                        controller.model.modify_faculty(name, 'maximum_credits', 4)
                                    position_feedback.set_text("Position set to Adjunct.")
                                    position_feedback.classes(replace='text-md text-green-600')
                                    reload_form()

                                ui.button('Set Full-time').props('rounded color=black text-color=white no-caps').on('click', set_fulltime)
                                ui.button('Set Adjunct').props('rounded color=black text-color=white no-caps').on('click', set_adjunct)

                        ui.separator()

                        # --- Maximum Credits ---
                        with ui.column().classes('w-full gap-2'):
                            ui.label('Maximum Credits').classes('text-black font-bold text-lg')
                            ui.label(f"Current: {f.maximum_credits}").classes('text-black')
                            max_credits_feedback = ui.label('').classes('text-md text-black')
                            with ui.row().classes('gap-4 items-center'):
                                max_credits_input = ui.number(min=0, max=20, value=f.maximum_credits).classes('w-32')

                                def save_max_credits():
                                    name = selected_faculty['value'].name
                                    new_max = int(max_credits_input.value)
                                    if selected_faculty['value'].minimum_credits > new_max:
                                        controller.model.modify_faculty(name, 'minimum_credits', new_max)
                                    controller.model.modify_faculty(name, 'maximum_credits', new_max)
                                    if new_max <= 4:
                                        controller.model.modify_faculty(name, 'unique_course_limit', 1)
                                    else:
                                        if selected_faculty['value'].unique_course_limit < 2:
                                            controller.model.modify_faculty(name, 'unique_course_limit', 2)
                                    max_credits_feedback.set_text("Maximum credits updated.")
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

            def on_select(e):
                if not e.value or e.value not in faculty_options:
                    form_card.set_visibility(False)
                    return
                f = faculty_options[e.value]
                selected_faculty['value'] = f
                form_card.clear()
                form_card.set_visibility(True)
                build_form(f)

            ui.select(
                options=list(faculty_options.keys()),
                label='Select Faculty Member',
                on_change=on_select
            ).classes('w-full max-w-2xl text-xl')

            form_card
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl mt-4').on('click', lambda: ui.navigate.to('/faculty'))
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
        ui.query('body').style('background-color: var(--q-delete)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))

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
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))