"""Network graph and tree visualization example."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import (
    VectorMathAnim, NetworkGraph, Tree, FlowChart, Legend,
    parse_args,
)

args = parse_args()
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/network_tree')

# Network graph (left side)
graph = NetworkGraph(
    nodes={0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E'},
    edges=[(0, 1), (0, 2), (1, 3), (2, 3), (3, 4), (1, 4, '5')],
    cx=350, cy=350, radius=200, directed=True,
)
graph.write(0, 1.5)
canvas.add(graph)

# Tree (right side)
tree = Tree(
    {'CEO': {'CTO': {'Dev': {}, 'QA': {}}, 'CFO': {'Acct': {}}}},
    cx=1500, cy=120, h_spacing=150, v_spacing=120,
)
tree.write(1.5, 3)
canvas.add(tree)

# FlowChart (bottom)
flow = FlowChart(['Input', 'Process', 'Review', 'Output'],
                 x=400, y=700, box_width=180, spacing=60)
flow.write(3, 4.5)
canvas.add(flow)

# Legend
legend = Legend([('#58C4DD', 'Network'), ('#83C167', 'Tree'), ('#FF6B6B', 'Flow')],
               x=50, y=50)
legend.fadein(0, 0.5)
canvas.add(legend)

# Highlight animation
graph.highlight_node(3, start=4.5, end=5.5)
tree.highlight_node('CTO', start=5, end=6)

if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port)
