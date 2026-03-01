"""Coordinate System — showcasing the Axes class features.

Demonstrates: axes creation animation, sine + parabola plots, shaded area under
a curve, animated axis range change, grid, labels, and a tangent line.
"""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
import math

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/coordinate_system')
canvas.set_background()

# ── Functions ────────────────────────────────────────────────────────
def sine(x):
    return math.sin(x)

def parabola(x):
    return 0.15 * x * x

# ── Phase 1 (0–2s): Create axes with grid + title ───────────────────
axes = Axes(
    x_range=(-4, 4, 1), y_range=(-2, 3, 1),
    x=260, y=80, plot_width=1400, plot_height=880,
    show_grid=True, creation=0,
)
axes.fadein(0, 1.5)

title = axes.add_title('Coordinate System Demo', font_size=36, creation=0)
title.fadein(0, 1.0)

# ── Phase 2 (1.5–4s): Plot sine and parabola ────────────────────────
sine_curve = axes.plot(sine, stroke='#58C4DD', stroke_width=4, creation=1.5)
sine_curve.draw_along(1.5, 3.0)

parabola_curve = axes.plot(parabola, stroke='#FF79C6', stroke_width=4, creation=2.5)
parabola_curve.draw_along(2.5, 4.0)

# Function labels
sine_label = Text(
    text='sin(x)', x=1580, y=280,
    font_size=28, fill='#58C4DD', stroke_width=0, text_anchor='middle',
    creation=3.0,
)
sine_label.fadein(3.0, 3.5)

parabola_label = Text(
    text='0.15x\u00b2', x=1580, y=330,
    font_size=28, fill='#FF79C6', stroke_width=0, text_anchor='middle',
    creation=4.0,
)
parabola_label.fadein(4.0, 4.5)

# ── Phase 3 (4.5–6.5s): Shaded area under sine ─────────────────────
area = axes.get_area(
    sine, x_range=(0, math.pi),
    fill='#58C4DD', fill_opacity=0.3, stroke_width=0, z=-1,
)
area.set_opacity(0, start=0)
area.set_opacity(1, start=4.5, end=5.5)

area_label = Text(
    text='Area under sin(x), 0 to \u03c0',
    x=960, y=1010,
    font_size=22, fill='#aaa', stroke_width=0, text_anchor='middle',
    creation=5.0,
)
area_label.fadein(5.0, 5.5)
area_label.fadeout(6.0, 6.5)

# ── Phase 4 (6.5–8.5s): Tangent line sliding along the sine curve ──
tangent = axes.animated_tangent_line(
    sine, x_start=-3, x_end=3,
    start=6.5, end=8.5,
    length=250, creation=6.5, z=2,
    stroke='#FFFF00', stroke_width=3,
)
tangent.fadein(6.5, 7.0)
tangent.fadeout(8.2, 8.5)

tangent_label = Text(
    text='Tangent line', x=1580, y=380,
    font_size=22, fill='#FFFF00', stroke_width=0, text_anchor='middle',
    creation=6.5,
)
tangent_label.fadein(6.5, 7.0)
tangent_label.fadeout(8.2, 8.5)

# ── Phase 5 (8.5–10.5s): Animate the axis range ────────────────────
# Fade out the area before the range changes
area.set_opacity(0, start=8.0, end=8.5)

# Zoom into the interesting region around the origin
axes.animate_range(8.5, 10.0, x_range=(-2, 2), y_range=(-1.5, 1.5))

zoom_label = Text(
    text='Zooming in...', x=960, y=1010,
    font_size=24, fill='#ccc', stroke_width=0, text_anchor='middle',
    creation=8.5,
)
zoom_label.fadein(8.5, 9.0)
zoom_label.fadeout(10.0, 10.5)

# ── Phase 6 (10.5–12s): Zoom back out and add legend ────────────────
axes.animate_range(10.5, 11.5, x_range=(-4, 4), y_range=(-2, 3))

legend = axes.add_legend(
    entries=[('sin(x)', '#58C4DD'), ('0.15x\u00b2', '#FF79C6')],
    position='upper right', font_size=20, creation=10.5, z=10,
)
legend.fadein(10.5, 11.0)

# ── Add everything to canvas ────────────────────────────────────────
canvas.add(axes)
canvas.add(sine_label, parabola_label)
canvas.add(area, area_label)
canvas.add(tangent_label, zoom_label)

if not args.no_display:
    canvas.browser_display(
        start=args.start or 0,
        end=args.end or 12,
        fps=args.fps, port=args.port,
        hot_reload=args.hot_reload,
    )
