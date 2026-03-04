"""DonutChart with sample data."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = DonutChart(
    values=[35, 25, 20, 15, 5],
    labels=['Python', 'JS', 'Rust', 'Go', 'Other'],
    colors=['#58C4DD', '#E74C3C', '#2ECC71', '#F39C12', '#9B59B6'],
    center_text='Languages',
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_donut_chart.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
