"""Manim equivalent: PointWithTrace -- dot leaves a traced path as it moves."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/point_with_trace')
canvas.set_background()
point = Dot(cx=960, cy=540)
point.c.rotate_around(1, 2, (1060, 540), 180, clockwise=True)
point.c.move_to(2.5, 3.5, (1160, 440))
point.c.move_to(4, 5, (1060, 440))
trace = Trace(point.c, start=0, end=5, dt=1/60)

canvas.add_objects(trace, point)
if args.for_docs:
    canvas.export_video('docs/source/_static/videos/point_with_trace.mp4', fps=30)
if not args.for_docs:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
