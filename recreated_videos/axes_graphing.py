"""Axes Graphing Demo — showcasing Axes and graphing features.

Demonstrates: function plotting, area shading, tangent lines, Riemann rectangles,
animated axis ranges, legends, polar curves, and NumberLine with pointer.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/axes_graphing')
canvas.set_background()

# ── Functions ────────────────────────────────────────────────────────
def sine(x):
    return math.sin(x)

def cosine(x):
    return math.cos(x)

def quadratic(x):
    return 0.25 * x * x - 1

# =====================================================================
# Phase 1 (0-4s): Basic Axes with Functions
# =====================================================================

# Create axes
axes = Axes(
    x_range=(-4, 4), y_range=(-3, 3),
    x=260, y=100, plot_width=1400, plot_height=880,
    show_grid=True, creation=0,
)
axes.fadein(0, 1.0)

# Title
title = axes.add_title('Axes & Graphing Showcase', font_size=36, creation=0)
title.fadein(0, 0.8)

# Add coordinate labels
axes.add_coordinates(creation=0)

# Plot sin(x) - draw it along from left to right
sin_curve = axes.plot(sine, stroke='#58C4DD', stroke_width=4, creation=0.5)
sin_curve.draw_along(0.5, 2.0)

# Plot cos(x) with a different color
cos_curve = axes.plot(cosine, stroke='#FF79C6', stroke_width=4, creation=1.5)
cos_curve.draw_along(1.5, 3.0)

# Animate axis range change (zoom in slightly)
axes.animate_range(3.0, 4.0, x_range=(-3, 3), y_range=(-2, 2))

# =====================================================================
# Phase 2 (4-8s): Advanced Features
# =====================================================================

# Zoom back out for the advanced features
axes.animate_range(4.0, 4.5, x_range=(-4, 4), y_range=(-3, 3))

# Get area between sin and cos curves
area_between = axes.get_area(
    sine, bounded_graph=cosine,
    x_range=(-math.pi / 2, math.pi / 2),
    fill='#A855F7', fill_opacity=0.3, stroke_width=0, z=-1,
    creation=4.5,
)
area_between.set_opacity(0, start=0)
area_between.set_opacity(1, start=4.5, end=5.5)

area_label = Text(
    text='Area between curves',
    x=960, y=1010,
    font_size=22, fill='#A855F7', stroke_width=0, text_anchor='middle',
    creation=4.5,
)
area_label.fadein(4.5, 5.0)
area_label.fadeout(5.8, 6.2)

# Tangent line sliding along the sine curve
tangent = axes.animated_tangent_line(
    sine, x_start=-3, x_end=3,
    start=5.5, end=7.0,
    length=250, creation=5.5, z=2,
    stroke='#FFFF00', stroke_width=3,
)
tangent.fadein(5.5, 5.8)
tangent.fadeout(6.8, 7.2)

# Fade out the area between
area_between.set_opacity(0, start=6.0, end=6.5)

# Add legend
legend = axes.add_legend(
    entries=[('sin(x)', '#58C4DD'), ('cos(x)', '#FF79C6')],
    position='upper right', font_size=20, creation=5.5, z=10,
)
legend.fadein(5.5, 6.0)

# Riemann rectangles for sin(x) on [0, pi]
riemann = axes.get_riemann_rectangles(
    sine, x_range=(0, math.pi), dx=0.3,
    fill='#58C4DD', fill_opacity=0.4, stroke='#fff', stroke_width=1,
    creation=6.5, z=-1,
)
riemann.fadein(6.5, 7.0)

riemann_label = Text(
    text='Riemann sum approximation',
    x=960, y=1010,
    font_size=22, fill='#58C4DD', stroke_width=0, text_anchor='middle',
    creation=6.8,
)
riemann_label.fadein(6.8, 7.2)
riemann_label.fadeout(7.6, 8.0)

# Fade out Riemann rectangles and legend before phase 3
riemann.fadeout(7.5, 8.0)
legend.fadeout(7.5, 8.0)

# =====================================================================
# Phase 3 (8-12s): Polar plot and NumberLine
# =====================================================================

# Fade out phase 2 content
sin_curve.fadeout(7.8, 8.2)
cos_curve.fadeout(7.8, 8.2)
axes.fadeout(7.8, 8.3)
title.fadeout(7.8, 8.2)

# -- Polar axes with a rose curve (top half) --
polar = PolarAxes(
    cx=500, cy=500,
    max_radius=300, r_range=(0, 4),
    n_rings=4, n_sectors=12,
    creation=8.3,
)
polar.fadein(8.3, 8.8)

# Plot a rose curve: r = 3 * cos(2*theta)
def rose(theta_deg):
    theta = math.radians(theta_deg)
    return 3 * abs(math.cos(2 * theta))

rose_curve = polar.plot_polar(rose, theta_range=(0, 360), num_points=300,
                               creation=8.3, stroke='#FF6B6B', stroke_width=3)
rose_curve.draw_along(8.5, 10.0)

polar_title = Text(
    text='Polar: r = 3|cos(2\u03b8)|',
    x=500, y=870,
    font_size=24, fill='#FF6B6B', stroke_width=0, text_anchor='middle',
    creation=8.5,
)
polar_title.fadein(8.5, 9.0)

# -- Number line with animated pointer (bottom right) --
nline = NumberLine(
    x_range=(-5, 5, 1), length=600,
    x=1050, y=750,
    include_arrows=True, include_numbers=True,
    creation=8.3,
)
nline.fadein(8.3, 8.8)

nline_title = Text(
    text='NumberLine with Pointer',
    x=1350, y=680,
    font_size=24, fill='#ddd', stroke_width=0, text_anchor='middle',
    creation=8.3,
)
nline_title.fadein(8.3, 8.8)

# Add a pointer that will animate along the number line
import vectormation.attributes as attributes
ptr_value = attributes.Real(8.5, -4)
pointer = nline.add_pointer(ptr_value, label='x', color='#FFFF00', creation=8.5)
pointer.fadein(8.5, 9.0)

# Animate the pointer from -4 to 4
ptr_value.move_to(9.0, 11.0, 4)

# Highlight a range on the number line
highlight = nline.highlight_range(-2, 2, color='#58C4DD', opacity=0.3, creation=9.5)
highlight.fadein(9.5, 10.0)

hl_label = Text(
    text='[-2, 2]',
    x=1350, y=820,
    font_size=20, fill='#58C4DD', stroke_width=0, text_anchor='middle',
    creation=9.5,
)
hl_label.fadein(9.5, 10.0)

# Add dots at key points
dot_neg = nline.add_dot_at(-2, color='#83C167', radius=6, creation=9.5)
dot_neg.fadein(9.5, 10.0)
dot_pos = nline.add_dot_at(2, color='#83C167', radius=6, creation=9.5)
dot_pos.fadein(9.5, 10.0)

# -- Small Axes in upper right with a quadratic function --
small_axes = Axes(
    x_range=(-3, 3), y_range=(-2, 3),
    x=1050, y=100, plot_width=550, plot_height=400,
    show_grid=True, creation=8.3,
)
small_axes.fadein(8.3, 8.8)

quad_curve = small_axes.plot(quadratic, stroke='#83C167', stroke_width=3, creation=8.5)
quad_curve.draw_along(8.5, 10.0)

# Add area under the quadratic
quad_area = small_axes.get_area(
    quadratic, x_range=(-2, 2),
    fill='#83C167', fill_opacity=0.25, stroke_width=0, z=-1,
    creation=10.0,
)
quad_area.set_opacity(0, start=0)
quad_area.set_opacity(1, start=10.0, end=10.8)

# Cursor moving along the quadratic
cursor = small_axes.add_cursor(
    quadratic, x_start=-2.5, x_end=2.5,
    start=10.5, end=12.0,
    r=5, fill='#FFFF00', creation=10.5, z=5,
)

small_title = Text(
    text='f(x) = 0.25x\u00b2 - 1',
    x=1325, y=530,
    font_size=20, fill='#83C167', stroke_width=0, text_anchor='middle',
    creation=8.5,
)
small_title.fadein(8.5, 9.0)

# ── Add everything to canvas ────────────────────────────────────────
canvas.add(axes)
canvas.add(area_between, area_label)
canvas.add(riemann_label)
canvas.add(polar, rose_curve, polar_title)
canvas.add(nline, nline_title, pointer, highlight, hl_label, dot_neg, dot_pos)
canvas.add(small_axes, small_title)

if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or 12,
        fps=args.fps, port=args.port,
        hot_reload=args.hot_reload,
    )
