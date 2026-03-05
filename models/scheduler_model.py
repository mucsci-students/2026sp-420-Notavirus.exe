# models/scheduler_model.py
"""
SchedulerModel - Handles schedule generation operations

This model class manages schedule generation using the Scheduler class.
"""

import scheduler
import csv
import json
import io
from scheduler import Scheduler
from scheduler.models import CourseInstance, TimeInstance, TimePoint, Day, Duration, Course, TimeSlot


class SchedulerModel:
    """
    Model class for schedule generation operations.
    
    Attributes:
        config_model: Reference to ConfigModel for configuration access
    """
    
    def __init__(self, config_model):
        """
        Initialize SchedulerModel.
        
        Parameters:
            config_model (ConfigModel): Central configuration model
        
        Returns:
            None
        """
        self.config_model = config_model
    
    def generate_schedules(self, limit: int = None):
        """
        Generate schedules using the Scheduler.
        
        Parameters:
            limit (int | None): Maximum number of schedules to generate
        
        Returns:
            generator: Generator yielding schedule models
        """
        # Set limit if provided
        if limit is not None:
            self.config_model.config.limit = limit
        
        # Create scheduler and generate
        scheduler_gen = Scheduler(self.config_model.config)
        return scheduler_gen.get_models()
    
    def count_possible_schedules(self, max_check: int = 100) -> int:
        """
        Count how many schedules can be generated (up to max_check).
        
        Parameters:
            max_check (int): Maximum schedules to check
        
        Returns:
            int: Number of schedules found (up to max_check)
        """
        count = 0
        try:
            for _ in self.generate_schedules(limit=max_check):
                count += 1
        except Exception:
            pass
        
        return count

    def _build_dummy_course(self, course_str: str, faculty: str | None = None, lab: str | None = None):
        """
        Build synthetic Course object for imported schedules.

        Required because CourseInstance expects a Course reference.

        Safe defaults are used for solver-related fields.
        """

        if not course_str:
            course_id = "UNKNOWN"
            section = 1
        else:
            if "." in course_str:
                course_id, section_str = course_str.rsplit(".", 1)
                try:
                    section = int(section_str)
                except ValueError:
                    section = 1
            else:
                course_id = course_str
                section = 1

        return Course(
            course_id=course_id,
            credits=0,
            section=section,
            labs=[lab] if lab else [],
            rooms=[],
            conflicts=[],
            faculties=[faculty] if faculty else [],
        )
    def _build_time_instance(self, t: dict):
        """
        Convert JSON time dictionary into TimeInstance object.
        """

        day_value = t["day"]

        return TimeInstance(
            day=Day(day_value),
            start=TimePoint(timepoint=t["start"]),
            duration=Duration(duration=t["duration"])
        )
    

    def import_from_csv(self, file_bytes: bytes):
        """
        Import schedule CSV in format:
        <course>,<faculty>,<room>,<lab>,<times...>

        Returns list[list[CourseInstance]]
        """

        text = file_bytes.decode("utf-8")
        reader = csv.reader(io.StringIO(text))

        schedules = []
        schedule = []

        for row in reader:

        # ---- Empty line means new schedule ----
            if not row or all(cell.strip() == "" for cell in row):
                if schedule:
                    schedules.append(schedule)
                    schedule = []
                continue

            course_str = row[0]
            faculty = row[1]
            room = row[2]
            lab = row[3]

            # Convert "None" string to actual None
            if lab == "None":
                lab = None

            # Remaining columns are time strings
            time_strings = row[4:]

            times = []
            day_map = {
                "MON": 1,
                "TUE": 2,
                "WED": 3,
                "THU": 4,
                "FRI": 5,
            }

            lab_index = None

            for idx, t in enumerate(time_strings):
                # Check if this is the lab time
                is_lab = t.endswith("^")
                if is_lab:
                    t = t.rstrip("^")
                    lab_index = idx  # mark the lab index
                # Example format: "MON 09:00-09:50"
                day_part, time_part = t.split(" ")
                start_str, end_str = time_part.split("-")
                            # ---- Convert start time ----
                start_hr, start_min = map(int, start_str.split(":"))
                start_tp = TimePoint.make_from(start_hr, start_min)

                # ---- Convert end time ----
                end_hr, end_min = map(int, end_str.split(":"))
                end_tp = TimePoint.make_from(end_hr, end_min)

                time_instance = self._build_time_instance({
                    "day": day_map.get(day_part.upper()),
                    "start": start_tp.value,
                    "duration": end_tp.value - start_tp.value
                })

                times.append(time_instance)

            dummy_course = self._build_dummy_course(
                course_str,
                faculty=faculty
            )

            ci = CourseInstance(
                course=dummy_course,
                time=TimeSlot(
                    times=times,
                    lab_index=lab_index
                ),
                faculty=faculty,
                room=room,
                lab=lab
                
            )

            schedule.append(ci)

        # ---- Add final schedule if file doesn't end with empty line ----
        if schedule:
            schedules.append(schedule)

        return schedules

    
    def export_to_csv(self, schedules: list[list]):
        """
        Export schedules using CourseInstance.as_csv().
        Multiple schedules are separated by a blank line.
        Returns: bytes
        """

        output = io.StringIO()

        for schedule_index, schedule in enumerate(schedules):

            for ci in schedule:
                output.write(ci.as_csv() + "\n")

            # Separate schedules with blank line
            if schedule_index < len(schedules) - 1:
                output.write("\n")

        return output.getvalue().encode("utf-8")
    
    def import_from_json(self, file_bytes: bytes):
        """
        Import schedule JSON exported via model_dump().
        Returns list[list[CourseInstance]].
        """

        text = file_bytes.decode("utf-8")
        raw_schedules = json.loads(text)

        schedules = []

        for schedule_data in raw_schedules:

            schedule = []

            for ci_data in schedule_data:
                print("building time instances")
                #times is the days + duration + start time 
                times = [
                    self._build_time_instance(t)
                    for t in ci_data.get("times", [])
                ]

                course_str = ci_data.get("course_str")
                print("building dummy course instances")
                dummy_course = self._build_dummy_course(
                    course_str,
                    faculty=ci_data.get("faculty")
                )
                print("building instances done")
                #need to make course instances for EVERY time in times[]
                
                ci = CourseInstance(
                    course=dummy_course,
                    time=TimeSlot(times=times, lab_index=ci_data.get("lab_index")),
                    faculty=ci_data.get("faculty"),
                    room=ci_data.get("room"),
                    lab=ci_data.get("lab")
                )
                schedule.append(ci)

            schedules.append(schedule)
        print("returning schedules as list[list[CourseInstance]]")
        return schedules


    def export_to_json(self, schedules: list[list]):
        """
        Export generated/imported schedules to JSON.
        Each schedule is a list of CourseInstance objects.
        Returns bytes for browser download.
        """

        schedule_list = []

        for schedule in schedules:
            json_schedule = []

            for course in schedule:

                # Prefer object serialization if available
                if hasattr(course, "as_dict"):
                    json_data = course.as_dict()
                else:
                    json_data = course.model_dump()

                json_schedule.append(json_data)

            schedule_list.append(json_schedule)

        return json.dumps(schedule_list, indent=2).encode("utf-8")