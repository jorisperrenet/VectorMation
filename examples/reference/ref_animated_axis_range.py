"""Animated axis range zoom."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

g = Graph(math.sin, x_range=(-5, 5), y_range=(-2, 2))
g.add_coordinates()
g.add_grid()
g.fadein(start=0, end=0.5)
g.animate_range(start=1, end=3, x_range=(-1, 1), y_range=(-1.5, 1.5))

v.add(g)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_animated_axis_range.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
