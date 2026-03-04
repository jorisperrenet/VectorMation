"""IconGrid infographic display."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

grid = IconGrid(
    data=[(30, '#58C4DD'), (20, '#E74C3C'), (15, '#2ECC71'), (35, '#F39C12')],
    x=710, y=400, cols=10, size=18, gap=5,
)

v.add(grid)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_icon_grid.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
