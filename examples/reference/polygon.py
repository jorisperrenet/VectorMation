"""Regular polygon gallery: triangle, pentagon, hexagon."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

v = VectorMathAnim('_ref_out', verbose=args.verbose)
v.set_background()

tri = RegularPolygon(3, radius=80, cx=380, cy=540, fill='#E74C3C', fill_opacity=0.7)
pent = RegularPolygon(5, radius=80, cx=960, cy=540, fill='#58C4DD', fill_opacity=0.7)
hexa = RegularPolygon(6, radius=80, cx=1540, cy=540, fill='#83C167', fill_opacity=0.7)

l1 = Text('Triangle', x=380, y=680, font_size=24, fill='#aaa', text_anchor='middle')
l2 = Text('Pentagon', x=960, y=680, font_size=24, fill='#aaa', text_anchor='middle')
l3 = Text('Hexagon', x=1540, y=680, font_size=24, fill='#aaa', text_anchor='middle')

v.add(tri, pent, hexa, l1, l2, l3)
if args.for_docs:
    v.write_frame(filename='docs/source/_static/videos/polygon.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
