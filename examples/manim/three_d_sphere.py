"""Manim equivalent: ThreeDLightSourcePosition -- sphere on 3D axes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/three_d_sphere')
canvas.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-3, 3))

sphere = Sphere3D(radius=1.5, fill_color='#FC6255',
                  checkerboard_colors=('#FC6255', '#c44030'),
                  resolution=(16, 32), fill_opacity=0.9)
axes.add_surface(sphere)

canvas.add_objects(axes)
if args.verbose:
    canvas.write_frame(0, 'docs/source/_static/videos/three_d_sphere.svg')
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
