"""DropShadowFilter applied to shapes."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

rect = Rectangle(300, 200, fill='#58C4DD', fill_opacity=0.9, stroke='#FFFFFF', stroke_width=2)
rect.center_to_pos(posx=700, posy=540)
rect.drop_shadow(dx=8, dy=8, blur=6)

circ = Circle(r=100, cx=1220, cy=540, fill='#FF6B6B', fill_opacity=0.9, stroke='#FFFFFF', stroke_width=2)
circ.drop_shadow(dx=8, dy=8, blur=6)

v.add(rect, circ)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/ref_drop_shadow.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=0)
