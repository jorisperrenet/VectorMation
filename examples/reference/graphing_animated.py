"""Animated sin + cos graph creation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import math
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

graph = Graph(math.sin, x_range=(-2 * math.pi, 2 * math.pi),
              y_range=(-1.5, 1.5))

# Draw sin curve
graph.curve.create(start=0, end=2)

# Add and draw cos curve
cos_curve = graph.add_function(math.cos, stroke='#FC6255')
cos_curve.create(start=2.5, end=4.5)

v.add(graph)
if args.for_docs:
    v.export_video('docs/source/_static/videos/graph_animated_ref.mp4', fps=30, end=5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
