"""Axes zoom with animated ranges."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

ax = Axes(x_range=(-5, 5), y_range=(-2, 26))
curve = ax.plot(lambda x: x ** 2, stroke='#58C4DD')

# Zoom into x=[1, 4], y=[0, 18]
ax.set_ranges((1, 4), (0, 18), start=0, end=2)

v.add(ax)
if args.for_docs:
    v.export_video('docs/source/_static/videos/graph_zoom.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
