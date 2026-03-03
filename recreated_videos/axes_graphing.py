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
    fill='#A855F7', fill_opacity=0.3, stroke_width=0, z=1,
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

# Fade out phase 2 content
sin_curve.fadeout(7.8, 8.2)
cos_curve.fadeout(7.8, 8.2)
axes.fadeout(7.8, 8.2)
title.fadeout(7.8, 8.2)

# ── Add everything to canvas ────────────────────────────────────────
canvas.add(axes)
canvas.add(area_between, area_label)
canvas.add(riemann_label)

canvas.browser_display(
        start=args.start or 0,
        end=args.end,
        fps=args.fps, port=args.port,
        hot_reload=args.hot_reload,
    )
