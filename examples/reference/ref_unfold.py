"""Unfold from zero width to full size."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Rectangle(width=240, height=140, fill='#1ABC9C', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.unfold(start=0.3, end=1.5, direction='right')
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_unfold.mp4', fps=30, end=2)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
