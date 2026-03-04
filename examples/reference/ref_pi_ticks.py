"""Pi-formatted tick labels on a sine graph."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

ax = Axes(x_range=(-2 * math.pi, 2 * math.pi), y_range=(-1.5, 1.5),
          x_tick_type='pi')
ax.plot(math.sin, stroke='#58C4DD', stroke_width=3)
ax.add_coordinates()
ax.add_grid()

v.add(ax)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_pi_ticks.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
