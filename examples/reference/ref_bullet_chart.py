"""BulletChart comparing actual vs target."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = BulletChart(
    actual=270,
    target=300,
    ranges=[(150, '#2a2a3a'), (250, '#3a3a4a'), (350, '#4a4a5a')],
    label='Revenue',
    x=460, y=490, width=1000, height=100,
    font_size=24,
    max_val=350,
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_bullet_chart.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
