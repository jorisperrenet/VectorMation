"""Convex hull around dots."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

d1 = Dot(cx=600, cy=300, r=8, fill='#FF6B6B')
d2 = Dot(cx=1300, cy=350, r=8, fill='#FF6B6B')
d3 = Dot(cx=1100, cy=700, r=8, fill='#FF6B6B')
d4 = Dot(cx=700, cy=750, r=8, fill='#FF6B6B')
d5 = Dot(cx=960, cy=450, r=8, fill='#FF6B6B')

hull = ConvexHull(d1, d2, d3, d4, d5,
                  stroke='#58C4DD', stroke_width=3, fill='#58C4DD', fill_opacity=0.15)
v.add(hull, d1, d2, d3, d4, d5)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_convex_hull.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
