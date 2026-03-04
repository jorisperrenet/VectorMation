"""Shift a circle across the screen."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

circle = Circle(r=60, cx=360, cy=540, fill='#58C4DD', fill_opacity=0.8)
circle.fadein(start=0, end=0.5)
circle.shift(dx=600, start=0.5, end=2.5)
circle.shift(dy=-200, start=2.5, end=3.5)

v.add(circle)
if args.for_docs:
    v.export_video('docs/source/_static/videos/shift.mp4', fps=30, end=4)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4)
