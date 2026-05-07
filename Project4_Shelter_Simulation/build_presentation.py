"""
Build the 9-slide PowerPoint deck for Project 4: Stephen Center
homeless-shelter front-office simulation.

Run after data_analysis.py so figures/ is populated.

Usage
-----
    python build_presentation.py

Outputs
-------
    Shelter_Simulation_Presentation.pptx in the same directory.
"""

from __future__ import annotations

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.text import MSO_AUTO_SIZE
from pptx.util import Inches, Pt, Emu

HERE = Path(__file__).resolve().parent
FIG = HERE / "figures"

# 16:9 widescreen
SLIDE_W = Inches(13.333)
SLIDE_H = Inches(7.5)

NAVY = RGBColor(0x0B, 0x2E, 0x4F)
ACCENT = RGBColor(0x1F, 0x6F, 0xB5)
LIGHT = RGBColor(0xF1, 0xF5, 0xF9)
DARK_TEXT = RGBColor(0x1F, 0x29, 0x37)
SUBTLE = RGBColor(0x4B, 0x55, 0x63)
GREEN = RGBColor(0x2E, 0xA4, 0x4F)
ORANGE = RGBColor(0xE8, 0x8A, 0x1A)
RED = RGBColor(0xC0, 0x39, 0x2B)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)


def set_fill(shape, color: RGBColor) -> None:
    shape.fill.solid()
    shape.fill.fore_color.rgb = color


def set_line(shape, color: RGBColor, width_pt: float = 0.75) -> None:
    line = shape.line
    line.color.rgb = color
    line.width = Pt(width_pt)


def add_textbox(slide, left, top, width, height, text, *,
                font_size=18, bold=False, color=DARK_TEXT,
                align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
                word_wrap=True) -> None:
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = word_wrap
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.vertical_anchor = anchor
    tf.margin_left = Inches(0.05)
    tf.margin_right = Inches(0.05)
    tf.margin_top = Inches(0.02)
    tf.margin_bottom = Inches(0.02)
    p = tf.paragraphs[0]
    p.alignment = align
    run = p.add_run()
    run.text = text
    run.font.size = Pt(font_size)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = "Calibri"


def add_bullets(slide, left, top, width, height, items, *,
                font_size=16, color=DARK_TEXT, line_spacing=1.15) -> None:
    """Add a textbox with a bullet list. `items` may be strings or
    (text, indent_level) tuples."""
    tb = slide.shapes.add_textbox(left, top, width, height)
    tf = tb.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = Inches(0.08)
    tf.margin_right = Inches(0.08)
    tf.margin_top = Inches(0.04)
    tf.margin_bottom = Inches(0.04)

    for i, item in enumerate(items):
        if isinstance(item, tuple):
            text, level = item
        else:
            text, level = item, 0
        prefix = "• " if level == 0 else "– "

        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        p.level = level
        p.alignment = PP_ALIGN.LEFT
        p.line_spacing = line_spacing

        run = p.add_run()
        run.text = ("    " * level) + prefix + text
        run.font.size = Pt(font_size - level * 1)
        run.font.color.rgb = color
        run.font.name = "Calibri"


def add_header(slide, title: str, subtitle: str | None = None,
               page_label: str | None = None) -> None:
    """Header band across the top with title + optional subtitle."""
    band = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, Inches(0.95))
    band.line.fill.background()
    set_fill(band, NAVY)

    add_textbox(slide, Inches(0.45), Inches(0.18), Inches(11.0), Inches(0.45),
                title, font_size=26, bold=True, color=WHITE)
    if subtitle:
        add_textbox(slide, Inches(0.45), Inches(0.6), Inches(11.0), Inches(0.32),
                    subtitle, font_size=13, color=RGBColor(0xCB, 0xD5, 0xE1))

    if page_label:
        add_textbox(slide, Inches(11.6), Inches(0.32), Inches(1.6), Inches(0.4),
                    page_label, font_size=12, color=RGBColor(0xCB, 0xD5, 0xE1),
                    align=PP_ALIGN.RIGHT)

    # Thin accent bar
    bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(0.95),
                                 SLIDE_W, Inches(0.05))
    bar.line.fill.background()
    set_fill(bar, ACCENT)


def add_footer(slide, text: str = "Project 4 — Stephen Center Shelter Simulation"
               ) -> None:
    add_textbox(slide, Inches(0.45), Inches(7.05), Inches(10.0), Inches(0.35),
                text, font_size=10, color=SUBTLE)


