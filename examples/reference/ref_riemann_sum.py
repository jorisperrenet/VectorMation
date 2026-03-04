"""Riemann sum rectangles under a curve."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

func = lambda x: x**2
g = Graph(func, x_range=(0, 3), y_range=(0, 10))
g.add_coordinates()
g.add_grid()
rects = g.get_riemann_rectangles(func, (0, 3), dx=0.3,
                                  fill='#3498DB', fill_opacity=0.4)

v.add(g, rects)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_riemann_sum.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
