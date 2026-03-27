import re

files = [
    "views/faculty_gui_view.py",
    "views/course_gui_view.py",
    "views/conflict_gui_view.py",
    "views/room_gui_view.py",
    "views/lab_gui_view.py",
    "views/schedule_gui_view.py",
]


def update_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Backgrounds
    content = re.sub(
        r"(ui\.query\('body'\)\.style\('background-color: var\(--q-[a-zA-Z]+\)'\))",
        r"\1.classes('dark:!bg-black')",
        content,
    )

    # 2. text-black -> !text-black dark:!text-white
    content = re.sub(
        r"(?<!!)text-black(?!\s*dark:!text-white)",
        "!text-black dark:!text-white",
        content,
    )

    # 3. Buttons (rounded color=black text-color=white ...) -> append dark:!bg-white dark:!text-black to .classes()
    def button_repl(m):
        props_str = m.group(1)
        classes_str = m.group(2)
        if "dark:!bg-white" not in classes_str:
            classes_str += " dark:!bg-white dark:!text-black"
        return f"{props_str}.classes('{classes_str}')"

    content = re.sub(
        r"(\.props\('[^']*color=black text-color=white[^']*'\)(?:\s*\\\n\s*)?)\.classes\('([^']+)'\)",
        button_repl,
        content,
    )

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)


for filepath in files:
    print(f"Updating {filepath}")
    update_file(filepath)
    print(f"Done {filepath}")
