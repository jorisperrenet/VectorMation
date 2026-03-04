"""Tutorial spiral example with rendered output."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

point = Dot(cx=960, cy=540)
trace = Trace(point.c, stroke_width=4)
point.c.set(start=0, end=5, func_inner=lambda t: (t * 80 + 960, 540))
point.c.rotate_around(0, 5, pivot_point=(960, 540), degrees=360 * 4)

v.add(trace, point)
if args.for_docs:
    v.export_video('docs/source/_static/videos/tutorial_spiral.mp4', fps=30, end=5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=5)
