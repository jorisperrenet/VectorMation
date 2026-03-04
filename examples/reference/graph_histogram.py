"""Histogram from data."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import random
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

random.seed(42)
data = [random.gauss(5, 1.5) for _ in range(200)]

ax = Axes(x_range=(0, 10), y_range=(0, 50))
ax.add_coordinates()
ax.plot_histogram(data, bins=15, fill='#3498DB', fill_opacity=0.7)
ax.add_title('Normal Distribution (n=200)')

v.add(ax)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/graph_histogram.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=1)
