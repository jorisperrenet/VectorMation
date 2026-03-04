"""Integer: animated whole-number display."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

n = Integer(0, font_size=96)
n.center_to_pos()
n.animate_value(42, start=0, end=2)

v.add(n)
if args.for_docs:
    v.export_video('docs/source/_static/videos/ref_animated_integer.mp4', fps=30, end=2.5)
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2.5)