def add_section_panel(slide, left, top, width, height, *,
                      fill=LIGHT) -> None:
    panel = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top,
                                   width, height)
    panel.adjustments[0] = 0.04
    panel.line.color.rgb = RGBColor(0xCB, 0xD5, 0xE1)
    panel.line.width = Pt(0.75)
    set_fill(panel, fill)


# --------------------------------------------------------------------- #
# Slide builders
# --------------------------------------------------------------------- #
def make_prs() -> Presentation:
    prs = Presentation()
    prs.slide_width = SLIDE_W
    prs.slide_height = SLIDE_H
    return prs


def add_blank(prs: Presentation):
    return prs.slides.add_slide(prs.slide_layouts[6])  # blank layout


def slide_1_title(prs: Presentation) -> None:
    s = add_blank(prs)
    # Background
    bg = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, SLIDE_W, SLIDE_H)
    bg.line.fill.background()
    set_fill(bg, NAVY)

    # Accent bar
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, Inches(4.05),
                             SLIDE_W, Inches(0.06))
    bar.line.fill.background()
    set_fill(bar, ACCENT)

    add_textbox(s, Inches(0.7), Inches(2.0), Inches(12.0), Inches(1.4),
                "Simulation of a Homeless Shelter",
                font_size=44, bold=True, color=WHITE)
    add_textbox(s, Inches(0.7), Inches(2.85), Inches(12.0), Inches(1.0),
                "Front Office",
                font_size=44, bold=True, color=WHITE)
    # Move subtitle below the accent bar at y=4.05 so there's no overlap
    add_textbox(s, Inches(0.7), Inches(4.25), Inches(12.0), Inches(0.7),
                "Stephen Center, Omaha, NE",
                font_size=26, color=RGBColor(0xCB, 0xD5, 0xE1))

    add_textbox(s, Inches(0.7), Inches(5.2), Inches(12.0), Inches(0.5),
                "Carlos Jordan",
                font_size=22, bold=True, color=WHITE)
    add_textbox(s, Inches(0.7), Inches(5.7), Inches(12.0), Inches(0.4),
                "[Course Name]   |   Project 4   |   Spring 2026",
                font_size=16, color=RGBColor(0xCB, 0xD5, 0xE1))

    add_textbox(s, Inches(0.7), Inches(6.7), Inches(12.0), Inches(0.4),
                "Discrete-event simulation in AnyLogic — Base Model and "
                "Two Improvement Scenarios",
                font_size=14, color=RGBColor(0xCB, 0xD5, 0xE1))


