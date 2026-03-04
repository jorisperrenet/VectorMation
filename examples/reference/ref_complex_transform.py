"""Complex function transformation on NumberPlane."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

plane = NumberPlane(x_range=(-5, 5), y_range=(-5, 5))

v.add(plane)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_complex_transform.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
