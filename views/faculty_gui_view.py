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

        with ui.column().classes('w-full items-center font-sans p-8 gap-0'):
            # Title
            ui.label('Add Faculty').classes('text-5xl mb-12 mt-4 text-black')
            
            with ui.row().classes('w-full max-w-6xl justify-between items-start'):
                # Left Column
                with ui.column().classes('w-[50%] gap-6'):
                    with ui.row().classes('items-center gap-4 w-full'):
                        ui.label('Enter Faculty Name:').classes('text-2xl text-black')
                        name_input = ui.input().props('outlined dense square borderless').classes('w-64 text-xl bg-white').style('border: 2px solid black;')
                        
                    with ui.row().classes('items-center gap-6 w-full'):
                        ui.label('Faculty Position:').classes('text-2xl text-black')
                        position_radio = ui.radio(['Full Time', 'Adjunct'], value='Full Time').props('inline color=black').classes('text-xl text-black gap-4')

                    ui.label('Faculty Availability:').classes('text-2xl text-black')
                    
                    # Separate availability for each day
                    day_inputs = {}
                    with ui.column().classes('w-full pl-4 gap-2'):
                        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']:
                            with ui.row().classes('items-center w-full justify-between pr-4'):
                                cb = ui.checkbox(day).props('color=black keep-color').classes('text-xl text-black w-32')
                                
                                def handle_time_change(e, is_start, related_input):
                                    if e.value and not related_input.value:
                                        related_input.value = '17:00' if is_start else '09:00'
                                
                                with ui.row().classes('items-center gap-2').bind_visibility_from(cb, 'value'):
                                    start_input = ui.input('Start (e.g. 09:00)').props('outlined dense square borderless').classes('w-28 bg-white').style('border: 2px solid black;')
                                    ui.label('to').classes('text-lg text-black')
                                    end_input = ui.input('End (e.g. 17:00)').props('outlined dense square borderless').classes('w-28 bg-white').style('border: 2px solid black;')
                                    
                                    start_input.on_value_change(lambda e, si=start_input, ei=end_input: handle_time_change(e, True, ei))
                                    end_input.on_value_change(lambda e, si=start_input, ei=end_input: handle_time_change(e, False, si))
                                    
                                day_inputs[day] = {'cb': cb, 'start': start_input, 'end': end_input}

                    # Courses and Preferences
                    with ui.column().classes('w-full mt-6 gap-2'):
                        ui.label('Courses and Preferences:').classes('text-2xl text-black')
                        
                        course_container = ui.column().classes('w-full gap-2')
                        course_rows = []
                        def add_course_row():
                            with course_container:
                                row_container = ui.row().classes('items-center gap-4 w-full wrap')
                                with row_container:
                                    course_input = ui.input('Course Code').props('outlined dense square borderless').classes('flex-grow bg-white').style('border: 2px solid black; min-width: 150px;')
                                    weight_input = ui.number('Weight (1-10)', min=1, max=10, value=5).props('outlined dense square borderless').classes('w-40 bg-white').style('border: 2px solid black;')
                                    
                                    row_data = {'course': course_input, 'weight': weight_input}
                                    course_rows.append(row_data)
                                    
                                    def delete_row(e, rc=row_container, rd=row_data):
                                        rc.delete()
                                        if rd in course_rows:
                                            course_rows.remove(rd)
                                            
                                    ui.button('X', on_click=delete_row).props('color=red text-color=white rounded glossy').classes('h-10 w-10 min-w-10')
                        
                        # Add initial row
                        add_course_row()
                        
                        ui.button('+ Add Course', on_click=add_course_row).props('color=black text-color=white rounded').classes('mt-2 px-6')

                # Right Column
                with ui.column().classes('w-[45%] h-[500px] border-4 border-black bg-white p-6 items-start justify-start overflow-hidden'):
                    ui.label('Existing Faculty').classes('text-3xl text-black text-center w-full mb-4 font-bold border-b-2 border-black pb-2')
                    scroll_area = ui.scroll_area().classes('w-full h-full pr-4')
                    
                    def refresh_faculty_list():
                        scroll_area.clear()
                        with scroll_area:
                            from views.gui_view import GUIView
                            if not GUIView._controller:
                                ui.label('System not initialized properly.').classes('text-xl text-red-500')
                                return
                                
                            try:
                                faculty_list = GUIView._controller.config_model.get_all_faculty()
                                if faculty_list:
                                    for f in faculty_list:
                                        ui.label(f.name).classes('text-xl text-black mb-2 py-2 border-b border-gray-200 w-full')
                                else:
                                    ui.label('No existing faculty found.').classes('text-xl text-gray-500 italic')
                            except Exception as e:
                                ui.label('Could not load faculty data.').classes('text-xl text-red-500')
                    
                    refresh_faculty_list()

            # Save action function
            def save_faculty():
                name = name_input.value
                if not name:
                    ui.notify('Faculty name is required!', type='negative')
                    return
                
                is_full_time = position_radio.value == 'Full Time'
                
                times_data = {}
                for day, inputs in day_inputs.items():
                    if inputs['cb'].value:
                        start_time = inputs['start'].value or '09:00'
                        end_time = inputs['end'].value or '17:00'
                        times_data[day] = [{'start': start_time, 'end': end_time}]
                
                course_prefs = {}
                for row in course_rows:
                    course = row['course'].value
                    if course:
                        course_prefs[course] = int(row['weight'].value or 5)
                        
                faculty_data = {
                    'name': name,
                    'is_full_time': is_full_time,
                    'times': times_data,
                    'days': list(times_data.keys()),  # for compatibility
                    'course_preferences': course_prefs,
                }
                
                try:
                    from views.gui_view import GUIView
                    if not GUIView._controller:
                        ui.notify('System not initialized properly.', type='negative')
                        return
                    
                    controller = GUIView._controller.faculty_controller
                    
                    if controller.add_faculty(faculty_data):
                        ui.notify(f"Faculty '{name}' added successfully!", type='positive')
                        name_input.value = ''
                        refresh_faculty_list()
                    else:
                        ui.notify(f"Failed to add faculty '{name}'. Maybe they already exist?", type='negative')
                except Exception as e:
                    ui.notify(f"Error saving: {e}", type='negative')

            # Bottom row for buttons
            with ui.row().classes('w-full max-w-6xl justify-between items-end mt-16'):
                ui.button('Cancel').props('rounded color=black text-color=white no-caps').classes('w-48 h-16 text-2xl font-bold').on('click', lambda: ui.navigate.to('/faculty'))
                ui.button('Save').props('rounded color=black text-color=white no-caps').classes('w-48 h-16 text-2xl font-bold').on('click', save_faculty)

    @ui.page('/faculty/modify')
    @staticmethod
    def faculty_modify():
        """
        Displays the GUI for modifying faculty.
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps').classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))

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