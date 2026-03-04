"""Right angle indicator."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

# Draw two perpendicular lines and a right angle marker
vertex = (960, 540)
p1 = (1260, 540)
p2 = (960, 240)
l1 = Line(x1=vertex[0], y1=vertex[1], x2=p1[0], y2=p1[1], stroke='#aaa', stroke_width=3)
l2 = Line(x1=vertex[0], y1=vertex[1], x2=p2[0], y2=p2[1], stroke='#aaa', stroke_width=3)
ra = RightAngle(vertex, p1, p2, size=30, stroke='#58C4DD', stroke_width=3)
v.add(l1, l2, ra)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_right_angle.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
