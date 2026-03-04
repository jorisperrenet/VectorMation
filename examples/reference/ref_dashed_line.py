"""DashedLine shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

l = DashedLine(x1=560, y1=640, x2=1360, y2=440, dash='12,6', stroke='#F39C12', stroke_width=4)
v.add(l)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_dashed_line.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
