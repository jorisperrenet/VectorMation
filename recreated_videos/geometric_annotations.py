"""Geometric Annotations Demo — Angle, RightAngle, Cross, DimensionLine,
Brace, LabeledLine, LabeledArrow, SurroundingRectangle, ArrowVectorField."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from vectormation.objects import *

args = parse_args()
v = VectorMathAnim(verbose=args.verbose, save_dir='svgs/geometric_annotations')
v.set_background()
T = 30.0

WHITE = '#FFFFFF'
BLUE  = '#58C4DD'
RED   = '#FC6255'
GREEN = '#83C167'
YELLOW = '#FFFF00'
GREY  = '#888888'

# =============================================================================
# Phase 1 (0-6s): Angle + RightAngle annotations
# =============================================================================
title1 = Text(text='Angle Annotations', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title1.write(0, 0.5)
title1.fadeout(5.0, 5.5)
v.add(title1)

# Triangle with angle annotations
ax, ay = 400, 700
bx, by = 900, 700
cx, cy = 650, 300

tri = Lines((ax, ay), (bx, by), (cx, cy), (ax, ay),
            stroke=BLUE, stroke_width=3, fill_opacity=0, creation=0)
tri.fadein(0.5, 1.0)
tri.fadeout(5.0, 5.5)
v.add(tri)

# Angle at vertex A
angle_a = Angle(vertex=(ax, ay), p1=(bx, by), p2=(cx, cy), radius=40,
                label='a', creation=0, stroke=YELLOW, stroke_width=2)
angle_a.fadein(1.5, 2.0)
angle_a.fadeout(5.0, 5.5)
v.add(angle_a)

# Angle at vertex B
angle_b = Angle(vertex=(bx, by), p1=(cx, cy), p2=(ax, ay), radius=40,
                label='b', creation=0, stroke=GREEN, stroke_width=2)
angle_b.fadein(2.0, 2.5)
angle_b.fadeout(5.0, 5.5)
v.add(angle_b)

# Angle at vertex C
angle_c = Angle(vertex=(cx, cy), p1=(ax, ay), p2=(bx, by), radius=40,
                label='c', creation=0, stroke=RED, stroke_width=2)
angle_c.fadein(2.5, 3.0)
angle_c.fadeout(5.0, 5.5)
v.add(angle_c)

# Label
lbl1 = Text(text='Angle(vertex, p1, p2, radius, label)', x=960, y=830,
            font_size=22, fill=GREY, stroke_width=0, text_anchor='middle', creation=0.3)
lbl1.fadeout(5.0, 5.5)
v.add(lbl1)

# Right angle demo on the right side
rect_x, rect_y = 1400, 500
line_h = Line(x1=rect_x - 100, y1=rect_y, x2=rect_x + 100, y2=rect_y,
              stroke=WHITE, stroke_width=2, creation=0)
line_h.fadein(1.0, 1.5)
line_h.fadeout(5.0, 5.5)
v.add(line_h)

line_v = Line(x1=rect_x, y1=rect_y - 100, x2=rect_x, y2=rect_y + 100,
              stroke=WHITE, stroke_width=2, creation=0)
line_v.fadein(1.0, 1.5)
line_v.fadeout(5.0, 5.5)
v.add(line_v)

right_angle = RightAngle(vertex=(rect_x, rect_y),
                          p1=(rect_x + 100, rect_y),
                          p2=(rect_x, rect_y - 100),
                          size=20, creation=0, stroke=YELLOW, stroke_width=2)
right_angle.fadein(2.0, 2.5)
right_angle.fadeout(5.0, 5.5)
v.add(right_angle)

ra_lbl = Text(text='RightAngle()', x=1400, y=700, font_size=22,
              fill=GREY, stroke_width=0, text_anchor='middle', creation=0.3)
ra_lbl.fadeout(5.0, 5.5)
v.add(ra_lbl)

# =============================================================================
# Phase 2 (6-12s): Cross + SurroundingRectangle
# =============================================================================
title2 = Text(text='Markers & Highlights', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title2.write(6, 6.5)
title2.fadeout(11.0, 11.5)
v.add(title2)

# Cross marks
for i, (px, py) in enumerate([(300, 350), (500, 450), (700, 300)]):
    cross = Cross(size=30, cx=px, cy=py, creation=6, stroke=RED, stroke_width=3)
    cross.fadein(6.5 + i * 0.3, 7.0 + i * 0.3)
    cross.fadeout(11.0, 11.5)
    v.add(cross)

cross_lbl = Text(text='Cross(size, cx, cy)', x=500, y=550, font_size=22,
                 fill=GREY, stroke_width=0, text_anchor='middle', creation=6.3)
cross_lbl.fadeout(11.0, 11.5)
v.add(cross_lbl)

# SurroundingRectangle demo
target_text = Text(text='Highlighted!', x=1300, y=400, font_size=40,
                   fill=WHITE, stroke_width=0, text_anchor='middle', creation=6)
target_text.fadein(6.5, 7.0)
target_text.fadeout(11.0, 11.5)
v.add(target_text)

sr = SurroundingRectangle(target_text, buff=10, creation=6,
                          stroke=YELLOW, stroke_width=3, fill_opacity=0)
sr.fadein(7.5, 8.0)
sr.pulsate(start=8.5, end=10.5, scale_factor=1.1, n_pulses=3)
sr.fadeout(11.0, 11.5)
v.add(sr)

sr_lbl = Text(text='SurroundingRectangle(target, buff)', x=1300, y=550,
              font_size=22, fill=GREY, stroke_width=0, text_anchor='middle', creation=6.3)
sr_lbl.fadeout(11.0, 11.5)
v.add(sr_lbl)

# cross_out method
co_target = Text(text='Wrong!', x=500, y=750, font_size=40,
                 fill=WHITE, stroke_width=0, text_anchor='middle', creation=6)
co_target.fadein(6.5, 7.0)
co_cross = co_target.cross_out(start=8.0, end=8.5, color=RED)
co_target.fadeout(11.0, 11.5)
co_cross.fadeout(11.0, 11.5)
v.add(co_target)
v.add(co_cross)

co_lbl = Text(text='.cross_out()', x=500, y=850, font_size=22,
              fill=GREY, stroke_width=0, text_anchor='middle', creation=6.3)
co_lbl.fadeout(11.0, 11.5)
v.add(co_lbl)

# =============================================================================
# Phase 3 (12-18s): DimensionLine + LabeledLine + LabeledArrow
# =============================================================================
title3 = Text(text='Measurement & Labels', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title3.write(12, 12.5)
title3.fadeout(17.0, 17.5)
v.add(title3)

# DimensionLine
dim = DimensionLine((250, 400), (750, 400), label='500px', creation=12)
dim.fadein(12.5, 13.0)
dim.fadeout(17.0, 17.5)
v.add(dim)

dim_lbl = Text(text='DimensionLine(p1, p2, label)', x=500, y=500,
               font_size=22, fill=GREY, stroke_width=0, text_anchor='middle', creation=12.3)
dim_lbl.fadeout(17.0, 17.5)
v.add(dim_lbl)

# LabeledLine
ll = LabeledLine(x1=250, y1=650, x2=750, y2=650, label='distance',
                 creation=12)
ll.fadein(13.0, 13.5)
ll.fadeout(17.0, 17.5)
v.add(ll)

ll_lbl = Text(text='LabeledLine(x1, y1, x2, y2, label)', x=500, y=730,
              font_size=22, fill=GREY, stroke_width=0, text_anchor='middle', creation=12.3)
ll_lbl.fadeout(17.0, 17.5)
v.add(ll_lbl)

# LabeledArrow
la = LabeledArrow(x1=1100, y1=400, x2=1600, y2=400, label='force',
                  creation=12)
la.fadein(13.5, 14.0)
la.fadeout(17.0, 17.5)
v.add(la)

la_lbl = Text(text='LabeledArrow()', x=1350, y=500,
              font_size=22, fill=GREY, stroke_width=0, text_anchor='middle', creation=12.3)
la_lbl.fadeout(17.0, 17.5)
v.add(la_lbl)

# Brace
brace_target = Rectangle(300, 80, x=1100, y=650, fill=BLUE, fill_opacity=0.3,
                          stroke=BLUE, stroke_width=2, creation=12)
brace_target.fadein(13.0, 13.5)
brace_target.fadeout(17.0, 17.5)
v.add(brace_target)

br = Brace(brace_target, direction='down', creation=12)
br.fadein(14.0, 14.5)
br.fadeout(17.0, 17.5)
v.add(br)

br_lbl = Text(text='Brace(target, direction)', x=1350, y=820,
              font_size=22, fill=GREY, stroke_width=0, text_anchor='middle', creation=12.3)
br_lbl.fadeout(17.0, 17.5)
v.add(br_lbl)

# =============================================================================
# Phase 4 (18-24s): ArrowVectorField
# =============================================================================
title4 = Text(text='Arrow Vector Field', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title4.write(18, 18.5)
title4.fadeout(23.0, 23.5)
v.add(title4)

def vortex_field(x, y):
    cx, cy = 960, 540
    dx, dy = x - cx, y - cy
    return (-dy, dx)

avf = ArrowVectorField(vortex_field,
                       x_range=(200, 1720, 160),
                       y_range=(150, 930, 160),
                       max_length=60, creation=18,
                       stroke=BLUE, stroke_width=2)
avf.fadein(18.5, 19.5)
avf.fadeout(23.0, 23.5)
v.add(avf)

avf_lbl = Text(text='ArrowVectorField(func, x_range, y_range)', x=960, y=980,
               font_size=22, fill=GREY, stroke_width=0, text_anchor='middle', creation=18.3)
avf_lbl.fadeout(23.0, 23.5)
v.add(avf_lbl)

# =============================================================================
# Phase 5 (24-30s): Combinations
# =============================================================================
title5 = Text(text='Combined Annotations', x=960, y=60, font_size=48,
              fill=WHITE, stroke_width=0, text_anchor='middle')
title5.write(24, 24.5)
title5.fadeout(29.0, 29.5)
v.add(title5)

# A right triangle with all annotations
A = (400, 750)
B = (900, 750)
C = (900, 350)

combo_tri = Lines(A, B, C, A,
                  stroke=WHITE, stroke_width=3, fill_opacity=0, creation=24)
combo_tri.fadein(24.5, 25.0)
combo_tri.fadeout(29.0, 29.5)
v.add(combo_tri)

# Right angle at B
ra_combo = RightAngle(vertex=B, p1=(B[0] + 100, B[1]), p2=(B[0], B[1] - 100),
                      size=20, creation=24, stroke=YELLOW, stroke_width=2)
ra_combo.fadein(25.0, 25.5)
ra_combo.fadeout(29.0, 29.5)
v.add(ra_combo)

# Angle at A
angle_combo = Angle(vertex=A, p1=B, p2=C, radius=50,
                    label='t', creation=24, stroke=GREEN, stroke_width=2)
angle_combo.fadein(25.5, 26.0)
angle_combo.fadeout(29.0, 29.5)
v.add(angle_combo)

# Dimension lines for sides
dim_base = DimensionLine(A, B, label='adjacent', offset=40, creation=24)
dim_base.fadein(26.0, 26.5)
dim_base.fadeout(29.0, 29.5)
v.add(dim_base)

dim_height = DimensionLine(B, C, label='opposite', offset=40, creation=24)
dim_height.fadein(26.5, 27.0)
dim_height.fadeout(29.0, 29.5)
v.add(dim_height)

# Hypotenuse label
hyp = LabeledLine(x1=A[0], y1=A[1], x2=C[0], y2=C[1], label='hypotenuse',
                  font_size=20, label_buff=15, creation=24,
                  stroke=BLUE, stroke_width=2)
hyp.fadein(27.0, 27.5)
hyp.fadeout(29.0, 29.5)
v.add(hyp)

# Formula
formula = Text(text='tan(t) = opposite / adjacent', x=1400, y=550,
               font_size=36, fill=WHITE, stroke_width=0, text_anchor='middle', creation=24)
formula.typewrite(start=27.0, end=28.5)
formula.fadeout(29.0, 29.5)
v.add(formula)

# =============================================================================
# Display
# =============================================================================
v.browser_display(
        start=args.start or 0,
        end=args.end or T,
        fps=args.fps,
        port=args.port,
    )
