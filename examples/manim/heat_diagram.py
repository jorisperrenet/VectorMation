"""Manim equivalent: HeatDiagramPlot -- line graph from discrete data points."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/heat_diagram')
canvas.set_background()
ax = Axes(x_range=(0, 40), y_range=(-8, 32),
          x_label=r'$\Delta Q$', y_label=r'$T[^\circ C]$')

x_vals = [0, 8, 38, 39]
y_vals = [20, 0, 0, -5]
graph = ax.plot_line_graph(x_vals, y_vals, stroke='#FFFF00')
canvas.add_objects(ax)
if args.verbose:
    canvas.write_frame(0, 'docs/source/_static/videos/heat_diagram.svg')
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
