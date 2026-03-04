"""FunnelChart showing conversion stages."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = FunnelChart(
    stages=[
        ('Visitors', 10000),
        ('Signups', 5000),
        ('Active', 2500),
        ('Paid', 1200),
        ('Enterprise', 400),
    ],
    x=460, y=140, width=1000, height=800,
    font_size=20,
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_funnel.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