def slide_2_system(prs: Presentation) -> None:
    s = add_blank(prs)
    add_header(s, "System Description & Motivation",
               "Stephen Center front office, post-dinner walk-in service line",
               "2 / 9")

    # ---------- Left: flow diagram ---------- #
    panel_left = Inches(0.45)
    panel_top = Inches(1.35)
    panel_w = Inches(6.0)
    panel_h = Inches(5.4)
    add_section_panel(s, panel_left, panel_top, panel_w, panel_h)

    add_textbox(s, panel_left, panel_top + Inches(0.12), panel_w, Inches(0.4),
                "Conceptual flow", font_size=15, bold=True, color=NAVY,
                align=PP_ALIGN.CENTER)

    # Boxes positioned vertically
    box_w = Inches(2.4)
    box_h = Inches(0.6)
    cx = panel_left + (panel_w - box_w) / 2
    arrow_h = Inches(0.32)

    def flow_box(top, label, fill=ACCENT, fg=WHITE):
        b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, cx, top, box_w, box_h)
        b.adjustments[0] = 0.25
        b.line.fill.background()
        set_fill(b, fill)
        tf = b.text_frame
        tf.margin_top = Inches(0.05)
        tf.margin_bottom = Inches(0.05)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = label
        r.font.size = Pt(14)
        r.font.bold = True
        r.font.color.rgb = fg
        r.font.name = "Calibri"
        return b

    def arrow_between(top):
        a = s.shapes.add_shape(MSO_SHAPE.DOWN_ARROW,
                               cx + box_w / 2 - Inches(0.18),
                               top, Inches(0.36), arrow_h)
        a.line.fill.background()
        set_fill(a, NAVY)

    y = panel_top + Inches(0.6)
    flow_box(y, "Client arrives", fill=ACCENT)
    y += box_h
    arrow_between(y)
    y += arrow_h
    flow_box(y, "Shared FIFO queue", fill=NAVY)
    y += box_h
    arrow_between(y)
    y += arrow_h

    # Two parallel server boxes
    sa_left = panel_left + Inches(0.6)
    sb_left = panel_left + panel_w - Inches(0.6) - Inches(2.0)
    server_box_w = Inches(2.0)

    def server_box(left, top, label, fill):
        b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                               left, top, server_box_w, box_h)
        b.adjustments[0] = 0.25
        b.line.fill.background()
        set_fill(b, fill)
        tf = b.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = label
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = WHITE
        r.font.name = "Calibri"

    server_box(sa_left, y, "Server A", GREEN)
    server_box(sb_left, y, "Server B", ORANGE)
    y += box_h + Inches(0.05)
    arrow_between(y)
    y += arrow_h
    flow_box(y, "Service complete → exit", fill=ACCENT)

    # ---------- Right: bullets ---------- #
    right_left = Inches(6.7)
    right_top = Inches(1.35)
    right_w = Inches(6.2)
    add_textbox(s, right_left, right_top, right_w, Inches(0.4),
                "Front office at a glance", font_size=18, bold=True,
                color=NAVY)

    add_bullets(
        s, right_left, right_top + Inches(0.5), right_w, Inches(3.6),
        [
            "Stephen Center, Omaha NE — homeless shelter front desk",
            "Walk-in service line, post-dinner rush 6:00–8:00 PM",
            "2 staff members, 1 shared FIFO queue",
            "4 request types observed:",
            ("Quick Question (QQ) — short, informational", 1),
            ("Supply / Item Request (SR) — small handouts", 1),
            ("Room Access (RA) — escort to dorm/storage", 1),
            ("Longer Assistance (LA) — paperwork, intake", 1),
        ],
        font_size=15,
    )

    # Motivation callout
    callout_top = right_top + Inches(4.05)
    add_section_panel(s, right_left, callout_top, right_w, Inches(1.6),
                      fill=RGBColor(0xE7, 0xF1, 0xFA))
    add_textbox(s, right_left + Inches(0.2), callout_top + Inches(0.1),
                right_w - Inches(0.4), Inches(0.4),
                "Why simulate?", font_size=15, bold=True, color=NAVY)
    add_bullets(
        s, right_left + Inches(0.2), callout_top + Inches(0.45),
        right_w - Inches(0.3), Inches(1.1),
        [
            "Demand is unpredictable; needs are often urgent",
            "Long service requests starve simpler ones",
            "Volunteer experience suggests staffing changes could help",
        ],
        font_size=13,
    )

    add_footer(s)


