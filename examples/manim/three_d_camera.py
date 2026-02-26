"""Demonstrate 3D camera rotation animation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/three_d_camera')
canvas.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-3, 3))

# Add a filled surface
def saddle(x, y):
    return (x**2 - y**2) / 6

axes.plot_surface(saddle, resolution=(20, 20),
                  fill_color='#58C4DD', fill_opacity=0.8)

# Rotate camera 360 degrees over 6 seconds
axes.set_camera_orientation(0, 6, theta=axes.theta.at_time(0) + math.tau)

canvas.add_objects(axes)
if args.verbose:
    canvas.export_video('docs/source/_static/videos/three_d_camera.mp4', fps=30)
if not args.no_display:
    canvas.browser_display(start_time=0, end_time=6, fps=args.fps, port=args.port,
                           hot_reload=True)
