# controllers/chatbot_controller.py
"""
ChatbotController - LangChain AI assistant for the Scheduler application.
Exposes labs, rooms, courses, faculty, and conflicts to a ReAct agent via structured tools.
Design pattern: Implemented the decorator pattern by using wraps and having @requires_config
    be at the top of each function that needs it instead of having the code in every function.
"""

import asyncio
import difflib
import logging
from functools import wraps

from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain.agents import create_agent
from pydantic import BaseModel, Field
from scheduler import CourseConfig, FacultyConfig
from scheduler.config import TimeRange

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a scheduling configuration assistant for a university course scheduler.

Your job is to help users manage the configuration by executing commands using your tools.

You can:
- Add, delete, or rename LABS (e.g. "Mac Lab", "Linux Lab")
- Add, delete, or rename ROOMS (e.g. "Roddy 136")
- Add, delete, or modify COURSES (e.g. "CMSC 340")
- Add, delete, or modify FACULTY members
- Add, delete, or modify CONFLICTS between courses
- List all labs, rooms, courses, faculty, and conflicts

Rules:
- Always use a tool to fulfill a request. Do not make up results.
- Always relay the tool's exact output to the user — never paraphrase or summarize it.
- Be brief outside of tool output. Confirm success in one sentence or explain failure simply.
- Any request to list or show faculty must call the get_faculty tool, which shows names only and asks if the user wants details.
- Only call get_faculty_details when the user explicitly asks for more info about a specific faculty member.
- Any request to list or show courses must call the get_courses tool, which shows course IDs only and asks if the user wants details.
- Only call get_course_details when the user explicitly asks for more info about a specific course.
- When adding a course, ask the user for: course ID, credits, acceptable rooms (comma-separated), acceptable labs (comma-separated, can be empty), and faculty (comma-separated, can be empty).
- When adding faculty, ask for: name, position (full time or adjunct), max days (default 5), and availability times in the format "MON:08:00-17:00,WED:08:00-17:00".
- Valid days are: MON, TUE, WED, THU, FRI.
- All changes are in-memory only. Remind the user to press the Export to Config button to save changes to disk.
- If the user asks for something outside your capabilities, say so clearly.
"""


class _AddOrRemoveSchema(BaseModel):
    name: str = Field(description="The name")


class _RenameSchema(BaseModel):
    old_name: str = Field(description="The current name")
    new_name: str = Field(description="The new name")


class _GetSchema(BaseModel):
    pass


class _AddCourseSchema(BaseModel):
    course_id: str = Field(description="Course ID (e.g. 'CMSC 340')")
    credits: int = Field(description="Number of credit hours")
    rooms: str = Field(
        description="Comma-separated list of acceptable room names (e.g. 'Roddy 136,Roddy 205')"
    )
    labs: str = Field(
        description="Comma-separated list of acceptable lab names, or empty string if none"
    )
    faculty: str = Field(
        description="Comma-separated list of faculty names, or empty string if none"
    )


class _DeleteCourseSchema(BaseModel):
    course_id: str = Field(description="Course ID to delete")


class _ModifyCourseSchema(BaseModel):
    course_id: str = Field(description="Course ID to modify")
    field: str = Field(
        description="Field to modify: 'credits', 'room', 'lab', or 'faculty'"
    )
    value: str = Field(
        description="New value. For credits: a number. For room/lab/faculty: comma-separated list."
    )


class _AddFacultySchema(BaseModel):
    name: str = Field(description="Faculty member's name")
    is_full_time: bool = Field(
        description="True if the faculty is full time, False if adjunct"
    )
    max_days: int = Field(
        default=5, description="Maximum days per week they can teach (0-5)"
    )
    times: str = Field(
        description="Availability times in format 'MON:08:00-17:00,WED:09:00-18:00'"
    )


class _DeleteFacultySchema(BaseModel):
    name: str = Field(description="Faculty member's name to delete")


class _ModifyFacultySchema(BaseModel):
    name: str = Field(description="Faculty member's name")
    field: str = Field(
        description="Field to modify: 'maximum_credits', 'minimum_credits', 'unique_course_limit', or 'maximum_days'"
    )
    value: int = Field(description="New integer value for the field")


class _CourseDetailsSchema(BaseModel):
    course_id: str = Field(description="Course ID to get details for")


class _FacultyDetailsSchema(BaseModel):
    name: str = Field(description="Faculty member's name to get details for")


class _ConflictSchema(BaseModel):
    course_id_1: str = Field(description="First course ID")
    course_id_2: str = Field(description="Second course ID")


class _ModifyConflictSchema(BaseModel):
    old_course_id_1: str = Field(description="Current first course ID in the conflict")
    old_course_id_2: str = Field(description="Current second course ID in the conflict")
    new_course_id_1: str = Field(description="New first course ID")
    new_course_id_2: str = Field(description="New second course ID")


def requires_config(func):
    """
    Decorator that checks if a configuration is loaded before executing a tool method.

    If no configuration is loaded, returns an early message to the user
    instead of calling the wrapped function.

    Parameters:
        func: The tool method to wrap.
    Returns:
        The wrapped function.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self._no_config():
            return "No configuration loaded."
        return func(self, *args, **kwargs)

    return wrapper