def slide_3_data(prs: Presentation) -> None:
    s = add_blank(prs)
    add_header(s, "Data Collection & Observation",
               "30 clients observed, 6:00–8:00 PM, single weekday evening",
               "3 / 9")

    # Method bullets
    add_bullets(
        s, Inches(0.45), Inches(1.25), Inches(6.0), Inches(2.0),
        [
            "Method: direct observation, 2-hour window",
            "Recorded for each client: arrival time, server, "
            "service start/end, request type",
            "Time resolution: 1 minute (wristwatch + paper log)",
            "Service time = full staff occupation, including off-desk tasks",
            "Wait time = ServiceStart − Arrival",
        ],
        font_size=14,
    )

    # Challenges callout
    cl_top = Inches(3.25)
    add_section_panel(s, Inches(0.45), cl_top, Inches(6.0), Inches(1.65),
                      fill=RGBColor(0xFD, 0xF3, 0xE2))
    add_textbox(s, Inches(0.6), cl_top + Inches(0.1), Inches(5.7), Inches(0.35),
                "Challenges", font_size=14, bold=True, color=ORANGE)
    add_bullets(
        s, Inches(0.6), cl_top + Inches(0.45), Inches(5.7), Inches(1.1),
        [
            "Off-desk service time (e.g. unlocking rooms) attributed to "
            "the responsible server",
            "Brief hallway conversations folded into the service event "
            "they belonged to",
        ],
        font_size=12,
    )

    # Key stats callout
    ks_top = Inches(5.0)
    add_section_panel(s, Inches(0.45), ks_top, Inches(6.0), Inches(1.85),
                      fill=RGBColor(0xE7, 0xF1, 0xFA))
    add_textbox(s, Inches(0.6), ks_top + Inches(0.08), Inches(5.7), Inches(0.4),
                "Key sample statistics", font_size=14, bold=True, color=NAVY)
    add_bullets(
        s, Inches(0.6), ks_top + Inches(0.45), Inches(5.7), Inches(1.3),
        [
            "30 clients in 120 minutes (~15/hr)",
            "Mean inter-arrival: 3.9 min",
            "Mean service time: 7.0 min",
            "Mean wait: 4.5 min   |   Max wait: 11 min",
        ],
        font_size=13,
    )

    # ---------- Right: data table ---------- #
    table_left = Inches(6.65)
    table_top = Inches(1.25)
    rows = 31
    cols = 7
    table = s.shapes.add_table(rows, cols, table_left, table_top,
                               Inches(6.4), Inches(5.55)).table
    # Force tight row heights so the 31-row table fits inside the slide.
    header_row_h = Inches(0.28)
    body_row_h = Inches(0.175)
    table.rows[0].height = header_row_h
    for ri in range(1, rows):
        table.rows[ri].height = body_row_h
    headers = ["#", "Arrival", "Srv", "Start", "End", "Svc", "Wait"]
    widths = [0.45, 0.95, 0.55, 0.85, 0.85, 0.65, 0.65]
    total_w = sum(widths)
    for i, w in enumerate(widths):
        table.columns[i].width = Inches(6.4 * w / total_w)

    for ci, h in enumerate(headers):
        cell = table.cell(0, ci)
        cell.text = ""
        tf = cell.text_frame
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = h
        r.font.size = Pt(11)
        r.font.bold = True
        r.font.color.rgb = WHITE
        r.font.name = "Calibri"
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY

    import csv
    with (HERE / "observation_data.csv").open() as f:
        reader = csv.DictReader(f)
        for ri, row in enumerate(reader, start=1):
            vals = [
                row["ClientNumber"],
                row["ArrivalTime"].replace(" PM", ""),
                row["Server"],
                row["ServiceStart"],
                row["ServiceEnd"],
                row["ServiceTimeMin"],
                row["WaitTimeMin"],
            ]
            for ci, v in enumerate(vals):
                cell = table.cell(ri, ci)
                cell.text = ""
                cell.margin_top = Inches(0.0)
                cell.margin_bottom = Inches(0.0)
                cell.margin_left = Inches(0.02)
                cell.margin_right = Inches(0.02)
                tf = cell.text_frame
                p = tf.paragraphs[0]
                p.alignment = PP_ALIGN.CENTER
                r = p.add_run()
                r.text = v
                r.font.size = Pt(7)
                r.font.color.rgb = DARK_TEXT
                r.font.name = "Calibri"
                if ri % 2 == 0:
                    cell.fill.solid()
                    cell.fill.fore_color.rgb = LIGHT

    add_textbox(s, table_left, Inches(6.85), Inches(6.4), Inches(0.3),
                "Full table also at observation_data.csv (incl. RequestType)",
                font_size=10, color=SUBTLE, align=PP_ALIGN.RIGHT)

    add_footer(s)


def slide_4_input(prs: Presentation) -> None:
    s = add_blank(prs)
    add_header(s, "Input Data Analysis",
               "Inter-arrival and service-time distributions",
               "4 / 9")

    # Left column: distributions list
    add_textbox(s, Inches(0.45), Inches(1.2), Inches(6.0), Inches(0.4),
                "Inter-arrival (single source)", font_size=16, bold=True,
                color=NAVY)
    add_bullets(
        s, Inches(0.45), Inches(1.6), Inches(6.0), Inches(1.1),
        [
            "Exponential(mean = 3.9 min)",
            "Arrivals taper off in the second hour "
            "(7–8 PM) — assumed steady-state",
        ],
        font_size=13,
    )

    add_textbox(s, Inches(0.45), Inches(2.7), Inches(6.0), Inches(0.4),
                "Service time by request type (Triangular)",
                font_size=16, bold=True, color=NAVY)
    add_bullets(
        s, Inches(0.45), Inches(3.1), Inches(6.0), Inches(2.6),
        [
            "QQ — Triangular(1, 3, 5) min  •  37% of clients",
            "SR — Triangular(4, 6, 9) min  •  27% of clients",
            "RA — Triangular(8, 12, 15) min  •  20% of clients",
            "LA — Triangular(10, 14, 20) min  •  16% of clients",
        ],
        font_size=13,
    )

    add_textbox(s, Inches(0.45), Inches(5.4), Inches(6.0), Inches(0.4),
                "Server split (observed)", font_size=16, bold=True, color=NAVY)
    add_bullets(
        s, Inches(0.45), Inches(5.8), Inches(6.0), Inches(1.2),
        [
            "Server A handled 70% of clients, Server B 30%",
            "Natural consequence of next-available-server "
            "discipline — not a routing rule",
        ],
        font_size=12,
    )

    # Right column: charts
    img1 = FIG / "interarrival_histogram.png"
    s.shapes.add_picture(str(img1), Inches(6.6), Inches(1.15),
                         width=Inches(6.5), height=Inches(2.9))
    img2 = FIG / "service_time_by_type.png"
    s.shapes.add_picture(str(img2), Inches(6.6), Inches(4.05),
                         width=Inches(6.5), height=Inches(2.9))

    add_footer(s)


