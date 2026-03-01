# views/course_gui_view.py
"""
CourseGUIView - Graphical-user interface for course interactions

This view class handles all files for the GUI that are related to courses.
"""
from nicegui import ui
from views.gui_theme import GUITheme

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

            ui.button('Add Course').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/add'))
            ui.button('Modify Course').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/modify'))
            ui.button('Delete Course').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/delete'))
            ui.button('View Course').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/course/view'))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/'))

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

        from views.gui_view import GUIView

        controller = GUIView.controller.course_controller
        resources = controller.get_available_resources()

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans gap-6'):
            ui.label('Add Course').classes('text-4xl mb-4 text-black')

            course_id_input = ui.input(label='Course ID (e.g. CMSC 161)').props('rounded outlined').classes('w-80')
            credits_input = ui.input(label='Credits: ', min=0, value=4).props('rounded outlined').classes('w-80')
            room_select = ui.select(resources['rooms'], label='Rooms', multiple=True).props('rounded outlined').classes('w-80')
            lab_select = ui.select(resources ['labs'], label='Labs', multiple=True).props('rounded outlined').classes('w-80')
            faculty_select = ui.select(resources ['faculty'], label='Faculty', multiple=True).props('rounded outlined').classes('w-80')

            result_label = ui.label('').classes('text-base')

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
                        course_id_input.set_value('')
                        credits_input.set_value(4)
                        room_select.set_value([])
                        lab_select.set_value([])
                        faculty_select.set_value([])

                except Exception as e:
                    result_label.set_text(f'Error: {e}')

            ui.button('Add Course').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', handle_add)
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/course'))


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
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/course'))

    @ui.page('/course/delete')
    @staticmethod
    def course_delete():
        """
        Displays the GUI for deleting a course.

        Presents a dropdown of all course sections (e.g. CMSC 140.01, CMSC 140.02)
        derived from the current configuration. Deleting a specific section removes
        only that section from the JSON, and remaining sections are renumbered
        automatically on reload.

        Parameters:
            None
        Returns:
            None
        """
        from views.gui_view import GUIView

        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-delete)')

        controller = GUIView.controller.course_controller
        existing_courses = controller.get_courses_with_sections()

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans gap-6'):
            ui.label('Delete Course').classes('text-4xl mb-4 text-black')
            ui.label('Select a course to delete from the drop down below, but remember all references to the course will be permanently gone!').classes('text-lg text-black text-center max-w-xl')

            if not existing_courses:
                ui.label('There are no courses currently in the configuration.').classes('text-xl text-black')
                ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/course'))
                return

            status_label = ui.label('').classes('text-lg text-black')

            section_options = {label: (course.course_id, index) for label, index, course in existing_courses}
            selected = {'value': None}

            select = ui.select(
                options=list(section_options.keys()),
                label='Select Course Section',
                on_change=lambda e: selected.update({'value': section_options[e.value]}) if e.value in section_options else selected.update({'value': None})
            ).classes('w-full max-w-xl text-xl')


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
                                updated = controller.get_courses_with_sections()
                                new_options = {label: (course.course_id, index) for label, index, course in updated}
                                section_options.update(new_options)
                                select.options = list(new_options.keys())
                                select.value = None
                                select.update()
                        ui.button('Delete', on_click=confirm_delete).props('rounded color=red text-color=white no-caps')

                dialog.open()

            ui.button('Delete Course').props('rounded color=red text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', handle_delete)
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/course'))

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
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/course'))
