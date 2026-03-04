"""DoubleArrow with heads on both ends."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

darrow = DoubleArrow(x1=560, y1=540, x2=1360, y2=540, stroke='#E74C3C', fill='#E74C3C')

v.add(darrow)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_double_arrow.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
