# views/gui_utils.py
"""
GUIUtils - Shared utility functions for GUI views.
"""
from nicegui import ui


def require_config(back_url: str = '/') -> bool:
    """
    Checks whether a configuration has been loaded.

    If no configuration is loaded, renders a 'no config' message on the
    current page with a Load Configuration button and a Back button, then
    returns False. The calling page function should return immediately after
    a False result.

    Parameters:
        back_url (str): The URL the Back button navigates to. Defaults to '/'.
    Returns:
        bool: True if a config is loaded, False if the no-config UI was rendered.
    """
    from views.gui_view import GUIView
    if GUIView.controller is not None and GUIView.controller.config_model is not None:
        return True

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
        .load-dialog .q-uploader__list,
        .load-dialog .q-uploader__subtitle {
            display: none !important;
        }
        .load-dialog .q-uploader__header-content .q-uploader__subtitle {
            display: none !important;
        }
        .load-dialog .q-uploader__header {
            background: #f5f5f5 !important;
            color: black !important;
        }
        .load-dialog .q-uploader__title {
            color: black !important;
        }
    ''')

    with ui.column().classes('w-full items-center pt-24 pb-12 gap-6'):
        ui.icon('folder_off').classes('text-6xl text-gray-400 dark:text-gray-500')
        ui.label('No Configuration Loaded').classes('text-2xl !text-black dark:!text-white')
        ui.label('Please load a configuration file to continue.') \
            .classes('text-base !text-gray-500 dark:!text-gray-400')

        load_dialog = ui.dialog()
        with load_dialog:
            with ui.card().classes('w-96 gap-4 load-dialog').style('background: white;'):
                ui.label('Load Configuration (.json)').style(
                    'color: black !important; font-size: 1.1rem; font-weight: 600;'
                )
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
                    from views.faculty_gui_view import FacultyGUIView
                    from views.course_gui_view import CourseGUIView
                    from views.conflict_gui_view import ConflictGUIView
                    from views.lab_gui_view import LabGUIView
                    from views.room_gui_view import RoomGUIView
                    from views.schedule_gui_view import ScheduleGUIView
                    from views.schedule_gui_view import _state as _schedule_state

                    try:
                        file_path = f'temp_{e.file.name}'
                        with open(file_path, 'wb') as f:
                            f.write(await e.file.read())

                        ctrl = GUIView.controller
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
                        GUIView.config_path                 = file_path

                        os.remove(file_path)

                        status_label.style('color: green !important;')
                        status_label.set_text(f'✓ Loaded: {e.file.name}')
                        ui.notify('Configuration loaded successfully!', type='positive')
                        load_dialog.close()
                        ui.navigate.reload()

                    except Exception as ex:
                        status_label.style('color: red !important;')
                        status_label.set_text(f'Error: {ex}')

                ui.upload(
                    label='Select JSON file',
                    auto_upload=True,
                    max_files=1,
                    on_upload=handle_upload,
                ).classes('w-full')

                ui.button('Cancel').props('flat no-caps').style('color: black !important;') \
                    .on('click', load_dialog.close)

        with ui.row().classes('gap-4'):
            ui.button('Load Configuration') \
                .props('rounded color=black text-color=white no-caps') \
                .classes('w-56 h-14 text-lg dark:!bg-white dark:!text-black') \
                .on('click', load_dialog.open)
            ui.button('Back') \
                .props('rounded color=black text-color=white no-caps') \
                .classes('w-56 h-14 text-lg dark:!bg-white dark:!text-black') \
                .on('click', lambda: ui.navigate.to(back_url))

    return False