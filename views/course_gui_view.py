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
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
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
