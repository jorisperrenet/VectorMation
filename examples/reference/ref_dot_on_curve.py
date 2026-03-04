"""Dot following a curve using graph_position."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

func = math.sin
g = Graph(func, x_range=(-2 * math.pi, 2 * math.pi), y_range=(-1.5, 1.5))
g.add_coordinates()
g.add_grid()
g.fadein(start=0, end=0.5)

from vectormation import attributes
x_val = attributes.Real(-2 * math.pi, -2 * math.pi)
x_val.move_to(0, 3, 2 * math.pi)

dot = Dot(r=10, fill='#E74C3C', z=5, creation=0.5)
dot.c.set_onward(0.5, g.graph_position(func, x_val))

v.add(g, dot)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_dot_on_curve.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
