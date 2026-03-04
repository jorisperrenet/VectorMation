"""RegularPolygon shapes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

colors = ['#E74C3C', '#F39C12', '#2ECC71', '#3498DB', '#9B59B6']
for i, (n, color) in enumerate(zip([3, 5, 6, 7, 8], colors)):
    cx = 300 + i * 330
    p = RegularPolygon(n, radius=100, cx=cx, cy=540, fill=color, fill_opacity=0.5, stroke=color)
    v.add(p)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_regular_polygon.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