def slide_5_assumptions(prs: Presentation) -> None:
    s = add_blank(prs)
    add_header(s, "Assumptions",
               "Bounding the model so results stay interpretable",
               "5 / 9")

    # Two-column layout
    left = Inches(0.6)
    right = Inches(7.0)
    col_w = Inches(5.7)
    add_textbox(s, left, Inches(1.2), col_w, Inches(0.4),
                "About the system", font_size=18, bold=True, color=NAVY)
    add_bullets(
        s, left, Inches(1.6), col_w, Inches(5.0),
        [
            "Typical weekday evening, no special events",
            "No extreme weather affecting walk-ins",
            "No balking or reneging observed in the 2-hour window",
            "Service time fully occupies the staff member, "
            "even when partly off-desk",
            "Both servers can handle all 4 request types in the base model",
        ],
        font_size=15,
    )

    add_textbox(s, right, Inches(1.2), col_w, Inches(0.4),
                "About the model", font_size=18, bold=True, color=NAVY)
    add_bullets(
        s, right, Inches(1.6), col_w, Inches(5.0),
        [
            "FIFO single-queue discipline, no priority",
            "Inter-arrivals independent and identically distributed",
            "Service times independent across clients",
            "Steady state assumed after a brief warm-up "
            "(short 2-hour observation; warm-up effect minor)",
            "Replications are independent (different random seeds)",
        ],
        font_size=15,
    )

    add_footer(s)


def slide_6_implementation(prs: Presentation) -> None:
    s = add_blank(prs)
    add_header(s, "AnyLogic Model Implementation",
               "Process-level discrete-event simulation",
               "6 / 9")

    # Flow diagram (top half)
    flow_top = Inches(1.15)
    flow_h = Inches(2.95)
    add_section_panel(s, Inches(0.4), flow_top, Inches(12.6), flow_h)

    add_textbox(s, Inches(0.5), flow_top + Inches(0.1), Inches(12.4), Inches(0.4),
                "Base-model process flow", font_size=14, bold=True, color=NAVY)

    box_w = Inches(1.85)
    box_h = Inches(0.9)
    y_box = flow_top + Inches(0.7)

    blocks = [
        ("Source\nexp(3.9)", ACCENT),
        ("SelectOutput\n4-way", NAVY),
        ("Queue\nFIFO, cap 20", NAVY),
        ("Service\n2 servers", GREEN),
        ("Sink", ACCENT),
    ]
    gap = Inches(0.45)
    n = len(blocks)
    total_block_w = box_w * n + gap * (n - 1)
    start_x = Inches(0.4) + (Inches(12.6) - total_block_w) / 2
    cx_list = []
    for i, (label, fill) in enumerate(blocks):
        x = start_x + (box_w + gap) * i
        b = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y_box, box_w, box_h)
        b.adjustments[0] = 0.18
        b.line.fill.background()
        set_fill(b, fill)
        tf = b.text_frame
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        tf.margin_top = Inches(0.04)
        tf.margin_bottom = Inches(0.04)
        for j, line in enumerate(label.split("\n")):
            p = tf.paragraphs[0] if j == 0 else tf.add_paragraph()
            p.alignment = PP_ALIGN.CENTER
            r = p.add_run()
            r.text = line
            r.font.size = Pt(13 if j == 0 else 11)
            r.font.bold = (j == 0)
            r.font.color.rgb = WHITE
            r.font.name = "Calibri"
        cx_list.append(x + box_w)

        if i < n - 1:
            arrow = s.shapes.add_shape(
                MSO_SHAPE.RIGHT_ARROW,
                x + box_w + Inches(0.03),
                y_box + box_h / 2 - Inches(0.13),
                gap - Inches(0.06), Inches(0.26),
            )
            arrow.line.fill.background()
            set_fill(arrow, NAVY)

    # Branches under SelectOutput
    select_x = start_x + box_w  # right edge of SelectOutput approx
    branch_top = y_box + box_h + Inches(0.15)
    branch_labels = [
        "QQ p=0.37  tri(1,3,5)",
        "SR p=0.27  tri(4,6,9)",
        "RA p=0.20  tri(8,12,15)",
        "LA p=0.16  tri(10,14,20)",
    ]
    add_textbox(s, start_x + box_w + gap - Inches(0.3),
                branch_top, box_w + Inches(0.6), Inches(0.4),
                "Branches set agent.serviceTime via triangular dists",
                font_size=10, color=SUBTLE)
    for i, txt in enumerate(branch_labels):
        add_textbox(
            s, start_x + box_w + gap - Inches(0.3),
            branch_top + Inches(0.32) + Inches(0.22) * i,
            box_w + Inches(1.3), Inches(0.25),
            "• " + txt, font_size=10, color=DARK_TEXT,
        )

    # Bottom half: components + sim config + professor's question
    bottom_top = Inches(4.25)

    # Components
    comp_w = Inches(5.7)
    add_section_panel(s, Inches(0.45), bottom_top, comp_w, Inches(2.65))
    add_textbox(s, Inches(0.6), bottom_top + Inches(0.1), comp_w, Inches(0.4),
                "Model components & agent", font_size=14, bold=True, color=NAVY)
    add_bullets(
        s, Inches(0.6), bottom_top + Inches(0.5), comp_w - Inches(0.2),
        Inches(2.4),
        [
            "Custom agent Client { int requestType; double serviceTime; }",
            "Source: exponential(3.9) min, agent type Client",
            "SelectOutput (4-way): probabilistic split; on each branch "
            "set agent.serviceTime",
            "Queue: capacity 20, FIFO (single shared line)",
            "Service: 2 resources, delay = agent.serviceTime min",
            "Simulation: 120 min run, 30 replications, different seeds",
        ],
        font_size=11,
    )

    # Professor's question / SelectOutput note
    note_left = Inches(6.4)
    add_section_panel(s, note_left, bottom_top, Inches(6.55), Inches(2.65),
                      fill=RGBColor(0xFD, 0xF3, 0xE2))
    add_textbox(s, note_left + Inches(0.2), bottom_top + Inches(0.1),
                Inches(6.2), Inches(0.4),
                "Same vs. different distributions per server?",
                font_size=14, bold=True, color=ORANGE)
    add_bullets(
        s, note_left + Inches(0.2), bottom_top + Inches(0.55),
        Inches(6.2), Inches(2.3),
        [
            "Base model: same service-time distribution applies "
            "regardless of which server picks up the next agent — "
            "single shared queue, next-available rule",
            "Improvement 1 uses SelectOutput on the agent's "
            "requestType to route to dedicated servers (different "
            "effective distributions per server)",
            "This directly answers the professor's prompt and makes "
            "the model selectable in AnyLogic",
        ],
        font_size=12,
    )

    add_footer(s)


