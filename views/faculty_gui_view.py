# views/faculty_gui_view.py
from nicegui import ui
from views.gui_theme import GUITheme

class FacultyGUIView:
    faculty_model      = None
    faculty_controller = None

    @ui.page('/faculty')
    @staticmethod
    def faculty():
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-primary)')
        with ui.column().classes('w-full items-center pt-12 pb-12 font-sans'):
            ui.label('Faculty').classes('text-4xl mb-10 text-black')
            for label, route in [
                ('Add Faculty',    '/faculty/add'),
                ('Modify Faculty', '/faculty/modify'),
                ('Delete Faculty', '/faculty/delete'),
                ('View Faculty',   '/faculty/view'),
            ]:
                ui.button(label).props('rounded color=black text-color=white no-caps') \
                    .classes('w-80 h-16 text-xl mb-2').on('click', lambda r=route: ui.navigate.to(r))
            ui.space()
            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl mt-4').on('click', lambda: ui.navigate.to('/'))

    @ui.page('/faculty/add')
    @staticmethod
    def faculty_add():
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-add)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))

    @ui.page('/faculty/modify')
    @staticmethod
    def faculty_modify():
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-modify)')
        with ui.column().classes('gap-6 items-center w-full'):
            ui.label('Under Construction!').classes('text-4xl mb-10 text-black')
            ui.button('Back').props('rounded color=black text-color=white no-caps') \
                .classes('w-80 h-16 text-xl').on('click', lambda: ui.navigate.to('/faculty'))

    @ui.page('/faculty/delete')
    @staticmethod
    def faculty_delete():
        GUITheme.applyTheming()
        ui.query('body').style('background-color: var(--q-delete)')

        with ui.column().classes('w-full items-center pt-12 pb-12 gap-4'):
            ui.label('Delete Faculty').classes('text-4xl mb-6 text-black')

            container = ui.column().classes('w-full max-w-lg gap-3 items-center')
            status    = ui.label('').classes('text-sm')

            def build(c):
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
                                    def _delete():
                                        with ui.dialog() as dlg, ui.card().classes('p-8 gap-4 items-center text-center'):
                                            ui.label(f"Delete '{name}'?").classes('text-xl font-bold')
                                            ui.label('This will also remove them from any course assignments.') \
                                                .classes('text-sm text-gray-500')
                                            with ui.row().classes('gap-4 mt-4'):
                                                ui.button('Cancel', on_click=dlg.close) \
                                                    .props('rounded color=black text-color=white no-caps')

                                                def confirm(d=dlg, n=name, mod=m, s=sl):
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