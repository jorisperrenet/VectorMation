"""WaffleChart showing category proportions."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = WaffleChart(
    categories=[
        ('Python', 45, '#3776AB'),
        ('JavaScript', 30, '#F7DF1E'),
        ('Rust', 15, '#DEA584'),
        ('Other', 10, '#888888'),
    ],
    x=560, y=290, grid_size=10, cell_size=40, gap=5,
    font_size=18,
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_waffle.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
