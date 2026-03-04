"""WaterfallChart showing cumulative values."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = WaterfallChart(
    values=[100, 30, -20, 50, -15, -10],
    labels=['Revenue', 'Sales', 'Returns', 'Services', 'Tax', 'Costs', 'Net'],
    x=460, y=240, width=1000, height=500,
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_waterfall.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
