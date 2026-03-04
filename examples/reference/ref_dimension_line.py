"""DimensionLine between two points."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

rect = Rectangle(400, 200, x=760, y=440, fill='#333', stroke='#58C4DD')
dim = DimensionLine(p1=(760, 440), p2=(1160, 440), label='400 px', offset=40)

v.add(rect, dim)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_dimension_line.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
