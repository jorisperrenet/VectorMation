"""UnitInterval: probability axis."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

ui = UnitInterval(x=360, y=540, length=1200, tick_step=0.1)

v.add(ui)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_unit_interval.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
