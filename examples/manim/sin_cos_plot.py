"""Manim equivalent: SinAndCosFunctionPlot -- sin and cos on axes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/sin_cos_plot')
canvas.set_background()
axes = Axes(x_range=(-2 * math.pi, 2 * math.pi), y_range=(-1.5, 1.5),
            x_label='x', y_label='y')
axes.add_function(math.sin, label=r'$\sin(x)$', stroke='#58C4DD')
axes.add_function(math.cos, label=r'$\cos(x)$', stroke='#FC6255')

canvas.add_objects(axes)
if args.for_docs:
    canvas.write_frame(0, 'docs/source/_static/videos/sin_cos_plot.svg')
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
