"""Basic Axes with labels and a plotted function."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
ax.add_coordinates()
ax.add_grid()
ax.plot(math.sin, stroke='#3498DB', stroke_width=3)
ax.plot(math.cos, stroke='#E74C3C', stroke_width=3)

v.add(ax)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_axes_basic.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
