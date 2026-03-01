"""Formatters & Utility Demo — showcasing tick formatters, MorphObject, and TexCountAnimation.

Demonstrates: pi_tex_format, scientific_format, engineering_format, percent_format,
degree_format, MorphObject, TexCountAnimation.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/formatters_demo')
canvas.set_background()
T = 24.0

# -- Colors -------------------------------------------------------------------
WHITE = '#FFFFFF'
ACCENT = '#58C4DD'
YELLOW = '#FFFF00'
GREEN = '#83C167'
RED = '#FC6255'
ORANGE = '#F5A623'
PINK = '#FF79C6'
GRAY = '#888888'

# =============================================================================
# Phase 1 (0-4s): Pi TeX Format — trig function with pi-labeled x-axis
# =============================================================================

phase1_title = Text(
    text='pi_tex_format — Trig Axes', x=960, y=55, font_size=38,
    fill=WHITE, stroke_width=0, text_anchor='middle', creation=0,
)
phase1_title.fadein(0.0, 0.4)
phase1_title.fadeout(3.5, 4.0)
canvas.add(phase1_title)

ax_pi = Axes(
    x_range=(-math.pi, math.pi), y_range=(-1.5, 1.5),
    x=260, y=120, plot_width=1400, plot_height=400,
    x_tick_type='pi_tex', show_grid=True,
    x_label='$x$', y_label='$y$',
    creation=0,
)
ax_pi.fadein(0.0, 0.8)

sin_curve = ax_pi.plot(math.sin, stroke=ACCENT, stroke_width=4, creation=0.5)
sin_curve.draw_along(0.5, 2.0)

cos_curve = ax_pi.plot(math.cos, stroke=PINK, stroke_width=4, creation=1.2)
cos_curve.draw_along(1.2, 2.5)

legend_pi = ax_pi.add_legend([('sin(x)', ACCENT), ('cos(x)', PINK)], creation=1.5)

canvas.add(ax_pi)

# Degree format below — angles in radians on x-axis shown as degrees
ax_deg = Axes(
    x_range=(0, 2 * math.pi), y_range=(-1.2, 1.2),
    x=260, y=580, plot_width=1400, plot_height=400,
    x_tick_type='degree', show_grid=True,
    x_label='$\\theta$',
    creation=0,
)
ax_deg.fadein(0.0, 0.8)

sin_deg = ax_deg.plot(math.sin, stroke=GREEN, stroke_width=4, creation=1.0)
sin_deg.draw_along(1.0, 2.5)

deg_label = Text(
    text='degree_format — Angle Axis', x=960, y=570, font_size=28,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=0.5,
)
deg_label.fadein(0.5, 0.9)
deg_label.fadeout(3.5, 4.0)
canvas.add(deg_label)

canvas.add(ax_deg)

# Fade out phase 1
ax_pi.fadeout(3.5, 4.0)
ax_deg.fadeout(3.5, 4.0)

# =============================================================================
# Phase 2 (4-8s): Scientific & Engineering Formats
# =============================================================================

phase2_title = Text(
    text='scientific_format & engineering_format', x=960, y=55, font_size=38,
    fill=WHITE, stroke_width=0, text_anchor='middle', creation=4,
)
phase2_title.fadein(4.0, 4.4)
phase2_title.fadeout(7.5, 8.0)
canvas.add(phase2_title)

# Scientific format — exponential growth
ax_sci = Axes(
    x_range=(0, 5), y_range=(0, 100000),
    x=260, y=120, plot_width=1400, plot_height=400,
    y_tick_type='scientific', show_grid=True,
    x_label='$t$', y_label='$N$',
    creation=4,
)
ax_sci.fadein(4.0, 4.6)

def exponential(x):
    return 100 * math.exp(x * 2.3)

exp_curve = ax_sci.plot(exponential, stroke=ORANGE, stroke_width=4, creation=4.5)
exp_curve.draw_along(4.5, 6.0)

sci_label = Text(
    text='Y-axis: scientific notation (2.5x10\u00b3)', x=960, y=115, font_size=24,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=4.3,
)
sci_label.fadein(4.3, 4.7)
sci_label.fadeout(7.5, 8.0)
canvas.add(sci_label)

canvas.add(ax_sci)

# Engineering format — SI prefixes
ax_eng = Axes(
    x_range=(0, 10), y_range=(0, 5000),
    x=260, y=580, plot_width=1400, plot_height=400,
    y_tick_type='engineering', show_grid=True,
    x_label='$f$', y_label='$P$',
    creation=4,
)
ax_eng.fadein(4.0, 4.6)

def power_curve(x):
    return 5 * x ** 3

eng_curve = ax_eng.plot(power_curve, stroke=YELLOW, stroke_width=4, creation=5.0)
eng_curve.draw_along(5.0, 6.5)

eng_label = Text(
    text='Y-axis: engineering format (1k, 2k, ...)', x=960, y=575, font_size=24,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=4.3,
)
eng_label.fadein(4.3, 4.7)
eng_label.fadeout(7.5, 8.0)
canvas.add(eng_label)

canvas.add(ax_eng)

ax_sci.fadeout(7.5, 8.0)
ax_eng.fadeout(7.5, 8.0)

# =============================================================================
# Phase 3 (8-12s): Percent Format
# =============================================================================

phase3_title = Text(
    text='percent_format — Probability Axes', x=960, y=55, font_size=38,
    fill=WHITE, stroke_width=0, text_anchor='middle', creation=8,
)
phase3_title.fadein(8.0, 8.4)
phase3_title.fadeout(11.5, 12.0)
canvas.add(phase3_title)

ax_pct = Axes(
    x_range=(0, 10), y_range=(0, 1),
    x=260, y=180, plot_width=1400, plot_height=700,
    y_tick_type='percent', show_grid=True,
    x_label='$x$', y_label='$P(x)$',
    creation=8,
)
ax_pct.fadein(8.0, 8.6)

def sigmoid(x):
    return 1 / (1 + math.exp(-(x - 5)))

sig_curve = ax_pct.plot(sigmoid, stroke=ACCENT, stroke_width=4, creation=8.5)
sig_curve.draw_along(8.5, 10.0)

# Add a horizontal line at 50% (from x=10 to y_val=0.5)
h_line = ax_pct.get_horizontal_line(10, 0.5, stroke=RED, stroke_dasharray='8,4',
                                     stroke_width=2, creation=9.5)
h_line.fadein(9.5, 10.0)

pct_note = Text(
    text='50% threshold', x=ax_pct.plot_x + ax_pct.plot_width - 100,
    y=ax_pct._math_to_svg_y(0.5, 9.5) - 15,
    font_size=22, fill=RED, stroke_width=0, text_anchor='end', creation=9.5,
)
pct_note.fadein(9.5, 10.2)
pct_note.fadeout(11.5, 12.0)
canvas.add(pct_note)

canvas.add(ax_pct)

ax_pct.fadeout(11.5, 12.0)

# =============================================================================
# Phase 4 (12-16s): Custom tick_format — lambda formatter
# =============================================================================

phase4_title = Text(
    text='Custom tick_format via lambda', x=960, y=55, font_size=38,
    fill=WHITE, stroke_width=0, text_anchor='middle', creation=12,
)
phase4_title.fadein(12.0, 12.4)
phase4_title.fadeout(15.5, 16.0)
canvas.add(phase4_title)

# Custom formatter: show values as fractions of tau
ax_custom = Axes(
    x_range=(0, 8), y_range=(0, 100),
    x=260, y=180, plot_width=1400, plot_height=700,
    x_tick_format=lambda v: f'{v:.0f} hrs',
    y_tick_format=lambda v: f'${v:.0f}',
    show_grid=True,
    x_label='Time', y_label='Revenue',
    creation=12,
)
ax_custom.fadein(12.0, 12.6)

def revenue(x):
    return 3 * x ** 2 - 5 * x + 20

rev_curve = ax_custom.plot(revenue, stroke=GREEN, stroke_width=4, creation=12.5)
rev_curve.draw_along(12.5, 14.0)

# Shade area under the curve
area = ax_custom.get_area(revenue, x_range=(1, 7), fill=GREEN, fill_opacity=0.2,
                           creation=13.5)
area.fadein(13.5, 14.0)

custom_note = Text(
    text='x: "N hrs"    y: "$N"', x=960, y=160, font_size=24,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=12.3,
)
custom_note.fadein(12.3, 12.7)
custom_note.fadeout(15.5, 16.0)
canvas.add(custom_note)

canvas.add(ax_custom)

ax_custom.fadeout(15.5, 16.0)

# =============================================================================
# Phase 5 (16-20s): MorphObject
# =============================================================================

phase5_title = Text(
    text='MorphObject — Shape Morphing', x=960, y=55, font_size=38,
    fill=WHITE, stroke_width=0, text_anchor='middle', creation=16,
)
phase5_title.fadein(16.0, 16.4)
phase5_title.fadeout(19.5, 20.0)
canvas.add(phase5_title)

# Morph a circle into a square
circle_src = Circle(r=100, cx=960, cy=400, fill=ACCENT, fill_opacity=0.8,
                    stroke=ACCENT, stroke_width=3, creation=16)
circle_src.fadein(16.0, 16.5)

square_dst = Rectangle(200, 200, x=960, y=400, fill=ORANGE, fill_opacity=0.8,
                        stroke=ORANGE, stroke_width=3, creation=16)

morph1 = MorphObject(circle_src, square_dst, start=17.0, end=18.5)

morph1_label = Text(
    text='Circle -> Square', x=960, y=560, font_size=28,
    fill=WHITE, stroke_width=0, text_anchor='middle', creation=16.5,
)
morph1_label.fadein(16.5, 16.8)
morph1_label.fadeout(19.0, 19.5)
canvas.add(morph1_label)

# Morph a star into a triangle
star = Star(5, outer_radius=80, cx=400, cy=750, fill=YELLOW, fill_opacity=0.7,
            stroke=YELLOW, stroke_width=3, creation=16)
star.fadein(16.0, 16.5)

triangle = RegularPolygon(3, radius=90, cx=400, cy=750, fill=GREEN, fill_opacity=0.7,
                           stroke=GREEN, stroke_width=3, creation=16)

morph2 = MorphObject(star, triangle, start=17.0, end=18.5, rotation_degrees=120)

morph2_label = Text(
    text='Star -> Triangle (with rotation)', x=400, y=880, font_size=22,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=16.5,
)
morph2_label.fadein(16.5, 16.8)
morph2_label.fadeout(19.0, 19.5)
canvas.add(morph2_label)

# Morph text
text_from = Text(text='Hello', x=1500, y=750, font_size=64,
                 fill=WHITE, stroke_width=0, text_anchor='middle', creation=16)
text_from.fadein(16.0, 16.5)

text_to = Text(text='World', x=1500, y=750, font_size=64,
               fill=PINK, stroke_width=0, text_anchor='middle', creation=16)

morph3 = MorphObject(text_from, text_to, start=17.0, end=18.5)

morph3_label = Text(
    text='Text morphing', x=1500, y=880, font_size=22,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=16.5,
)
morph3_label.fadein(16.5, 16.8)
morph3_label.fadeout(19.0, 19.5)
canvas.add(morph3_label)

canvas.add(circle_src, square_dst, morph1)
canvas.add(star, triangle, morph2)
canvas.add(text_from, text_to, morph3)

# Fade remaining objects
square_dst.fadeout(19.0, 19.5)
triangle.fadeout(19.0, 19.5)
text_to.fadeout(19.0, 19.5)

# =============================================================================
# Phase 6 (20-24s): TexCountAnimation
# =============================================================================

phase6_title = Text(
    text='TexCountAnimation — Animated Numbers', x=960, y=55, font_size=38,
    fill=WHITE, stroke_width=0, text_anchor='middle', creation=20,
)
phase6_title.fadein(20.0, 20.4)
phase6_title.fadeout(23.5, 24.0)
canvas.add(phase6_title)

# Counter: 0 -> 1000
counter_label = Text(
    text='Count:', x=400, y=350, font_size=36,
    fill=GRAY, stroke_width=0, text_anchor='end', creation=20,
)
counter_label.fadein(20.0, 20.4)
counter_label.fadeout(23.5, 24.0)
canvas.add(counter_label)

counter = TexCountAnimation(
    start_val=0, end_val=1000, start=20.5, end=22.5,
    fmt='{:.0f}', x=430, y=350, font_size=48,
    fill=WHITE, creation=20,
)
counter.fadeout(23.5, 24.0)
canvas.add(counter)

# Decimal counter: 0.00 -> 3.14
dec_label = Text(
    text='Pi approx:', x=400, y=480, font_size=36,
    fill=GRAY, stroke_width=0, text_anchor='end', creation=20,
)
dec_label.fadein(20.0, 20.4)
dec_label.fadeout(23.5, 24.0)
canvas.add(dec_label)

pi_counter = TexCountAnimation(
    start_val=0, end_val=3.14, start=20.5, end=22.5,
    fmt='{:.2f}', x=430, y=480, font_size=48,
    fill=ACCENT, creation=20,
)
pi_counter.fadeout(23.5, 24.0)
canvas.add(pi_counter)

# Counter with count_to: demonstrates chaining
chain_label = Text(
    text='Chained:', x=400, y=610, font_size=36,
    fill=GRAY, stroke_width=0, text_anchor='end', creation=20,
)
chain_label.fadein(20.0, 20.4)
chain_label.fadeout(23.5, 24.0)
canvas.add(chain_label)

chain_counter = TexCountAnimation(
    start_val=0, end_val=50, start=20.5, end=21.5,
    fmt='{:.0f}', x=430, y=610, font_size=48,
    fill=YELLOW, creation=20,
)
chain_counter.count_to(100, start=21.5, end=22.5)
chain_counter.count_to(75, start=22.5, end=23.2)
chain_counter.fadeout(23.5, 24.0)
canvas.add(chain_counter)

# Summary note
summary = Text(
    text='Formatters: pi_tex, degree, scientific, engineering, percent, custom lambda',
    x=960, y=800, font_size=24,
    fill=GRAY, stroke_width=0, text_anchor='middle', creation=20.5,
)
summary.fadein(20.5, 21.0)
summary.fadeout(23.5, 24.0)
canvas.add(summary)

# =============================================================================
# Display
# =============================================================================

if not args.no_display:
    canvas.browser_display(start=args.start or 0, end=args.end or T,
                           fps=args.fps, port=args.port)
