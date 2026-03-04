"""Animated tangent line sliding along a curve."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

func = lambda x: x ** 3 - 3 * x
g = Graph(func, x_range=(-3, 3), y_range=(-5, 5))
g.add_coordinates()
g.add_grid()
g.fadein(start=0, end=1)

tangent = g.animated_tangent_line(func, -2.5, 2.5, start=1, end=4,
                                  length=350, stroke='#E74C3C', stroke_width=4)
tangent.fadein(start=1, end=1.3)

v.add(g, tangent)
if args.for_docs:
    v.export_video('docs/source/_static/videos/tangent_line.mp4', fps=30, end=5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
