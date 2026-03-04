"""SankeyDiagram flow visualization."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

chart = SankeyDiagram(
    flows=[
        ('Budget', 'Engineering', 400),
        ('Budget', 'Marketing', 250),
        ('Budget', 'Sales', 200),
        ('Engineering', 'Product', 300),
        ('Engineering', 'Infra', 100),
        ('Marketing', 'Ads', 150),
        ('Marketing', 'Content', 100),
        ('Sales', 'Direct', 120),
        ('Sales', 'Partners', 80),
    ],
    x=160, y=140, width=1600, height=700,
    font_size=18,
)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_sankey.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
