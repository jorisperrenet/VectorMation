"""Manim equivalent: FollowingGraphCamera -- camera follows a dot along a graph."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
import math
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/following_graph_camera')
canvas.set_background()

ax = Axes(x_range=(-1, 10), y_range=(-1, 10))
func = lambda x: math.sin(x)
ax.plot(func, stroke='#58C4DD')

# Dot moves along the sine curve from x=0 to x=3*pi over [0.5, 2.0]
dot = Dot(cx=ax.coords_to_point(0, 0)[0], cy=ax.coords_to_point(0, 0)[1], fill='#FF8C00')
x_coor = lambda t: min(max((t - 0.5) / 1.5, 0), 1) * 3 * math.pi
dot.c.set_onward(0, lambda t: ax.coords_to_point(x_coor(t), func(x_coor(t)), t))

# Camera: zoom in, follow the dot, then zoom out
canvas.camera_zoom(2, start=0, end=0.5, cx=dot.c.at_time(0)[0], cy=dot.c.at_time(0)[1])
canvas.camera_follow(dot, start=0.5, end=2.0)
canvas.camera_reset(start=2.0, end=2.5)

canvas.add_objects(ax, dot)
if args.verbose:
    canvas.export_video('docs/source/_static/videos/following_graph_camera.mp4', fps=30)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
