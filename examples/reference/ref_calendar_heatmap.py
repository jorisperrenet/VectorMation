"""CalendarHeatmap contribution-style grid."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
import random
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

random.seed(42)
data = {(r, c): random.randint(0, 10) for r in range(7) for c in range(52)}

chart = CalendarHeatmap(
    data=data,
    rows=7, cols=52,
    x=120, y=300, cell_size=28, gap=4,
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_calendar_heatmap.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
