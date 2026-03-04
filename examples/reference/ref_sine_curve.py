"""Simple sine curve on Graph axes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

g = Graph(math.sin, x_range=(-2 * math.pi, 2 * math.pi), y_range=(-1.5, 1.5))
g.add_coordinates()
g.add_grid()

v.add(g)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_sine_curve.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
