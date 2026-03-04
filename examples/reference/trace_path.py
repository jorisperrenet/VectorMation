"""Dot moving with a visible trail."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

dot = Dot(cx=300, cy=540, r=10, fill='#FF6B6B')
dot.fadein(start=0, end=0.3)
dot.shift(dx=400, start=0.3, end=1.5)
dot.shift(dy=-200, start=1.5, end=2.5)
dot.shift(dx=500, start=2.5, end=4)

trail = dot.trace_path(start=0.3, end=4, stroke='#FF6B6B', stroke_width=2)

v.add(trail, dot)
if args.for_docs:
    v.export_video('docs/source/_static/videos/trace_path.mp4', fps=30, end=4.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=4.5)
