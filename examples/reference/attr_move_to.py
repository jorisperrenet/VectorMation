"""Animate a circle's radius with move_to."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

circle = Circle(r=40, cx=960, cy=540, fill='#58C4DD', fill_opacity=0.8, stroke_width=3)
circle.fadein(start=0, end=0.5)

# Smoothly grow the radius from 40 to 200
circle.r.move_to(0.5, 2.5, 200)
# Then shrink it back
circle.r.move_to(2.5, 4.5, 40)

v.add(circle)
if args.for_docs:
    v.export_video('docs/source/_static/videos/attr_move_to.mp4', fps=30, end=5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
