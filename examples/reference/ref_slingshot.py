"""Pullback then launch with overshoot."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Dot(cx=300, cy=540, r=20, fill='#E74C3C')
c.fadein(start=0, end=0.3)
c.slingshot(tx=1600, ty=540, start=0.5, end=2, pullback=0.4, overshoot=0.2)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_slingshot.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
