"""FunctionGraph with draw_along animation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import math
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

curve = FunctionGraph(math.sin, x_range=(0, 2 * math.pi),
                      width=600, height=300, x=200, y=350)
curve.draw_along(start=0, end=2)

v.add(curve)
if args.for_docs:
    v.export_video('docs/source/_static/videos/graph_functiongraph.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
