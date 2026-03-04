"""FunctionGraph shape."""
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

g = Graph(math.sin, x_range=(-2*math.pi, 2*math.pi), y_range=(-1.5, 1.5))
v.add(g)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_function_graph.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
