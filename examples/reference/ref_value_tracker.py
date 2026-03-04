"""DecimalNumber tracking a ValueTracker."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

vt = ValueTracker(0)
vt.animate_value(3.14159, start=0, end=2)

label = DecimalNumber(vt, fmt='{:.4f}', font_size=72)
label.center_to_pos()

v.add(label)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_value_tracker.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
