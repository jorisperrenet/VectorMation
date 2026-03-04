"""Arc shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

a = Arc(r=140, start_angle=0, end_angle=270, cx=960, cy=540,
        stroke='#1ABC9C', stroke_width=6, fill_opacity=0)
v.add(a)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_arc_shape.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
