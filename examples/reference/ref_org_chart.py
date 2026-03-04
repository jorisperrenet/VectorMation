"""OrgChart tree structure."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

tree = ('CEO', [
    ('CTO', [
        ('Dev Lead', []),
        ('QA Lead', []),
    ]),
    ('CFO', [
        ('Accounting', []),
    ]),
    ('COO', [
        ('Operations', []),
        ('HR', []),
    ]),
])

chart = OrgChart(tree, y=100, h_spacing=200, v_spacing=120)

v.add(chart)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_org_chart.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
