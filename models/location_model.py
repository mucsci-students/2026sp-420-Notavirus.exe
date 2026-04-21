# models/location_model.py
"""
LocationModel - Shared base for LabModel and RoomModel.

Both models manage a named list (labs or rooms), update course references,
and update faculty preference dicts. The only differences are which
attribute names to use, so we parameterise those at construction time.
"""


class LocationModel:
    """
    Base class for location-type models (labs, rooms).

    Parameters
    ----------
    config_model : ConfigModel
    list_attr    : str  — attribute on config.config holding the list  (e.g. "labs")
    course_attr  : str  — attribute on CourseConfig                     (e.g. "lab")
    pref_attr    : str  — attribute on FacultyConfig for preferences    (e.g. "lab_preferences")
    """

    def __init__(
        self,
        config_model,
        list_attr: str,
        course_attr: str,
        pref_attr: str,
    ):
        self.config_model = config_model
        self._list_attr = list_attr
        self._course_attr = course_attr
        self._pref_attr = pref_attr

    @property
    def _cfg(self):
        return self.config_model.config.config

    @property
    def _items(self) -> list[str]:
        return getattr(self._cfg, self._list_attr)

    # ------------------------------------------------------------------
    # Protected CRUD helpers — subclasses delegate to these
    # ------------------------------------------------------------------

    def _exists(self, name: str) -> bool:
        return name in self._items

    def _add(self, name: str) -> bool:
        if not name or not name.strip():
            return False
        if self._exists(name):
            return False
        self._items.append(name)
        return True

    def _delete(self, name: str) -> bool:
        if not self._exists(name):
            return False
        for course in self._cfg.courses:
            setattr(
                course,
                self._course_attr,
                [x for x in getattr(course, self._course_attr) if x != name],
            )
        for faculty in self._cfg.faculty:
            prefs = getattr(faculty, self._pref_attr)
            if name in prefs:
                del prefs[name]
        setattr(
            self._cfg,
            self._list_attr,
            [x for x in self._items if x != name],
        )
        return True

    def _modify(self, old_name: str, new_name: str) -> bool:
        if not new_name or not new_name.strip():
            return False
        if not self._exists(old_name) or self._exists(new_name):
            return False
        items = self._items
        items[items.index(old_name)] = new_name
        for course in self._cfg.courses:
            old_list = getattr(course, self._course_attr)
            setattr(
                course,
                self._course_attr,
                [new_name if x == old_name else x for x in old_list],
            )
        for faculty in self._cfg.faculty:
            prefs = getattr(faculty, self._pref_attr)
            if old_name in prefs:
                prefs[new_name] = prefs.pop(old_name)
        return True

    def _get_all(self) -> list[str]:
        return self._items

    def _get_affected_courses(self, name: str) -> list:
        return [c for c in self._cfg.courses if name in getattr(c, self._course_attr)]

    def _get_affected_faculty(self, name: str) -> list:
        return [f for f in self._cfg.faculty if name in getattr(f, self._pref_attr)]

    # ------------------------------------------------------------------
    # Public API shared by all subclasses
    # ------------------------------------------------------------------

    def get_affected_courses(self, name: str) -> list:
        return self._get_affected_courses(name)

    def get_affected_faculty(self, name: str) -> list:
        return self._get_affected_faculty(name)
