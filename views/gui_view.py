# views/gui_view.py
"""
GUIView - Graphical-user interface for all user interactions

This view class handles all files for the GUI that don't have
their own files (i.e. the landing page, the navigation page, and currently including
print config, run scheduler, and display schedules)
"""

from nicegui import ui
from views.faculty_gui_view import FacultyGUIView
from views.course_gui_view import CourseGUIView
from views.conflict_gui_view import ConflictGUIView
from views.lab_gui_view import LabGUIView
from views.schedule_gui_view import ScheduleGUIView, _state as _schedule_state
from views.room_gui_view import RoomGUIView
from views.gui_theme import GUITheme
from time_config_data_class import time_config_data
from scheduler import TimeBlock, Meeting

class GUIView:
    config_path: str = ''
    controller = None

    @ui.page('/')
    @staticmethod
    def home():
        GUITheme.applyTheming()
        ui.add_css('''
            .load-dialog, .load-dialog *,
            .load-dialog .q-field__label,
            .load-dialog .q-field__native,
            .load-dialog .q-uploader__title,
            .load-dialog .q-uploader__subtitle,
            .load-dialog .q-uploader__header,
            .load-dialog .q-uploader__list {
                color: black !important;
            }
            .load-dialog .q-uploader {
                background: #f5f5f5 !important;
                color: black !important;
            }
            .load-dialog .q-uploader__file-status,
            .load-dialog .q-uploader__file,
            .load-dialog .q-uploader__list {
                display: none !important;
            }
            .load-dialog .q-uploader__subtitle {
                display: none !important;
            }
        ''')

        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            
            # Title
            ui.label('Scheduler').classes('text-4xl mb-10 !text-black dark:!text-white')
            
            # Row 1
            with ui.row().classes('gap-12 mb-4'):
                ui.button('Faculty').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/faculty'))
                ui.button('Room').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/room'))
                
            # Row 2
            with ui.row().classes('gap-12 mb-4'):
                ui.button('Course').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/course'))
                ui.button('Conflict').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/conflict'))
                
            # Row 3 (Lab)
            with ui.row().classes('mb-12'):
                ui.button('Lab').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/lab'))
                
            # Wide buttons vertically stacked
            with ui.column().classes('gap-6 items-center w-full'):
                ui.button('Print Config').props('rounded no-caps').classes('w-80 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/print_config'))
                ui.button('Time Slot Config').props('rounded no-caps').classes('w-80 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/time_config'))
                with ui.row().classes('gap-6'):
                    ui.button('Run Scheduler').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/run_scheduler'))
                    ui.button('Display Schedules').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/display_schedules'))
                with ui.row().classes('gap-6'):
                    ui.button('Load Configuration').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: load_dialog.open())
                    ui.button('Export Configuration').props('rounded no-caps').classes('w-40 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', GUIView.export_configuration)

        with ui.dialog() as load_dialog:
            with ui.card().classes('w-96 gap-4 load-dialog').style('background: white;'):
                ui.label('Load Configuration (.json)').style('color: black !important; font-size: 1.1rem; font-weight: 600;')

                status_label = ui.label('').style('color: black !important;')

                async def handle_upload(e):
                    #import os
                    from models.config_model import ConfigModel
                    from models.faculty_model import FacultyModel
                    from models.course_model import CourseModel
                    from models.conflict_model import ConflictModel
                    from models.lab_model import LabModel
                    from models.room_model import RoomModel
                    from models.scheduler_model import SchedulerModel
                    from controllers.faculty_controller import FacultyController
                    from controllers.course_controller import CourseController
                    from controllers.conflict_controller import ConflictController
                    from controllers.lab_controller import LabController
                    from controllers.room_controller import RoomController
                    from controllers.schedule_controller import ScheduleController

                    try:
                        real_name = e.file.name
                        file_path = real_name

                        with open(file_path, 'wb') as f:
                            f.write(await e.file.read())

                        ctrl = GUIView.controller
                        # Use the GUIView instance as view — works whether or not
                        # a config was previously loaded
                        view = ctrl.view if (ctrl and ctrl.view) else GUIView()

                        new_config          = ConfigModel(file_path)
                        new_faculty_model   = FacultyModel(new_config)
                        new_course_model    = CourseModel(new_config)
                        new_conflict_model  = ConflictModel(new_config)
                        new_lab_model       = LabModel(new_config)
                        new_room_model      = RoomModel(new_config)
                        new_scheduler_model = SchedulerModel(new_config)

                        new_faculty_ctrl   = FacultyController(new_faculty_model, view)
                        new_course_ctrl    = CourseController(new_course_model, new_config)
                        new_conflict_ctrl  = ConflictController(new_conflict_model, view)
                        new_lab_ctrl       = LabController(new_lab_model, view)
                        new_room_ctrl      = RoomController(new_room_model, view)
                        new_schedule_ctrl  = ScheduleController(new_scheduler_model, view)

                        ctrl.config_model        = new_config
                        ctrl.faculty_model       = new_faculty_model
                        ctrl.course_model        = new_course_model
                        ctrl.conflict_model      = new_conflict_model
                        ctrl.lab_model           = new_lab_model
                        ctrl.room_model          = new_room_model
                        ctrl.scheduler_model     = new_scheduler_model
                        ctrl.faculty_controller  = new_faculty_ctrl
                        ctrl.course_controller   = new_course_ctrl
                        ctrl.conflict_controller = new_conflict_ctrl
                        ctrl.lab_controller      = new_lab_ctrl
                        ctrl.room_controller     = new_room_ctrl
                        ctrl.schedule_controller = new_schedule_ctrl
                        ctrl.view                = view
                        ctrl.config_path         = file_path

                        FacultyGUIView.faculty_model        = new_faculty_model
                        FacultyGUIView.faculty_controller   = new_faculty_ctrl

                        CourseGUIView.course_model          = new_course_model
                        CourseGUIView.course_controller     = new_course_ctrl

                        ConflictGUIView.conflict_model      = new_conflict_model
                        ConflictGUIView.conflict_controller = new_conflict_ctrl

                        LabGUIView.lab_model                = new_lab_model
                        LabGUIView.lab_controller           = new_lab_ctrl
                        LabGUIView._lab_controller          = new_lab_ctrl

                        RoomGUIView.room_model              = new_room_model
                        RoomGUIView.room_controller         = new_room_ctrl

                        _schedule_state._scheduler_model    = new_scheduler_model
                        ScheduleGUIView.schedule_controller = new_schedule_ctrl

                        GUIView.config_path = file_path
                        GUIView.controller.config_path = file_path
                        
                        ctrl.config_path = file_path
                        GUIView.config_path = file_path
                        GUIView.controller.config_path = file_path
                        
                        status_label.style('color: green !important;')
                        status_label.set_text(f'✓ Loaded: {e.file.name}')
                        ui.notify('Configuration loaded successfully!', type='positive')
                        load_dialog.close()

                    except Exception as ex:
                        status_label.style('color: red !important;')
                        status_label.set_text(f'Error: {ex}')

                ui.upload(
                    label='Select JSON file',
                    auto_upload=True,
                    max_files=1,
                    on_upload=handle_upload,
                ).classes('w-full').style('color: black !important;')

                ui.button('Cancel').props('flat no-caps').style('color: black !important;').on('click', load_dialog.close)

    @staticmethod
    def export_configuration():
        """
        Exports the configuration file.
        Asks the controller to save current in-memory configurations to disk, then downloads.
        """
        try:
            
            success = GUIView.controller.save_configuration()
            if success:
                import os
                real_name = os.path.basename(GUIView.controller.config_path)
                ui.download(GUIView.controller.config_path, real_name)                
                ui.notify('Configuration exported successfully!', type='positive')
            else:
                ui.notify('Error saving configuration.', type='negative')
        except Exception as e:
            ui.notify(f'Failed to export configuration: {e}', type='negative')

    @ui.page('/print_config')
    @staticmethod
    def print_config():
        """
        Displays the GUI for printing the config file.

        If no configuration is loaded, shows a message and a Back button
        instead of attempting to render config data.

        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)').classes('dark:!bg-black')

        cm = GUIView.controller.config_model if GUIView.controller else None

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-6'):
            ui.label('Configuration').classes('text-4xl mb-10 !text-black dark:!text-white')

            if cm is None:
                ui.label('No configuration loaded.').classes('text-xl italic !text-gray-500 dark:!text-gray-400')
                ui.label('Return to the home page and use Load Configuration to load a file.').classes('text-base !text-gray-400 dark:!text-gray-500')
                ui.button('Back').props('rounded color=black text-color=white no-caps') \
                    .classes('w-80 h-16 text-xl mt-6 dark:!bg-white dark:!text-black') \
                    .on('click', lambda: ui.navigate.to('/'))
                return

            with ui.expansion('Rooms', icon='meeting_room').classes('w-3/4 !text-black dark:!text-white'):
                for room in cm.get_all_rooms():
                    ui.label(room).classes('!text-black dark:!text-white')

            with ui.expansion('Labs', icon='computer').classes('w-3/4 !text-black dark:!text-white'): 
                for lab in cm.get_all_labs():
                    ui.label(lab).classes('!text-black dark:!text-white')

            with ui.expansion('Courses', icon='book').classes('w-3/4 !text-black dark:!text-white'):
                with ui.scroll_area().classes('w-full h-64'):
                    for course in cm.get_all_courses():
                        with ui.card().classes('w-full mb-2 !bg-white dark:!bg-gray-800'):
                            with ui.row().classes('w-full justify-between items-center'):
                                ui.label(course.course_id).classes('font-bold text-lg !text-black dark:!text-white')
                                ui.label(f'{course.credits} credits').classes('text-gray-500 dark:!text-gray-300')
                            with ui.row().classes('gap-4'):
                                ui.label(f'Rooms: {", ".join(course.room) or "Any"}').classes('text-sm !text-black dark:!text-white')
                                ui.label(f'Labs: {", ".join(course.lab) or "None"}').classes('text-sm !text-black dark:!text-white')
                                ui.label(f'Faculty: {", ".join(course.faculty) or "Any"}').classes('text-sm !text-black dark:!text-white')

            with ui.expansion('Faculty', icon='person').classes('w-3/4 !text-black dark:!text-white'):
                for f in cm.get_all_faculty():
                    with ui.expansion(f.name).classes('w-full !text-black dark:!text-white'):
                        ui.label(f'Max credits: {f.maximum_credits}').classes('!text-black dark:!text-white')
                        ui.label(f'Min credits: {f.minimum_credits}').classes('!text-black dark:!text-white')
                        for day, slots in f.times.items():
                            ui.label(f'{day}: {", ".join(str(s) for s in slots) or "Unavailable"}').classes('!text-black dark:!text-white')

            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))
    @ui.page('/time_config')
    @staticmethod
    def time_slot_config():
        """
        Full GUI for time slot configuration and class pattern management:
        - Days / time blocks
        - Class patterns
        - Meetings (add/edit/delete)
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)').classes('dark:!bg-black')

        cm = getattr(GUIView.controller, 'config_model', None)
        if cm is None:
            with ui.column().classes('w-full items-center pt-12 gap-6'):
                ui.label('No configuration loaded.').classes('text-xl italic !text-gray-500 dark:!text-gray-400')
                ui.button('Back').props('rounded color=black text-color=white no-caps')\
                    .classes('w-80 h-16 text-xl mt-6 dark:!bg-white dark:!text-black')\
                    .on('click', lambda: ui.navigate.to('/'))
            return

        time_config = time_config_data(cm.config.time_slot_config)
        container = ui.column().classes('w-3/4 items-center gap-4')
        ui.label("Time Slot Config").classes('text-4xl mb-6 !text-black dark:!text-white')

        # -----------------------------
        # Helper UI Elements
        # -----------------------------
        def time_picker(label: str, value: str | None = None):
            inp = ui.input(label=label, value=value or "").classes('w-full !text-black dark:!text-white')
            with ui.menu().props('no-parent-event') as menu:
                ui.time().bind_value(inp).props('color=black text-color=white no-caps')
                with ui.row().classes('justify-end'):
                    ui.button('Close', on_click=menu.close).props('flat').classes('!text-black dark:!text-white')
            with inp.add_slot('append'):
                ui.icon('access_time').on('click', menu.open).classes('cursor-pointer !text-black dark:!text-white')
            return inp

        def number_input(label, value=0, min_val=0):
            return ui.number(label=label, value=value, min=min_val).classes('w-full mb-2 !text-black dark:!text-white')

        def checkbox(label, value=False):
            return ui.checkbox(text=label, value=value).classes('!text-black dark:!text-white mb-2')

        # -----------------------------
        # Refresh function
        # -----------------------------
        def refresh():
            container.clear()
            render()

        # -----------------------------
        # Rendering
        # -----------------------------
        def render():
            # Days / Time Blocks
            with ui.expansion('Available Days', icon='meeting_room').classes('w-full !text-black dark:!text-white'):
                with ui.row().classes('w-full justify-between items-center mb-2'):
                    ui.label('Days').classes('text-lg !text-black dark:!text-white')
                    ui.button(icon='add').props('flat round').classes('!text-black dark:!text-white')\
                        .on('click', add_time_block)

                for day, blocks in time_config.get_all_time_slots().items():
                    with ui.expansion(str(day)).classes('w-full !text-black dark:!text-white'):
                        if not blocks:
                            ui.label('No time blocks available').classes('italic text-gray-500 dark:!text-gray-400')
                        for i, b in enumerate(blocks):
                            with ui.card().classes('w-full p-4 bg-gray-100 dark:bg-gray-800'):
                                s_input = time_picker('Start Time', b.start)
                                e_input = time_picker('End Time', b.end)
                                sp_input = number_input('Spacing', b.spacing or 0)

                                with ui.row().classes('gap-2 mt-2'):
                                    ui.button('Save', on_click=lambda d=day, idx=i, s=s_input, e=e_input, sp=sp_input: save_time_block(d, idx, s, e, sp))\
                                    .classes('!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white')
                                    ui.button(icon='delete', on_click=lambda d=day, idx=i: delete_time_block(d, idx))\
                                    .props('flat color=red')

            # Class Patterns
            with ui.expansion('Class Patterns', icon='school').classes('w-full !text-black dark:!text-white'):
                classes = time_config.get_classes()
                if not classes:
                    ui.label('No class patterns available').classes('italic text-gray-500 dark:!text-gray-400')
                for idx, cls in enumerate(classes, start=1):
                    with ui.expansion(f'Pattern {idx}').classes('w-full !text-black dark:!text-white'):
                        with ui.card().classes('w-full p-4 bg-gray-100 dark:bg-gray-800'):
                            credits_input = number_input('Credits', cls.credits)
                            disabled_input = checkbox('Disabled', cls.disabled)
                            start_input = time_picker('Start Time', cls.start_time)
                            ui.button('Save', on_click=lambda c=cls, cr=credits_input, dis=disabled_input, st=start_input: save_class_pattern(c, cr, dis, st))\
                            .classes('!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white')

                            # Meetings
                            with ui.expansion('Meetings').classes('w-full !text-black dark:!text-white mt-2'):
                                ui.button(icon='add').props('flat round').classes('!text-black dark:!text-white mb-2')\
                                    .on('click', lambda c=cls: add_meeting(c))

                                if not cls.meetings:
                                    ui.label('No meetings').classes('italic text-gray-500 dark:!text-gray-400')
                                for i, m in enumerate(cls.meetings):
                                    with ui.card().classes('w-full p-4 bg-gray-200 dark:bg-gray-700'):
                                        day_input = ui.select(options=time_config.get_days(), value=m.day, label='Day')\
                                            .classes('w-full mb-2 !text-black dark:!text-white')
                                        start_input = time_picker('Start Time', m.start_time)
                                        dur_input = number_input('Duration', m.duration, 1)
                                        lab_input = checkbox('Lab Meeting', m.lab)

                                        with ui.row().classes('gap-2 mt-2'):
                                            ui.button('Save', on_click=lambda cls=cls, idx=i, di=day_input, st=start_input, dur=dur_input, lab=lab_input:
                                                    save_meeting(cls, idx, di, st, dur, lab))\
                                            .classes('!bg-gray-300 !text-black dark:!bg-gray-600 dark:!text-white')
                                            ui.button(icon='delete', on_click=lambda cls=cls, idx=i: delete_meeting(cls, idx))\
                                            .props('flat color=red')

        # -----------------------------
        # Actions
        # -----------------------------
        def add_time_block():
            with ui.dialog() as d, ui.card().classes('w-96 p-4 bg-gray-100 dark:bg-gray-800'):
                ui.label('Add Time Block').classes('text-xl mb-4 !text-black dark:!text-white')
                day_select = ui.select(options=time_config.get_days(), label='Day').classes('w-full mb-2 !text-black dark:!text-white')
                start_input = time_picker('Start Time')
                end_input = time_picker('End Time')
                spacing_input = number_input('Spacing', 0)
                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button('Cancel', on_click=d.close)
                    ui.button('Add', on_click=lambda d=d, ds=day_select, s=start_input, e=end_input, sp=spacing_input: add_time_block_submit(d, ds, s, e, sp))
            d.open()

        def add_time_block_submit(dialog, day_sel, start_inp, end_inp, sp_inp):
            if not day_sel.value or not start_inp.value or not end_inp.value:
                ui.notify('Please fill all fields', color='red')
                return
            time_config.add_time_block(day_sel.value, TimeBlock(start=start_inp.value, end=end_inp.value, spacing=sp_inp.value or 0))
            dialog.close()
            refresh()

        def save_time_block(day, idx, s, e, sp):
            try:
                time_config.update_time_block(day, idx, TimeBlock(start=s.value, end=e.value, spacing=sp.value or 0))
            except Exception as ex:
                ui.notify(f'Error: {ex}', color='red')
            refresh()

        def delete_time_block(day, idx):
            time_config.remove_time_block(day, idx)
            refresh()

        def save_class_pattern(cls, cr_input, dis_input, st_input):
            cls.credits = cr_input.value
            cls.disabled = dis_input.value
            cls.start_time = st_input.value or None
            refresh()

        def add_meeting(cls):
            with ui.dialog() as d, ui.card().classes('w-96 p-4 bg-gray-100 dark:bg-gray-800'):
                ui.label('Add Meeting').classes('text-xl mb-4 !text-black dark:!text-white')
                day_sel = ui.select(options=time_config.get_days(), label='Day').classes('w-full mb-2 !text-black dark:!text-white')
                start_inp = time_picker('Start Time')
                dur_inp = number_input('Duration', 60, 1)
                lab_chk = checkbox('Lab Meeting')
                with ui.row().classes('w-full justify-end gap-2'):
                    ui.button('Cancel', on_click=d.close)
                    ui.button('Add', on_click=lambda d=d, c=cls, ds=day_sel, st=start_inp, dur=dur_inp, lab=lab_chk: add_meeting_submit(d, c, ds, st, dur, lab))
            d.open()

        def add_meeting_submit(dialog, cls, day_sel, start_inp, dur_inp, lab_chk):
            if not day_sel.value or not start_inp.value or not dur_inp.value:
                ui.notify('Please fill all fields', color='red')
                return
            time_config.add_meeting(cls, Meeting(day=day_sel.value, start_time=start_inp.value, duration=dur_inp.value, lab=lab_chk.value))
            dialog.close()
            refresh()

        def delete_meeting(cls, idx):
            time_config.remove_meeting(cls, idx)
            refresh()

        def save_meeting(cls, idx, day_input, start_input, dur_input, lab_input):
            try:
                meeting = cls.meetings[idx]
                meeting.day = day_input.value
                meeting.start_time = start_input.value
                meeting.duration = dur_input.value
                meeting.lab = lab_input.value
                refresh()
            except Exception as ex:
                ui.notify(f"Error saving meeting: {ex}", color="red")

        # -----------------------------
        # Initial render
        # -----------------------------
        refresh()
    @staticmethod
    def runGUI():
        """
        Runs the GUI.
                
        Parameters:
            None        
        Returns:        
            None
        """
        ui.run(title='Scheduler', storage_secret='scheduler_secret_key')

if __name__ in {"__main__", "__mp_main__"}:
    GUIView.runGUI()