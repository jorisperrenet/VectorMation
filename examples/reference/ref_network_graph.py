"""NetworkGraph with nodes and edges."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

graph = NetworkGraph(
    nodes={0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E'},
    edges=[(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (1, 4)],
    radius=250,
    directed=True,
)

v.add(graph)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_network_graph.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
