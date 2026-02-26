"""Animated axis zoom and pan — showcasing animated Real ranges on Axes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
from vectormation import attributes
from vectormation import easings

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/axes_zoom')
canvas.set_background()

ax = Axes(x_range=(-5, 5), y_range=(-2, 26), x_label='x', y_label='y')

f = lambda x: x ** 2
curve = ax.plot(f, label='$f(x)=x^2$', stroke='#58C4DD', stroke_width=4)

# Draw the curve in
create_anim = curve.create(start=0, end=2)

# Zoom into x=[1, 4], y=[0, 18] to inspect the curve more closely
ax.set_ranges(3, 5, x_range=(1, 4), y_range=(0, 18))

# Add a shaded area that appears after zooming in
area = ax.get_area(f, x_range=(1.5, 3.5), fill='#58C4DD', fill_opacity=0.3)
area.fadein(5.5, 6.5)

# Zoom back out to full view
ax.set_ranges(7, 9, x_range=(-5, 5), y_range=(-2, 26))

# Pan to the right: shift window to x=[0, 10], y=[0, 100]
ax.set_ranges(10, 12, x_range=(0, 10), y_range=(0, 100))

# Add a dot tracking along the curve during the pan
dot = Dot(fill='#FFFF00')
x_val = attributes.Real(0, 2)
x_val.move_to(10, 14, 9)
dot.c.set_onward(10, ax.graph_position(f, x_val))
dot.fadein(10, 10.5)

canvas.add_objects(ax, create_anim, dot)
if args.verbose:
    canvas.export_video('docs/source/_static/videos/axes_zoom.mp4', fps=30, end_time=14)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True, end_time=14)
