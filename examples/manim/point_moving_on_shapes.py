"""Manim equivalent: PointMovingOnShapes -- dot moving along and around shapes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/point_moving_on_shapes')
canvas.set_background()
cir = Circle(0, cx=960, cy=540, stroke='blue', fill_opacity=0)
cir.r.move_to(0, 1, 150)
dot = Dot(r=12, fill='#fff', fill_opacity=1)
dot.c.move_to(1, 2, (1110, 540))
dot.c.rotate_around(2, 4, (960, 540), 360)
dot.c.rotate_around(4, 5.5, (1260, 540), 360)
l = Line(960 + 3 * 150, 540, 960 + 5 * 150, 540)

canvas.add_objects(cir, dot, l)
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/point_moving_on_shapes.mp4', fps=30)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
