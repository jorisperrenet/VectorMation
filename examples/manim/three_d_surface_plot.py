"""Manim equivalent: ThreeDSurfacePlot -- Gaussian surface on 3D axes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/three_d_surface_plot')
canvas.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(0, 1.5))

sigma = 0.4
def gaussian(x, y):
    d2 = x * x + y * y
    return math.exp(-d2 / (2.0 * sigma * sigma))

axes.plot_surface(gaussian, resolution=(24, 24),
                  checkerboard_colors=('#FF862F', '#4488ff'),
                  stroke_color='#225588', stroke_width=0.3,
                  fill_opacity=0.85)

canvas.add_objects(axes)
if args.verbose:
    canvas.write_frame(0, 'docs/source/_static/videos/three_d_surface_plot.svg')
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
