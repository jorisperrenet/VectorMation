"""Manim equivalent: RotationUpdater -- line rotating forward and backward."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

canvas = VectorMathAnim(verbose=args.verbose, save_dir='svgs/manim/rotation_updater')
canvas.set_background()
l1 = Line(x1=760, y1=540, x2=960, y2=540)
l2 = Line(x1=760, y1=540, x2=960, y2=540, stroke=(255, 0, 0))
l2.p1.rotate_around(1, 3, l2.p2.at_time(0), degrees=130)
l2.p1.rotate_around(3, 5, l2.p2.at_time(0), degrees=130, clockwise=True)

canvas.add_objects(l1, l2)
if args.verbose:
    canvas.export_video('docs/source/_static/videos/rotation_updater.mp4', fps=30)
if not args.no_display:
    canvas.browser_display(fps=args.fps, port=args.port, hot_reload=True)
