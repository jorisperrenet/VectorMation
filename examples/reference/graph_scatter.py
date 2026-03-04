"""Scatter plot with regression line."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

ax = Axes(x_range=(0, 10), y_range=(0, 60))
ax.add_coordinates()
ax.add_grid()

x_data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
y_data = [5, 12, 10, 22, 25, 28, 35, 40, 50]
ax.plot_scatter(x_data, y_data, r=6, fill='#E74C3C')
ax.add_regression_line(x_data, y_data, stroke='#3498DB', stroke_width=3)

v.add(ax)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/graph_scatter.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=1)