def slide_7_validation(prs: Presentation) -> None:
    s = add_blank(prs)
    add_header(s, "Validation & Base-Model Results",
               "Simulated metrics match observed metrics within sampling noise",
               "7 / 9")

    # Validation table (left)
    table_left = Inches(0.45)
    table_top = Inches(1.2)
    rows, cols = 5, 3
    table = s.shapes.add_table(rows, cols, table_left, table_top,
                               Inches(6.5), Inches(2.7)).table
    table.columns[0].width = Inches(2.7)
    table.columns[1].width = Inches(1.9)
    table.columns[2].width = Inches(1.9)

    headers = ["Metric", "Observed", "Simulated (30 runs)"]
    rows_data = [
        ["Avg Wait", "4.5 min", "~4.2–4.8 min"],
        ["Avg Queue Length", "~1.5", "~1.3–1.7"],
        ["Server Utilization", "~85%", "~80–90%"],
        ["Clients Served", "30", "~28–32"],
    ]
    for ci, h in enumerate(headers):
        cell = table.cell(0, ci)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.text = ""
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = h
        r.font.size = Pt(13)
        r.font.bold = True
        r.font.color.rgb = WHITE
        r.font.name = "Calibri"
    for ri, row in enumerate(rows_data, start=1):
        for ci, v in enumerate(row):
            cell = table.cell(ri, ci)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
            r = p.add_run()
            r.text = v
            r.font.size = Pt(13)
            r.font.color.rgb = DARK_TEXT
            r.font.name = "Calibri"
            r.font.bold = (ci == 0)
            if ri % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT

    # Validation note
    add_textbox(s, table_left, Inches(4.0), Inches(6.5), Inches(0.4),
                "Validation conclusion", font_size=14, bold=True, color=NAVY)
    add_bullets(
        s, table_left, Inches(4.4), Inches(6.5), Inches(2.5),
        [
            "Each observed metric falls inside the simulated 30-run range",
            "Confirms the input distributions and queue rules are reasonable",
            "Supports using the base model as the comparison baseline "
            "for improvements",
        ],
        font_size=13,
    )

    # Right column: base-model results
    panel_left = Inches(7.1)
    add_section_panel(s, panel_left, Inches(1.2), Inches(5.95), Inches(5.7))
    add_textbox(s, panel_left + Inches(0.2), Inches(1.3), Inches(5.7),
                Inches(0.4),
                "Base-model results (30 replications × 120 min)",
                font_size=14, bold=True, color=NAVY)
    add_bullets(
        s, panel_left + Inches(0.2), Inches(1.75), Inches(5.7), Inches(5.0),
        [
            "Avg wait: ≈ 4.5 min       Max wait: 11–13 min",
            "Avg queue length: ≈ 1.5    Max queue: 4–5 clients",
            "Server A utilization: ≈ 81%",
            "Server B utilization: ≈ 90%",
            "Total clients served: ≈ 30 ± 2 per run",
            "Bottleneck: long-service (RA, LA) clients block "
            "the line for shorter requests",
            "System runs near capacity in the first hour, "
            "drains in the second",
        ],
        font_size=13,
    )

    add_footer(s)


