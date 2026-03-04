"""Gentle floating animation."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Circle(r=80, fill='#9B59B6', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.float_anim(start=0.3, end=2.5, amplitude=15, speed=1.5)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_float_anim.mp4', fps=30, end=3)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=3)
