# scheduler_facade.py
"""
SchedulerFacade - Facade design pattern for schedule generation.

Wraps the multi-step schedule generation pipeline (config validation,
Scheduler construction, model iteration, result collection) behind one
clean method: generate(). 

The optional progress_callback(percent: int, message: str) hook lets any
caller — the GUI, a CLI, a test — receive live progress updates without
knowing anything about the internals.

Design pattern: Facade
  - Hides: ConfigModel, SchedulerModel, Scheduler, generate_schedules()
  - Exposes: SchedulerFacade.generate(limit, progress_callback)
"""

from __future__ import annotations

from typing import Callable

ProgressCallback = Callable[[int, str], None]


class SchedulerFacade:
    """
    Facade over the schedule generation subsystem.

    Accepts an existing SchedulerModel so it slots directly into the
    MVC setup with zero duplicate model construction.

    Usage (from schedule_gui_view.py / on_generate):
        facade = SchedulerFacade(_state._scheduler_model)
        schedules = facade.generate(
            limit=50,
            progress_callback=lambda pct, msg: ...,
        )
    """

    def __init__(self, scheduler_model) -> None:
        """
        Parameters:
            scheduler_model (SchedulerModel): Fully initialised model
                that owns a ConfigModel and exposes generate_schedules().
        """
        self._model = scheduler_model

    # ------------------------------------------------------------------
    # Public facade interface
    # ------------------------------------------------------------------

    def generate(
        self,
        limit: int = 1,
        progress_callback: ProgressCallback | None = None,
    ) -> list[list]:
        """
        Run the full schedule generation pipeline.

        Progress milestones reported via callback:
          0  % — starting
         10  % — validation passed
         25  % — scheduler ready
         40  % — iteration begun
         40-95% — incremental per-schedule
         100 % — complete

        Parameters:
            limit (int): Maximum number of schedules to generate.
            progress_callback (ProgressCallback | None): Called as
                (percent: int, message: str) at each milestone.

        Returns:
            list[list]: Flat list of schedule objects (each a list of
                CourseInstance), same shape as generate_schedules().

        Raises:
            RuntimeError: If no model or config is loaded.
            Exception: Any scheduler error propagates to the caller.
        """

        def report(pct: int, msg: str) -> None:
            if progress_callback:
                progress_callback(pct, msg)

        report(0, "Starting schedule generation…")

        # Step 1 — validate
        report(10, "Validating configuration…")
        self._validate()

        # Step 2 — apply limit to config so Scheduler respects it
        report(25, "Preparing scheduler…")
        self._model.config_model.config.limit = limit

        # Step 3 — kick off generation
        report(40, "Running scheduler…")
        raw = self._model.generate_schedules(limit=limit)

        # Step 4 — collect with incremental progress
        schedules: list[list] = []
        for schedule in raw:
            schedules.append(schedule)
            n = len(schedules)
            pct = 40 + int(55 * min(n / max(limit, 1), 1.0))
            report(pct, f"Collected {n} schedule(s)…")

        report(100, f"Done — {len(schedules)} schedule(s) generated.")
        return schedules

    # ------------------------------------------------------------------
    # Private subsystem helpers hidden by the Facade
    # ------------------------------------------------------------------

    def _validate(self) -> None:
        """
        Raise RuntimeError if the model is not ready to generate.

        Parameters:
            None
        Returns:
            None
        Raises:
            RuntimeError: If scheduler_model or config_model is None.
        """
        if self._model is None:
            raise RuntimeError("No scheduler model provided.")
        if getattr(self._model, "config_model", None) is None:
            raise RuntimeError(
                "No configuration loaded. Load a config file before generating."
            )