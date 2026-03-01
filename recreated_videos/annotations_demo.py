"""Annotations & Labels Demo — Brace, Angle, LabeledArrow, LabeledDot, LabeledLine, DimensionLine, Cross, SurroundingRectangle."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/annotations_demo')
canvas.set_background()
T = 12.0

# -- Colors -------------------------------------------------------------------
ACCENT = '#58C4DD'
YELLOW = '#FFFF00'
GREEN = '#83C167'
RED = '#FC6255'
ORANGE = '#F5A623'
WHITE = '#FFFFFF'
GRAY = '#888888'

# =============================================================================
# Phase 1: Braces and Angles (0 – 4s)
# =============================================================================

phase1_title = Text(
    text='Braces & Angles', x=960, y=60, font_size=42,
    fill=WHITE, stroke_width=0, text_anchor='middle',
)
phase1_title.fadein(0.0, 0.4)
phase1_title.fadeout(3.5, 4.0)
canvas.add(phase1_title)

# --- Rectangle with Brace along its bottom edge ---
rect1 = Rectangle(400, 200, x=180, y=250, fill=ACCENT, fill_opacity=0.3,
                   stroke=ACCENT, stroke_width=3, creation=0)
rect1.fadein(0.2, 0.6)
rect1.fadeout(3.5, 4.0)
canvas.add(rect1)

brace_bottom = Brace(rect1, direction='down', label='Width = 400',
                      creation=0.4, fill=WHITE)
brace_bottom.fadein(0.4, 0.8)
brace_bottom.fadeout(3.5, 4.0)
canvas.add(brace_bottom)

brace_right = Brace(rect1, direction='right', label='Height = 200',
                     creation=0.6, fill=WHITE)
brace_right.fadein(0.6, 1.0)
brace_right.fadeout(3.5, 4.0)
canvas.add(brace_right)

# --- Two lines meeting at an angle with Angle measurement ---
# Vertex at (900, 450), two arms extending outward
vx, vy = 900, 420
arm_len = 220
a1_deg = 0    # arm 1 direction (rightward)
a2_deg = 55   # arm 2 direction (up-right)

p1x = vx + arm_len * math.cos(math.radians(a1_deg))
p1y = vy - arm_len * math.sin(math.radians(a1_deg))
p2x = vx + arm_len * math.cos(math.radians(a2_deg))
p2y = vy - arm_len * math.sin(math.radians(a2_deg))

line_a = Line(x1=vx, y1=vy, x2=p1x, y2=p1y, stroke=ORANGE, stroke_width=4, creation=0.8)
line_b = Line(x1=vx, y1=vy, x2=p2x, y2=p2y, stroke=ORANGE, stroke_width=4, creation=0.8)
line_a.fadein(0.8, 1.2)
line_b.fadein(0.8, 1.2)
line_a.fadeout(3.5, 4.0)
line_b.fadeout(3.5, 4.0)
canvas.add(line_a, line_b)

angle_marker = Angle(
    vertex=(vx, vy), p1=(p1x, p1y), p2=(p2x, p2y),
    radius=50, label=True, label_font_size=28,
    creation=1.0, stroke=YELLOW, stroke_width=3,
)
angle_marker.fadein(1.0, 1.4)
angle_marker.fadeout(3.5, 4.0)
canvas.add(angle_marker)

angle_label = Text(
    text='Angle measurement', x=1000, y=300, font_size=22,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=1.2,
)
angle_label.fadein(1.2, 1.5)
angle_label.fadeout(3.5, 4.0)
canvas.add(angle_label)

# --- Right angle marker ---
# Two perpendicular lines at (1500, 450)
rvx, rvy = 1500, 450
rp1 = (rvx + 180, rvy)      # horizontal arm
rp2 = (rvx, rvy - 180)      # vertical arm

rline_h = Line(x1=rvx, y1=rvy, x2=rp1[0], y2=rp1[1], stroke=GREEN, stroke_width=4, creation=1.4)
rline_v = Line(x1=rvx, y1=rvy, x2=rp2[0], y2=rp2[1], stroke=GREEN, stroke_width=4, creation=1.4)
rline_h.fadein(1.4, 1.8)
rline_v.fadein(1.4, 1.8)
rline_h.fadeout(3.5, 4.0)
rline_v.fadeout(3.5, 4.0)
canvas.add(rline_h, rline_v)

right_angle = RightAngle(
    vertex=(rvx, rvy), p1=rp1, p2=rp2,
    size=24, creation=1.6, stroke=YELLOW, stroke_width=3,
)
right_angle.fadein(1.6, 2.0)
right_angle.fadeout(3.5, 4.0)
canvas.add(right_angle)

right_label = Text(
    text='Right angle (90\u00b0)', x=1570, y=310, font_size=22,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=1.8,
)
right_label.fadein(1.8, 2.1)
right_label.fadeout(3.5, 4.0)
canvas.add(right_label)

# -- Description text for braces --
brace_label = Text(
    text='Brace annotations', x=380, y=220, font_size=22,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=0.3,
)
brace_label.fadein(0.3, 0.6)
brace_label.fadeout(3.5, 4.0)
canvas.add(brace_label)


# =============================================================================
# Phase 2: Labeled Objects (4 – 8s)
# =============================================================================

phase2_title = Text(
    text='Labels & Markers', x=960, y=60, font_size=42,
    fill=WHITE, stroke_width=0, text_anchor='middle', creation=4.0,
)
phase2_title.fadein(4.0, 4.4)
phase2_title.fadeout(7.5, 8.0)
canvas.add(phase2_title)

# --- LabeledArrow pointing to a circle ---
target_circle = Circle(r=50, cx=350, cy=350, fill=ACCENT, fill_opacity=0.5,
                        stroke=ACCENT, stroke_width=3, creation=4.0)
target_circle.fadein(4.0, 4.4)
target_circle.fadeout(7.5, 8.0)
canvas.add(target_circle)

labeled_arrow = LabeledArrow(
    x1=550, y1=280, x2=410, y2=330,
    label='Target shape', font_size=22, label_buff=15,
    creation=4.2, stroke=WHITE, stroke_width=2,
)
labeled_arrow.fadein(4.2, 4.6)
labeled_arrow.fadeout(7.5, 8.0)
canvas.add(labeled_arrow)

# --- LabeledDot ---
ldot = LabeledDot(label='A', r=28, cx=250, cy=600, creation=4.4,
                   font_size=24, fill=GREEN)
ldot.fadein(4.4, 4.8)
ldot.fadeout(7.5, 8.0)
canvas.add(ldot)

ldot2 = LabeledDot(label='B', r=28, cx=450, cy=600, creation=4.6,
                    font_size=24, fill=ORANGE)
ldot2.fadein(4.6, 5.0)
ldot2.fadeout(7.5, 8.0)
canvas.add(ldot2)

# --- LabeledLine connecting two labeled dots ---
lline = LabeledLine(
    x1=278, y1=600, x2=422, y2=600,
    label='d = 200', font_size=20, label_buff=18,
    creation=4.8, stroke=WHITE, stroke_width=2,
)
lline.fadein(4.8, 5.2)
lline.fadeout(7.5, 8.0)
canvas.add(lline)

# --- Cross through an object (marking "wrong") ---
wrong_rect = Rectangle(120, 80, x=750, y=350, fill=RED, fill_opacity=0.2,
                         stroke=RED, stroke_width=2, creation=5.0)
wrong_rect.fadein(5.0, 5.3)
wrong_rect.fadeout(7.5, 8.0)
canvas.add(wrong_rect)

wrong_text = Text(text='Error', x=810, y=400, font_size=24,
                   fill=RED, stroke_width=0, text_anchor='middle', creation=5.0)
wrong_text.fadein(5.0, 5.3)
wrong_text.fadeout(7.5, 8.0)
canvas.add(wrong_text)

cross_mark = wrong_rect.cross_out(start=5.3, end=5.8, color=RED, stroke_width=5)
cross_mark.fadeout(7.5, 8.0)
canvas.add(cross_mark)

# --- SurroundingRectangle around a group of shapes ---
group_s1 = Circle(r=30, cx=1200, cy=400, fill='#9B59B6', fill_opacity=0.5,
                   stroke='#9B59B6', stroke_width=2, creation=5.4)
group_s2 = Rectangle(60, 60, x=1290, y=370, fill=ACCENT, fill_opacity=0.5,
                      stroke=ACCENT, stroke_width=2, creation=5.4)
group_s3 = RegularPolygon(n=5, radius=35, cx=1400, cy=400, fill=ORANGE, fill_opacity=0.5,
                           stroke=ORANGE, stroke_width=2, creation=5.4)
group_s1.fadein(5.4, 5.7)
group_s2.fadein(5.4, 5.7)
group_s3.fadein(5.4, 5.7)
group_s1.fadeout(7.5, 8.0)
group_s2.fadeout(7.5, 8.0)
group_s3.fadeout(7.5, 8.0)
canvas.add(group_s1, group_s2, group_s3)

shape_group = VGroup(group_s1, group_s2, group_s3)
surround = SurroundingRectangle(shape_group, buff=20, creation=5.8,
                                 stroke=YELLOW, stroke_width=3)
surround.fadein(5.8, 6.2)
surround.fadeout(7.5, 8.0)
canvas.add(surround)

surround_label = Text(
    text='SurroundingRectangle', x=1300, y=330, font_size=20,
    fill=YELLOW, stroke_width=0, text_anchor='middle', creation=6.0,
)
surround_label.fadein(6.0, 6.3)
surround_label.fadeout(7.5, 8.0)
canvas.add(surround_label)

# Extra: LabeledArrow pointing at the surrounded group
group_arrow = LabeledArrow(
    x1=1300, y1=550, x2=1300, y2=470,
    label='Grouped shapes', font_size=20, label_buff=15,
    creation=6.2, stroke=GRAY, stroke_width=2,
)
group_arrow.fadein(6.2, 6.5)
group_arrow.fadeout(7.5, 8.0)
canvas.add(group_arrow)


# =============================================================================
# Phase 3: Advanced Annotations (8 – 12s)
# =============================================================================

phase3_title = Text(
    text='Advanced Annotations', x=960, y=60, font_size=42,
    fill=WHITE, stroke_width=0, text_anchor='middle', creation=8.0,
)
phase3_title.fadein(8.0, 8.4)
phase3_title.fadeout(11.5, 12.0)
canvas.add(phase3_title)

# --- DimensionLine between two points ---
dim_dot1 = Dot(r=6, cx=200, cy=250, fill=ACCENT, creation=8.2)
dim_dot2 = Dot(r=6, cx=600, cy=250, fill=ACCENT, creation=8.2)
dim_dot1.fadein(8.2, 8.5)
dim_dot2.fadein(8.2, 8.5)
dim_dot1.fadeout(11.5, 12.0)
dim_dot2.fadeout(11.5, 12.0)
canvas.add(dim_dot1, dim_dot2)

dim_line = DimensionLine(
    p1=(200, 250), p2=(600, 250),
    label='400 px', offset=40, font_size=22,
    creation=8.4, stroke=GRAY, stroke_width=1.5,
)
dim_line.fadein(8.4, 8.8)
dim_line.fadeout(11.5, 12.0)
canvas.add(dim_line)

dim_label_text = Text(
    text='DimensionLine', x=400, y=180, font_size=20,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=8.5,
)
dim_label_text.fadein(8.5, 8.8)
dim_label_text.fadeout(11.5, 12.0)
canvas.add(dim_label_text)

# --- Fully annotated triangle ---
# Triangle vertices
tx1, ty1 = 900, 800   # bottom-left
tx2, ty2 = 1350, 800  # bottom-right
tx3, ty3 = 1125, 420  # top (apex)

tri = Polygon((tx1, ty1), (tx2, ty2), (tx3, ty3),
              fill=ACCENT, fill_opacity=0.15, stroke=ACCENT, stroke_width=3,
              creation=8.6)
tri.fadein(8.6, 9.0)
tri.fadeout(11.5, 12.0)
canvas.add(tri)

# Vertex labels (LabeledDots)
vert_a = LabeledDot(label='A', r=18, cx=tx1, cy=ty1, creation=9.0,
                      font_size=16, fill='#9B59B6')
vert_b = LabeledDot(label='B', r=18, cx=tx2, cy=ty2, creation=9.0,
                      font_size=16, fill='#9B59B6')
vert_c = LabeledDot(label='C', r=18, cx=tx3, cy=ty3, creation=9.0,
                      font_size=16, fill='#9B59B6')
vert_a.fadein(9.0, 9.3)
vert_b.fadein(9.0, 9.3)
vert_c.fadein(9.0, 9.3)
vert_a.fadeout(11.5, 12.0)
vert_b.fadeout(11.5, 12.0)
vert_c.fadeout(11.5, 12.0)
canvas.add(vert_a, vert_b, vert_c)

# Brace along the base (bottom edge A-B)
# Use a thin rectangle as target for the brace along the base
base_target = Rectangle(tx2 - tx1, 2, x=tx1, y=ty1, creation=9.2)
base_brace = Brace(base_target, direction='down', label='a = 450',
                    creation=9.2, fill=WHITE)
base_brace.fadein(9.2, 9.6)
base_brace.fadeout(11.5, 12.0)
canvas.add(base_brace)

# Angle at vertex A (bottom-left)
angle_a = Angle(
    vertex=(tx1, ty1),
    p1=(tx2, ty2),   # toward B
    p2=(tx3, ty3),   # toward C
    radius=45, label=True, label_font_size=20,
    creation=9.5, stroke=YELLOW, stroke_width=2,
)
angle_a.fadein(9.5, 9.8)
angle_a.fadeout(11.5, 12.0)
canvas.add(angle_a)

# Angle at vertex B (bottom-right)
angle_b = Angle(
    vertex=(tx2, ty2),
    p1=(tx3, ty3),   # toward C
    p2=(tx1, ty1),   # toward A
    radius=45, label=True, label_font_size=20,
    creation=9.7, stroke=YELLOW, stroke_width=2,
)
angle_b.fadein(9.7, 10.0)
angle_b.fadeout(11.5, 12.0)
canvas.add(angle_b)

# DimensionLine along one side (A to C, the left edge)
dim_ac = DimensionLine(
    p1=(tx1, ty1), p2=(tx3, ty3),
    label='b', offset=35, font_size=20,
    creation=9.9, stroke=ORANGE, stroke_width=1.5,
)
dim_ac.fadein(9.9, 10.2)
dim_ac.fadeout(11.5, 12.0)
canvas.add(dim_ac)

# DimensionLine along the other side (B to C, the right edge)
dim_bc = DimensionLine(
    p1=(tx2, ty2), p2=(tx3, ty3),
    label='c', offset=-35, font_size=20,
    creation=10.1, stroke=ORANGE, stroke_width=1.5,
)
dim_bc.fadein(10.1, 10.4)
dim_bc.fadeout(11.5, 12.0)
canvas.add(dim_bc)

# Callout annotation pointing to the apex
apex_callout = LabeledArrow(
    x1=1350, y1=350, x2=1145, y2=415,
    label='Apex', font_size=20, label_buff=15,
    creation=10.3, stroke=WHITE, stroke_width=2,
)
apex_callout.fadein(10.3, 10.6)
apex_callout.fadeout(11.5, 12.0)
canvas.add(apex_callout)

# Descriptive text
tri_desc = Text(
    text='Triangle with angle, brace & dimension annotations',
    x=1125, y=900, font_size=22,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=10.5,
)
tri_desc.fadein(10.5, 10.8)
tri_desc.fadeout(11.5, 12.0)
canvas.add(tri_desc)

# =============================================================================
# Display
# =============================================================================
if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or T, fps=args.fps, port=args.port)
