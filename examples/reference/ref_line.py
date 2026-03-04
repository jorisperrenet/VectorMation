"""Line shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

l = Line(x1=560, y1=640, x2=1360, y2=440, stroke='#2ECC71', stroke_width=5)
v.add(l)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_line.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
