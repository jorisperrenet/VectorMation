"""Pie chart with highlighted sector."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

pie = PieChart([35, 25, 20, 20], labels=['Python', 'JS', 'Rust', 'Go'])
pie.add_percentage_labels()
pie.explode([0], distance=20)

v.add(pie)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/piechart.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
