"""KPICard metric display."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

card = KPICard(
    'Revenue', '$1.2M',
    subtitle='+12% MoM',
    trend_data=[10, 12, 11, 14, 13, 16, 15, 19, 18, 22],
    x=640, y=340, width=640, height=400,
    font_size=96,
)

v.add(card)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_kpi_card.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