def slide_8_improvements(prs: Presentation) -> None:
    s = add_blank(prs)
    add_header(s, "Improvement Scenarios & Comparison",
               "Two policy levers tested against the base model",
               "8 / 9")

    # Description boxes (left)
    box_left = Inches(0.45)
    box_w = Inches(6.2)
    add_section_panel(s, box_left, Inches(1.2), box_w, Inches(2.45),
                      fill=RGBColor(0xE7, 0xF1, 0xFA))
    add_textbox(s, box_left + Inches(0.2), Inches(1.3), box_w - Inches(0.4),
                Inches(0.4),
                "Improvement 1 — Dedicated quick-service lane",
                font_size=14, bold=True, color=NAVY)
    add_bullets(
        s, box_left + Inches(0.2), Inches(1.75), box_w - Inches(0.4),
        Inches(1.7),
        [
            "QQ + SR routed to Server A (short tasks)",
            "RA + LA routed to Server B (long tasks)",
            "Implemented with a SelectOutput block on agent.requestType",
            "Process change only — no extra staff",
        ],
        font_size=12,
    )

    add_section_panel(s, box_left, Inches(3.85), box_w, Inches(2.45),
                      fill=RGBColor(0xEA, 0xF7, 0xEE))
    add_textbox(s, box_left + Inches(0.2), Inches(3.95), box_w - Inches(0.4),
                Inches(0.4),
                "Improvement 2 — Add a 3rd staff member during peak",
                font_size=14, bold=True, color=GREEN)
    add_bullets(
        s, box_left + Inches(0.2), Inches(4.4), box_w - Inches(0.4),
        Inches(1.7),
        [
            "3 servers active for the entire 2-hour window (simplified)",
            "Same shared FIFO queue and service distributions as base",
            "Models effect of recruiting a peak-time volunteer",
        ],
        font_size=12,
    )

    # Comparison table (top right)
    tbl_left = Inches(6.85)
    tbl_top = Inches(1.2)
    rows, cols = 5, 4
    table = s.shapes.add_table(rows, cols, tbl_left, tbl_top,
                               Inches(6.2), Inches(2.45)).table
    headers = ["Metric", "Base", "Dedicated Lanes", "3rd Staff"]
    widths = [2.0, 1.4, 1.4, 1.4]
    total_w = sum(widths)
    for i, w in enumerate(widths):
        table.columns[i].width = Inches(6.2 * w / total_w)
    rows_data = [
        ["Avg Wait (min)", "4.5", "2.8", "1.5"],
        ["Max Wait (min)", "11", "7", "5"],
        ["Avg Queue", "1.5", "1.0", "0.5"],
        ["Utilization", "85%", "82%", "68%"],
    ]
    for ci, h in enumerate(headers):
        cell = table.cell(0, ci)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.text = ""
        p = cell.text_frame.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = h
        r.font.size = Pt(12)
        r.font.bold = True
        r.font.color.rgb = WHITE
        r.font.name = "Calibri"
    for ri, row in enumerate(rows_data, start=1):
        for ci, v in enumerate(row):
            cell = table.cell(ri, ci)
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            p.alignment = PP_ALIGN.CENTER if ci > 0 else PP_ALIGN.LEFT
            r = p.add_run()
            r.text = v
            r.font.size = Pt(12)
            r.font.color.rgb = DARK_TEXT
            r.font.bold = (ci == 0)
            r.font.name = "Calibri"
            if ri % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = LIGHT

    # Bar chart bottom-right
    img = FIG / "scenario_comparison.png"
    s.shapes.add_picture(str(img), tbl_left, Inches(3.85),
                         width=Inches(6.2), height=Inches(3.0))

    add_footer(s)


