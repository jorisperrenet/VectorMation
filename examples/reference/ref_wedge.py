"""Wedge (Sector) shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

w = Wedge(r=160, start_angle=30, end_angle=150, cx=960, cy=540,
          fill='#E67E22', fill_opacity=0.7, stroke='#E67E22')
v.add(w)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_wedge.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
