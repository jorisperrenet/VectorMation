"""Manim equivalent: ArgMinExample -- dot moving along a parabola to its minimum."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
from vectormation import easings, attributes
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/arg_min')
canvas.set_background()
ax = Axes(x_range=(0, 10), y_range=(0, 55))

func = lambda x: 2 * (x - 5) ** 2
curve = ax.plot(func, stroke='#C55F73')

# Dot that travels along the curve to the minimum using graph_position
dot = Dot(fill='#FFFF00')
x_val = attributes.Real(0, 0)
x_val.move_to(0, 3, 5, easing=easings.smooth)
dot.c.set_onward(0, ax.graph_position(func, x_val))

canvas.add_objects(ax, dot)
if args.verbose:
    canvas.export_video('docs/source/_static/videos/arg_min.mp4', fps=30, end_time=3)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