class ChatbotController:
    """
    Wraps LangChain ReAct agent with tools bound to the scheduler's models.

    Attributes:
        lab_model: LabModel instance (may be None if no config loaded)
        room_model: RoomModel instance
        course_model: CourseModel instance
        faculty_model: FacultyModel instance
        conflict_model: ConflictModel instance
    """

    def __init__(
        self, lab_model, room_model, course_model, faculty_model, conflict_model
    ):
        self.lab_model = lab_model
        self.room_model = room_model
        self.course_model = course_model
        self.faculty_model = faculty_model
        self.conflict_model = conflict_model
        self._agent = None

    def _no_config(self) -> bool:
        return self.lab_model is None

    def save_config(self) -> bool:
        """Persist all in-memory changes to the config file on disk."""
        try:
            return self.lab_model.config_model.safe_save()
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}", exc_info=True)
            return False

    # ── Lab tools ────────────────────────────────────────────────────────────

    @requires_config
    def _add_lab(self, name: str) -> str:
        result = (
            f"Lab '{name}' added."
            if self.lab_model.add_lab(name)
            else f"Failed to add lab '{name}' (may already exist)."
        )
        return result

    @requires_config
    def _delete_lab(self, name: str) -> str:
        return (
            f"Lab '{name}' deleted."
            if self.lab_model.delete_lab(name)
            else f"Failed to delete lab '{name}'."
        )

    @requires_config
    def _rename_lab(self, old_name: str, new_name: str) -> str:
        return (
            f"Lab renamed from '{old_name}' to '{new_name}'."
            if self.lab_model.modify_lab(old_name, new_name)
            else f"Failed to rename lab '{old_name}'."
        )

    @requires_config
    def _get_labs(self) -> str:
        labs = self.lab_model.get_all_labs()
        return ("Labs: " + ", ".join(labs)) if labs else "No labs configured."

    # ── Room tools ───────────────────────────────────────────────────────────

    @requires_config
    def _suggest_room(self, name: str) -> str:
        rooms = self.room_model.get_all_rooms()
        matches = difflib.get_close_matches(name, rooms, n=1, cutoff=0.6)
        if matches:
            return f" Did you mean '{matches[0]}'"
        return ""

    @requires_config
    def _add_room(self, name: str) -> str:
        return (
            f"Room '{name}' added."
            if self.room_model.add_room(name)
            else f"Failed to add room '{name}' (may already exist)."
        )

    @requires_config
    def _delete_room(self, name: str) -> str:
        if self.room_model.delete_room(name):
            return f"Room '{name}' deleted"
        return f"Failed to delete room '{name}' (not found).{self._suggest_room(name)}"

    @requires_config
    def _rename_room(self, old_name: str, new_name: str) -> str:
        return (
            f"Room renamed from '{old_name}' to '{new_name}'."
            if self.room_model.modify_room(old_name, new_name)
            else f"Failed to rename room '{old_name}' (not found).{self._suggest_room(old_name)}."
        )

    @requires_config
    def _get_rooms(self) -> str:
        rooms = self.room_model.get_all_rooms()
        return ("Rooms: " + ", ".join(rooms)) if rooms else "No rooms configured."

    # ── Course tools ─────────────────────────────────────────────────────────

    @requires_config
    def _add_course(
        self, course_id: str, credits: int, rooms: str, labs: str, faculty: str
    ) -> str:
        try:
            room_list = [r.strip() for r in rooms.split(",") if r.strip()]
            lab_list = [lab.strip() for lab in labs.split(",") if lab.strip()]
            faculty_list = [f.strip() for f in faculty.split(",") if f.strip()]

            existing_rooms = set(self.room_model.get_all_rooms())
            invalid_rooms = [r for r in room_list if r not in existing_rooms]
            if invalid_rooms:
                return (
                    f"Failed to add course '{course_id}': the following rooms do not exist: "
                    f"{', '.join(invalid_rooms)}. Valid rooms: {', '.join(sorted(existing_rooms)) or 'none'}."
                )

            existing_labs = set(self.lab_model.get_all_labs())
            invalid_labs = [lab for lab in lab_list if lab not in existing_labs]
            if invalid_labs:
                return (
                    f"Failed to add course '{course_id}': the following labs do not exist: "
                    f"{', '.join(invalid_labs)}. Valid labs: {', '.join(sorted(existing_labs)) or 'none'}."
                )

            existing_faculty = {f.name for f in self.faculty_model.get_all_faculty()}
            invalid_faculty = [f for f in faculty_list if f not in existing_faculty]
            if invalid_faculty:
                return (
                    f"Failed to add course '{course_id}': the following faculty do not exist: "
                    f"{', '.join(invalid_faculty)}. Valid faculty: {', '.join(sorted(existing_faculty)) or 'none'}."
                )

            course = CourseConfig(
                course_id=course_id,
                credits=credits,
                room=room_list,
                lab=lab_list,
                conflicts=[],
                faculty=faculty_list,
            )
            self.course_model.add_course(course)
            return f"Course '{course_id}' added."
        except Exception as e:
            return f"Failed to add course '{course_id}': {e}"

    @requires_config
    def _delete_course(self, course_id: str) -> str:
        return (
            f"Course '{course_id}' deleted."
            if self.course_model.delete_course(course_id)
            else f"Failed to delete course '{course_id}' (not found)."
        )

    @requires_config
    def _modify_course(self, course_id: str, field: str, value: str) -> str:
        valid_fields = {"credits", "room", "lab", "faculty"}
        if field not in valid_fields:
            return f"Invalid field '{field}'. Valid fields: {', '.join(sorted(valid_fields))}."
        try:
            if field == "credits":
                update = {"credits": int(value)}
            else:
                update = {field: [v.strip() for v in value.split(",") if v.strip()]}
            ok = self.course_model.modify_course(course_id, **update)
            if ok:
                return f"Course '{course_id}' field '{field}' updated."
            return f"Failed to modify course '{course_id}' (not found)."
        except Exception as e:
            return f"Failed to modify course '{course_id}': {e}"

    @requires_config
    def _get_courses(self) -> str:
        courses = self.course_model.get_all_courses()
        if not courses:
            return "No courses configured."
        ids = ", ".join(dict.fromkeys(c.course_id for c in courses))
        return (
            f"Courses: {ids}\n\nWould you like detailed information about any of them?"
        )

    @requires_config
    def _get_course_details(self, course_id: str) -> str:
        course = self.course_model.get_course_by_id(course_id)
        if course is None:
            return f"Course '{course_id}' not found."
        rooms = ", ".join(course.room) if course.room else "none"
        labs = ", ".join(course.lab) if course.lab else "none"
        faculty = ", ".join(course.faculty) if course.faculty else "none"
        conflicts = ", ".join(course.conflicts) if course.conflicts else "none"
        return (
            f"{course.course_id}: {course.credits} credits | rooms: {rooms} | "
            f"labs: {labs} | faculty: {faculty} | conflicts: {conflicts}"
        )

    # ── Faculty tools ─────────────────────────────────────────────────────────

    @requires_config
    def _suggest_faculty(self, name: str) -> str:
        faculty = self.faculty_model.get_all_faculty()
        names = [f.name for f in faculty]
        matches = difflib.get_close_matches(name, names, n=1, cutoff=0.6)
        if matches:
            return f"Did you mean '{matches[0]}'?"
        return ""

    @staticmethod
    def _parse_times(times_str: str) -> dict:
        """Parse 'MON:08:00-17:00,WED:09:00-18:00' into FacultyConfig times dict."""
        result = {}
        for part in times_str.split(","):
            part = part.strip()
            if ":" not in part:
                continue
            day, time_range = part.split(":", 1)
            day = day.strip().upper()
            start, end = time_range.strip().split("-")
            result.setdefault(day, []).append(
                TimeRange(start=start.strip(), end=end.strip())
            )
        return result

    @requires_config
    def _add_faculty(
        self,
        name: str,
        is_full_time: bool,
        max_days: int,
        times: str,
    ) -> str:
        try:
            times_dict = self._parse_times(times)
            if not times_dict:
                return "Failed: times string is invalid. Use format 'MON:08:00-17:00,WED:09:00-18:00'."

            from models.faculty_model import (
                FULL_TIME_MAX_CREDITS,
                ADJUNCT_MAX_CREDITS,
                FULL_TIME_UNIQUE_COURSE_LIMIT,
                ADJUNCT_UNIQUE_COURSE_LIMIT,
                MIN_CREDITS,
            )

            if is_full_time:
                max_credits = FULL_TIME_MAX_CREDITS
                unique_course_limit = FULL_TIME_UNIQUE_COURSE_LIMIT
            else:
                max_credits = ADJUNCT_MAX_CREDITS
                unique_course_limit = ADJUNCT_UNIQUE_COURSE_LIMIT

            faculty = FacultyConfig(
                name=name,
                maximum_credits=max_credits,
                minimum_credits=MIN_CREDITS,
                unique_course_limit=unique_course_limit,
                maximum_days=max_days,
                times=times_dict,
            )
            ok = self.faculty_model.add_faculty(faculty)
            if ok:
                return f"Faculty '{name}' added."
            return f"Failed to add faculty '{name}' (may already exist)."
        except Exception as e:
            return f"Failed to add faculty '{name}': {e}"

    @requires_config
    def _delete_faculty(self, name: str) -> str:
        if self.faculty_model.delete_faculty(name):
            return f"Faculty '{name}' deleted"
        return f"Failed to delete faculty '{name}' (not found).{self._suggest_faculty(name)}"

    @requires_config
    def _modify_faculty(self, name: str, field: str, value: int) -> str:
        valid_fields = {
            "maximum_credits",
            "minimum_credits",
            "unique_course_limit",
            "maximum_days",
        }
        if field not in valid_fields:
            return f"Invalid field '{field}'. Valid fields: {', '.join(sorted(valid_fields))}."
        ok = self.faculty_model.modify_faculty(name, field, value)
        if ok:
            return f"Faculty '{name}' field '{field}' updated to {value}."
        return f"Failed to modify faculty '{name}' (not found)."

    @requires_config
    def _get_faculty(self) -> str:
        faculty = self.faculty_model.get_all_faculty()
        if not faculty:
            return "No faculty configured."
        names = ", ".join(f.name for f in faculty)
        return f"Faculty: {names}\n\nWould you like detailed information about any of them?"

    @requires_config
    def _get_faculty_details(self, name: str) -> str:
        f = self.faculty_model.get_faculty_by_name(name)
        if f is None:
            return f"Faculty '{name}' not found."
        days = ", ".join(f.times.keys())
        return (
            f"{f.name}: max {f.maximum_credits} cr, min {f.minimum_credits} cr, "
            f"unique courses: {f.unique_course_limit}, max days: {f.maximum_days}, "
            f"available days: {days}"
        )

    # ── Conflict tools ────────────────────────────────────────────────────────

    @requires_config
    def _add_conflict(self, course_id_1: str, course_id_2: str) -> str:
        ok = self.conflict_model.add_conflict(course_id_1, course_id_2)
        if ok:
            return f"Conflict added between '{course_id_1}' and '{course_id_2}'."
        return (
            "Failed to add conflict (courses may not exist or conflict already exists)."
        )

    @requires_config
    def _delete_conflict(self, course_id_1: str, course_id_2: str) -> str:
        ok = self.conflict_model.delete_conflict(course_id_1, course_id_2)
        if ok:
            return f"Conflict removed between '{course_id_1}' and '{course_id_2}'."
        return "Failed to remove conflict (may not exist)."

    @requires_config
    def _modify_conflict(
        self,
        old_course_id_1: str,
        old_course_id_2: str,
        new_course_id_1: str,
        new_course_id_2: str,
    ) -> str:
        ok = self.conflict_model.modify_conflict_by_ids(
            old_course_id_1, old_course_id_2, new_course_id_1, new_course_id_2
        )
        if ok:
            return f"Conflict updated: '{new_course_id_1}' <-> '{new_course_id_2}'."
        return (
            "Failed to modify conflict (courses may not exist or conflict not found)."
        )

    @requires_config
    def _get_conflicts(self) -> str:
        conflicts = self.conflict_model.get_all_conflicts()
        if not conflicts:
            return "No conflicts configured."
        lines = [f"  {c1} <-> {c2}" for c1, c2, _, _ in conflicts]
        return "Conflicts:\n" + "\n".join(lines)

    # ── Agent setup ──────────────────────────────────────────────────────────

    def _build_agent(self):
        model = ChatOpenAI(model_name="gpt-5-mini")
        tools = [
            # Labs
            StructuredTool.from_function(
                name="add_lab",
                func=self._add_lab,
                description="Add a new lab",
                args_schema=_AddOrRemoveSchema,
            ),
            StructuredTool.from_function(
                name="delete_lab",
                func=self._delete_lab,
                description="Delete a lab",
                args_schema=_AddOrRemoveSchema,
            ),
            StructuredTool.from_function(
                name="rename_lab",
                func=self._rename_lab,
                description="Rename a lab",
                args_schema=_RenameSchema,
            ),
            StructuredTool.from_function(
                name="get_labs",
                func=self._get_labs,
                description="List all labs",
                args_schema=_GetSchema,
            ),
            # Rooms
            StructuredTool.from_function(
                name="add_room",
                func=self._add_room,
                description="Add a new room",
                args_schema=_AddOrRemoveSchema,
            ),
            StructuredTool.from_function(
                name="delete_room",
                func=self._delete_room,
                description="Delete a room",
                args_schema=_AddOrRemoveSchema,
            ),
            StructuredTool.from_function(
                name="rename_room",
                func=self._rename_room,
                description="Rename a room",
                args_schema=_RenameSchema,
            ),
            StructuredTool.from_function(
                name="get_rooms",
                func=self._get_rooms,
                description="List all rooms",
                args_schema=_GetSchema,
            ),
            # Courses
            StructuredTool.from_function(
                name="add_course",
                func=self._add_course,
                description="Add a new course",
                args_schema=_AddCourseSchema,
            ),
            StructuredTool.from_function(
                name="delete_course",
                func=self._delete_course,
                description="Delete a course by ID",
                args_schema=_DeleteCourseSchema,
            ),
            StructuredTool.from_function(
                name="modify_course",
                func=self._modify_course,
                description="Modify a course field (credits, room, lab, faculty)",
                args_schema=_ModifyCourseSchema,
            ),
            StructuredTool.from_function(
                name="get_courses",
                func=self._get_courses,
                description="List all course IDs",
                args_schema=_GetSchema,
            ),
            StructuredTool.from_function(
                name="get_course_details",
                func=self._get_course_details,
                description="Get detailed info for a specific course by ID",
                args_schema=_CourseDetailsSchema,
            ),
            # Faculty
            StructuredTool.from_function(
                name="add_faculty",
                func=self._add_faculty,
                description="Add a new faculty member",
                args_schema=_AddFacultySchema,
            ),
            StructuredTool.from_function(
                name="delete_faculty",
                func=self._delete_faculty,
                description="Delete a faculty member by name",
                args_schema=_DeleteFacultySchema,
            ),
            StructuredTool.from_function(
                name="modify_faculty",
                func=self._modify_faculty,
                description="Modify a faculty field (maximum_credits, minimum_credits, unique_course_limit, maximum_days)",
                args_schema=_ModifyFacultySchema,
            ),
            StructuredTool.from_function(
                name="get_faculty",
                func=self._get_faculty,
                description="List all faculty names",
                args_schema=_GetSchema,
            ),
            StructuredTool.from_function(
                name="get_faculty_details",
                func=self._get_faculty_details,
                description="Get detailed info for a specific faculty member by name",
                args_schema=_FacultyDetailsSchema,
            ),
            # Conflicts
            StructuredTool.from_function(
                name="add_conflict",
                func=self._add_conflict,
                description="Add a conflict between two courses",
                args_schema=_ConflictSchema,
            ),
            StructuredTool.from_function(
                name="delete_conflict",
                func=self._delete_conflict,
                description="Remove a conflict between two courses",
                args_schema=_ConflictSchema,
            ),
            StructuredTool.from_function(
                name="modify_conflict",
                func=self._modify_conflict,
                description="Replace one or both courses in an existing conflict pair",
                args_schema=_ModifyConflictSchema,
            ),
            StructuredTool.from_function(
                name="get_conflicts",
                func=self._get_conflicts,
                description="List all course conflicts",
                args_schema=_GetSchema,
            ),
        ]
        return create_agent(model, tools)

    async def chat(self, query: str, history: list[dict] | None = None) -> str:
        """
        Send a query to the agent and return the response text.

        Runs the blocking LangChain call in a thread to avoid blocking NiceGUI's event loop.

        Parameters:
            query: The current user message.
            history: Prior turns as list of {'role': 'user'|'ai', 'content': str}.
        """
        if self._agent is None:
            self._agent = self._build_agent()

        messages: list[BaseMessage] = [SystemMessage(content=SYSTEM_PROMPT)]
        for turn in history or []:
            if turn["role"] == "user":
                messages.append(HumanMessage(content=turn["content"]))
            else:
                messages.append(AIMessage(content=turn["content"]))
        messages.append(HumanMessage(content=query))

        result = await asyncio.to_thread(self._agent.invoke, {"messages": messages})

        for msg in reversed(result["messages"]):
            content = getattr(msg, "content", None)
            if content and isinstance(content, str):
                return content

        return "No response."
