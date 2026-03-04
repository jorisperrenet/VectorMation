"""Arrow between two points."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

arrow = Arrow(x1=560, y1=540, x2=1360, y2=540, stroke='#58C4DD', fill='#58C4DD')

v.add(arrow)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_arrow.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
