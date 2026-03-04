"""Cross shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

c = Cross(cx=960, cy=540, size=200, stroke='#E74C3C', stroke_width=6)
v.add(c)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_cross.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
