"""Countdown timer display."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

cd = Countdown(start_value=10, end_value=0, font_size=120, start=0, end=3)

v.add(cd)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_countdown.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
