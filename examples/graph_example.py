import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from vectormation.objects import *
args = parse_args()
import math

# Initialize the animation frame
canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/graph_example')
canvas.set_background()

# Plot sin(x) on [-2pi, 2pi]
graph = Graph(math.sin, x_range=(-2 * math.pi, 2 * math.pi),
              y_range=(-1.5, 1.5), x_label='x', y_label='sin(x)')

canvas.add_objects(graph)
if not args.no_display:
    canvas.browser_display(end=0, fps=args.fps, port=args.port, hot_reload=True)
