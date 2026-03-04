"""Ghostly fading copies along path."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Dot(cx=200, cy=540, r=18, fill='#E74C3C')
c.fadein(start=0, end=0.2)
c.shift(dx=1500, start=0.3, end=2.5)
c.fadein(start=0, end=0.3)
ghosts = c.stamp_trail(start=0.3, end=2.5, count=6, fade_duration=0.6, opacity=0.5)
v.add(c)
v.add(*ghosts)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_stamp_trail.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
