"""Line graph from data points."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

ax = Axes(x_range=(0, 10), y_range=(0, 100))
ax.add_coordinates()
ax.add_grid()
ax.plot_line_graph([1, 3, 5, 7, 9], [20, 45, 30, 80, 60], stroke='#E74C3C', stroke_width=3)

v.add(ax)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_line_graph_data.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
