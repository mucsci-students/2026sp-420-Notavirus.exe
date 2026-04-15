# views/pdf_export.py
"""
PDF export for schedules.

Reuses the calendar-building helpers from schedule_gui_view to avoid
duplicating data-extraction logic.  The lazy import of schedule_gui_view
(inside the function) avoids a circular import at module load time.
"""

import io


def generate_pdf(schedules: list[list]) -> bytes:
    """
    Render *schedules* as a black-and-white PDF calendar grid.

    One page per location (room / lab) per schedule.
    Returns bytes suitable for a browser download.
    """
    try:
        from reportlab.lib.pagesizes import landscape, letter
        from reportlab.pdfgen import canvas as pdf_canvas
        from reportlab.lib.colors import black, HexColor
    except ImportError:
        raise ImportError(
            "reportlab is required for PDF export. Install with: pip install reportlab"
        )

    # Lazy import avoids circular dependency (schedule_gui_view imports nothing
    # from here; we import from it only at call time).
    from views.schedule_gui_view import (
        _build_calendar_grid_by_room,
        _extract_calendar_metadata,
        _extract_time_range,
    )

    buffer = io.BytesIO()

    PAGE_W, PAGE_H = landscape(letter)  # 792 x 612 pt
    MARGIN = 36
    TIME_COL_W = 48
    TITLE_H = 24
    HEADER_H = 18

    c = pdf_canvas.Canvas(buffer, pagesize=landscape(letter))

    for sched_idx, schedule in enumerate(schedules):
        calendar_data = _build_calendar_grid_by_room(schedule)
        sorted_days, hourly_slots = _extract_calendar_metadata(schedule)

        if not calendar_data or not sorted_days:
            continue

        # Determine hour range from the hourly slots already computed
        min_hour, max_hour = 7, 20
        if hourly_slots:
            try:
                min_hour = int(hourly_slots[0].split(":")[0])
                max_hour = int(hourly_slots[-1].split(":")[0]) + 1
            except Exception:
                pass
        min_hour = max(0, min_hour - 1)
        max_hour = min(24, max_hour + 1)
        num_hours = max_hour - min_hour

        n_days = len(sorted_days)
        avail_w = PAGE_W - 2 * MARGIN
        grid_h = PAGE_H - 2 * MARGIN - TITLE_H - HEADER_H
        hour_h = min(60.0, max(28.0, grid_h / num_hours))
        day_col_w = (avail_w - TIME_COL_W) / n_days

        for location in sorted(calendar_data.keys()):

            def rl_y(top_offset: float) -> float:
                """Top-relative offset → ReportLab y (origin = bottom-left)."""
                return PAGE_H - MARGIN - top_offset

            # ── Title ─────────────────────────────────────────────────────────
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(black)
            c.drawString(MARGIN, rl_y(TITLE_H - 6), location)
            if len(schedules) > 1:
                c.setFont("Helvetica", 9)
                c.drawString(
                    MARGIN + 200, rl_y(TITLE_H - 6), f"Schedule {sched_idx + 1}"
                )

            c.setStrokeColor(black)
            c.setLineWidth(0.5)
            c.line(MARGIN, rl_y(TITLE_H), PAGE_W - MARGIN, rl_y(TITLE_H))

            # ── Day headers ───────────────────────────────────────────────────
            c.setFont("Helvetica-Bold", 9)
            for i, day in enumerate(sorted_days):
                x = MARGIN + TIME_COL_W + i * day_col_w
                c.drawCentredString(
                    x + day_col_w / 2, rl_y(TITLE_H + HEADER_H - 5), day
                )
            c.line(
                MARGIN,
                rl_y(TITLE_H + HEADER_H),
                PAGE_W - MARGIN,
                rl_y(TITLE_H + HEADER_H),
            )

            # ── Hour grid ─────────────────────────────────────────────────────
            grid_top = TITLE_H + HEADER_H
            grid_top_y = rl_y(grid_top)
            grid_bottom_y = rl_y(grid_top + num_hours * hour_h)

            for h_idx in range(num_hours + 1):
                row_y = rl_y(grid_top + h_idx * hour_h)
                c.setLineWidth(0.3)
                c.line(MARGIN, row_y, PAGE_W - MARGIN, row_y)
                if h_idx < num_hours:
                    c.setFont("Helvetica", 7)
                    c.setFillColor(black)
                    c.drawString(MARGIN + 2, row_y - 9, f"{min_hour + h_idx:02d}:00")

            c.line(MARGIN, grid_top_y, MARGIN, grid_bottom_y)
            for i in range(n_days + 1):
                x = MARGIN + TIME_COL_W + i * day_col_w
                c.setLineWidth(0.3)
                c.line(x, grid_top_y, x, grid_bottom_y)

            # ── Course blocks ─────────────────────────────────────────────────
            min_hour_min = min_hour * 60
            location_data = calendar_data.get(location, {})

            for day_idx, day in enumerate(sorted_days):
                day_x = MARGIN + TIME_COL_W + day_idx * day_col_w

                # Deduplicate courses that span multiple hourly buckets
                seen: set[tuple] = set()
                courses_for_day = []
                for hour_slot in hourly_slots:
                    for course_info in location_data.get(day, {}).get(hour_slot, []):
                        key = (course_info["full_course_str"], course_info["faculty"])
                        if key not in seen:
                            seen.add(key)
                            courses_for_day.append(course_info)

                for course_info in courses_for_day:
                    time_str = course_info.get("time_str", "")
                    if not time_str:
                        continue

                    time_range = _extract_time_range(time_str)
                    if not time_range:
                        continue

                    (sh, sm), (eh, em) = time_range
                    start_min = sh * 60 + sm
                    end_min = eh * 60 + em

                    top_px = (start_min - min_hour_min) / 60.0 * hour_h
                    height_px = max(16.0, (end_min - start_min) / 60.0 * hour_h)
                    block_bottom = rl_y(grid_top + top_px + height_px)
                    block_top_y = rl_y(grid_top + top_px)

                    # Light gray filled rectangle
                    c.setFillColor(HexColor("#eeeeee"))
                    c.setStrokeColor(black)
                    c.setLineWidth(0.6)
                    c.rect(
                        day_x + 1,
                        block_bottom,
                        day_col_w - 2,
                        height_px,
                        fill=1,
                        stroke=1,
                    )

                    # Text: course.section (bold), faculty, time
                    c.setFillColor(black)
                    font_size = 7
                    line_h = font_size + 2
                    text_top = block_top_y - 2

                    c.setFont("Helvetica-Bold", font_size)
                    if height_px >= line_h:
                        label = f"{course_info['course']}.{course_info['section']}"
                        c.drawString(day_x + 3, text_top - line_h, label)

                    c.setFont("Helvetica", font_size)
                    if height_px >= 2 * line_h:
                        c.drawString(
                            day_x + 3, text_top - 2 * line_h, course_info["faculty"]
                        )
                    if height_px >= 3 * line_h:
                        time_disp = f"{sh}:{sm:02d} - {eh}:{em:02d}"
                        c.drawString(day_x + 3, text_top - 3 * line_h, time_disp)

            c.showPage()

    c.save()
    return buffer.getvalue()
