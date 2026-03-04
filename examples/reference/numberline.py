"""Number line with pointer and segment."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

nl = NumberLine(x_range=(-5, 5, 1), length=1200)
nl.center_to_pos()
nl.add_pointer(2, label='x')
nl.add_segment(-1, 3, color='#3498DB')

v.add(nl)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/numberline.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
