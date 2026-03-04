"""Pendulum with trail."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

p = Pendulum(pivot_x=960, pivot_y=150, length=350, angle=45,
             period=1.5, damping=0.1, start=0, end=8)
trail = p.bob.trace_path(start=0, end=8, stroke='#FF6B6B',
                         stroke_width=1, stroke_opacity=0.5)

v.add(p, trail)
if args.for_docs:
    v.export_video('docs/source/_static/videos/pendulum.mp4', fps=30, end=8)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=8)