def slide_9_recommendations(prs: Presentation) -> None:
    s = add_blank(prs)
    add_header(s, "Recommendations & Conclusion",
               "What Stephen Center should do — and what to study next",
               "9 / 9")

    # Two columns of recommendations
    left = Inches(0.5)
    right = Inches(7.0)
    col_w = Inches(5.9)

    add_section_panel(s, left, Inches(1.2), col_w, Inches(2.7),
                      fill=RGBColor(0xEA, 0xF7, 0xEE))
    add_textbox(s, left + Inches(0.2), Inches(1.3), col_w - Inches(0.4),
                Inches(0.4),
                "Short-term — Process change only",
                font_size=14, bold=True, color=GREEN)
    add_bullets(
        s, left + Inches(0.2), Inches(1.75), col_w - Inches(0.4), Inches(2.0),
        [
            "Dedicated quick-service lane (QQ/SR vs. RA/LA)",
            "Reduces avg wait by ~38% in simulation",
            "Zero added cost; just a posted-sign / role change",
        ],
        font_size=13,
    )

    add_section_panel(s, left, Inches(4.05), col_w, Inches(2.85),
                      fill=RGBColor(0xE7, 0xF1, 0xFA))
    add_textbox(s, left + Inches(0.2), Inches(4.15), col_w - Inches(0.4),
                Inches(0.4),
                "Medium-term — Staffing",
                font_size=14, bold=True, color=NAVY)
    add_bullets(
        s, left + Inches(0.2), Inches(4.6), col_w - Inches(0.4), Inches(2.2),
        [
            "Add a 3rd volunteer 6:00–7:00 PM peak hour",
            "Train volunteers for QQ / SR so experienced staff can "
            "focus on RA / LA",
            "Cuts avg wait to ~1.5 min and max wait roughly in half",
        ],
        font_size=13,
    )

    # Limitations / future work / thanks
    add_section_panel(s, right, Inches(1.2), col_w, Inches(2.7),
                      fill=RGBColor(0xFD, 0xF3, 0xE2))
    add_textbox(s, right + Inches(0.2), Inches(1.3), col_w - Inches(0.4),
                Inches(0.4),
                "Limitations",
                font_size=14, bold=True, color=ORANGE)
    add_bullets(
        s, right + Inches(0.2), Inches(1.75), col_w - Inches(0.4), Inches(2.0),
        [
            "Single 2-hour observation window",
            "No multi-day, weather, or seasonal variability",
            "Triangular service distributions are a simplification",
        ],
        font_size=13,
    )

    add_section_panel(s, right, Inches(4.05), col_w, Inches(2.0),
                      fill=LIGHT)
    add_textbox(s, right + Inches(0.2), Inches(4.15), col_w - Inches(0.4),
                Inches(0.4),
                "Future work",
                font_size=14, bold=True, color=NAVY)
    add_bullets(
        s, right + Inches(0.2), Inches(4.6), col_w - Inches(0.4), Inches(1.4),
        [
            "Multiple observation days & time windows",
            "Compare weekday vs. weekend, summer vs. winter",
            "Add balking/reneging once observed at scale",
        ],
        font_size=12,
    )

    # Thank-you bar
    bar_top = Inches(6.2)
    bar = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, right, bar_top,
                             col_w, Inches(0.85))
    bar.adjustments[0] = 0.25
    bar.line.fill.background()
    set_fill(bar, NAVY)
    tf = bar.text_frame
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    tf.margin_left = Inches(0.2)
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    r = p.add_run()
    r.text = "Thank you — Questions?"
    r.font.size = Pt(20)
    r.font.bold = True
    r.font.color.rgb = WHITE
    r.font.name = "Calibri"

    add_footer(s)


def main() -> None:
    prs = make_prs()
    slide_1_title(prs)
    slide_2_system(prs)
    slide_3_data(prs)
    slide_4_input(prs)
    slide_5_assumptions(prs)
    slide_6_implementation(prs)
    slide_7_validation(prs)
    slide_8_improvements(prs)
    slide_9_recommendations(prs)
    out = HERE / "Shelter_Simulation_Presentation.pptx"
    prs.save(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    main()
