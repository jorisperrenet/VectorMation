"""Rapid shaking jitter effect."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Rectangle(width=160, height=100, fill='#E74C3C', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.shake(start=0.5, end=1.5, amplitude=8, frequency=15)
v.add(c)

if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_shake.mp4', fps=30, end=2)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
