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
                ui.button('Run Scheduler').props('rounded no-caps').classes('w-80 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/run_scheduler'))
                ui.button('Display Schedules').props('rounded no-caps').classes('w-80 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: ui.navigate.to('/display_schedules'))
                ui.button('Load Configuration').props('rounded no-caps').classes('w-80 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', lambda: load_dialog.open())
                ui.button('Export Configuration File').props('rounded no-caps').classes('w-80 h-16 text-xl !bg-black dark:!bg-white !text-white dark:!text-black').on('click', GUIView.export_configuration)

        with ui.dialog() as load_dialog:
            with ui.card().classes('w-96 gap-4 load-dialog').style('background: white;'):
                ui.label('Load Configuration (.json)').style('color: black !important; font-size: 1.1rem; font-weight: 600;')

                status_label = ui.label('').style('color: black !important;')

                async def handle_upload(e):
                    import os
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
                        file_path = f'temp_{e.file.name}'
                        with open(file_path, 'wb') as f:
                            f.write(await e.file.read())

                        ctrl = GUIView.controller

                        new_config = ConfigModel(file_path)

                        new_faculty_model   = FacultyModel(new_config)
                        new_course_model    = CourseModel(new_config)
                        new_conflict_model  = ConflictModel(new_config)
                        new_lab_model       = LabModel(new_config)
                        new_room_model      = RoomModel(new_config)
                        new_scheduler_model = SchedulerModel(new_config)

                        new_faculty_ctrl   = FacultyController(new_faculty_model, ctrl.view)
                        new_course_ctrl    = CourseController(new_course_model, new_config)
                        new_conflict_ctrl  = ConflictController(new_conflict_model, ctrl.view)
                        new_lab_ctrl       = LabController(new_lab_model, ctrl.view)
                        new_room_ctrl      = RoomController(new_room_model, ctrl.view)
                        new_schedule_ctrl  = ScheduleController(new_scheduler_model, ctrl.view)

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

                        os.remove(file_path)

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
                ui.download(GUIView.controller.config_path, 'scheduler_configuration.json')
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
                
        Parameters:
            None        
        Returns:
            None
        """
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        cm = GUIView.controller.config_model

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-6'):
            ui.label('Configuration').classes('text-4xl mb-10 !text-black dark:!text-white')

            with ui.expansion('Rooms', icon='meeting_room').classes('w-3/4'):
                for room in cm.get_all_rooms():
                    ui.label(room)

            with ui.expansion('Labs', icon='computer').classes('w-3/4'): 
                for lab in cm.get_all_labs():
                    ui.label(lab)

            with ui.expansion('Courses', icon='book').classes('w-3/4'):
                with ui.scroll_area().classes('w-full h-64'):
                    for course in cm.get_all_courses():
                        with ui.card().classes('w-full mb-2 !bg-white dark:!bg-white'):
                            with ui.row().classes('w-full justify-between items-center'):
                                ui.label(course.course_id).classes('font-bold text-lg !text-black')
                                ui.label(f'{course.credits} credits').classes('text-gray-500')
                            with ui.row().classes('gap-4'):
                                ui.label(f'Rooms: {", ".join(course.room) or "Any"}').classes('text-sm !text-black')
                                ui.label(f'Labs: {", ".join(course.lab) or "None"}').classes('text-sm !text-black')
                                ui.label(f'Faculty: {", ".join(course.faculty) or "Any"}').classes('text-sm !text-black')

            with ui.expansion('Faculty', icon='person').classes('w-3/4'):
                for f in cm.get_all_faculty():
                    with ui.expansion(f.name).classes('w-full'):
                        ui.label(f'Max credits: {f.maximum_credits}')
                        ui.label(f'Min credits: {f.minimum_credits}')
                        for day, slots in f.times.items():
                            ui.label(f'{day}: {", ".join(str(s) for s in slots) or "Unavailable"}')

            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl dark:!bg-white dark:!text-black').on('click', lambda: ui.navigate.to('/'))

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