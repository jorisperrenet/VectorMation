"""Polygon shape."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

pts = [(760, 640), (860, 400), (1060, 380), (1160, 600), (960, 700)]
p = Polygon(*pts, fill='#3498DB', fill_opacity=0.5, stroke='#3498DB', stroke_width=3)
v.add(p)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_polygon.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
