"""Line parameter diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

W, H = 400, 260
v = VectorMathAnim('_ref_out', verbose=args.verbose, width=W, height=H)
v.set_background(fill='#1e1e2e')

X1, Y1, X2, Y2 = 60, 190, 340, 60

v.add(Line(x1=X1, y1=Y1, x2=X2, y2=Y2, stroke='#58C4DD', stroke_width=2.5))

v.add(
    Dot(r=5, cx=X1, cy=Y1, fill='#f38ba8', stroke_width=0),
    Text('p1 (x1, y1)', x=X1 - 10, y=Y1 + 22, font_size=12, fill='#f38ba8'),
)

v.add(
    Dot(r=5, cx=X2, cy=Y2, fill='#a6e3a1', stroke_width=0),
    Text('p2 (x2, y2)', x=X2 - 30, y=Y2 - 15, font_size=12, fill='#a6e3a1'),
)

mx, my = (X1 + X2) / 2, (Y1 + Y2) / 2
v.add(
    Dot(r=3, cx=mx, cy=my, fill='#f9e2af', stroke_width=0),
    Text('center()', x=mx + 8, y=my - 8, font_size=10, fill='#f9e2af'),
)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/images/line_params.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
