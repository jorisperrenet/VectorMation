"""RadarChart with sample data."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = RadarChart(
    values=[85, 70, 90, 60, 75, 80],
    labels=['Speed', 'Power', 'Accuracy', 'Defense', 'Stamina', 'Agility'],
    max_val=100,
    colors=['#58C4DD'],
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_radar_chart.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
