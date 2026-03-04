"""Ellipse parameter diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

W, H = 400, 300
v = VectorMathAnim('_ref_out', verbose=args.verbose, width=W, height=H)
v.set_background(fill='#1e1e2e')

CX, CY, RX, RY = 200, 145, 120, 70

v.add(Ellipse(rx=RX, ry=RY, cx=CX, cy=CY, fill_opacity=0, stroke='#58C4DD', stroke_width=2.5))
v.add(Dot(r=4, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))
v.add(Text('(cx, cy)', x=CX + 8, y=CY + 18, font_size=11, fill='#f38ba8'))

v.add(
    DashedLine(x1=CX, y1=CY, x2=CX + RX, y2=CY, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Text('rx', x=CX + RX//2 - 6, y=CY - 8, font_size=14, fill='#cdd6f4'),
)

v.add(
    DashedLine(x1=CX, y1=CY, x2=CX, y2=CY - RY, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Text('ry', x=CX + 10, y=CY - RY//2 + 5, font_size=14, fill='#cdd6f4'),
)

v.add(
    DashedLine(x1=CX, y1=250, x2=CX, y2=265, dash='3,2', stroke='#a6adc8', stroke_width=1),
    Arrow(x1=25, y1=260, x2=CX, y2=260, tip_length=8, tip_width=6, stroke='#a6adc8', stroke_width=1),
    Text('cx', x=102, y=278, font_size=12, fill='#a6adc8'),
)

v.add(
    DashedLine(x1=35, y1=CY, x2=50, y2=CY, dash='3,2', stroke='#a6adc8', stroke_width=1),
    Arrow(x1=40, y1=20, x2=40, y2=CY, tip_length=8, tip_width=6, stroke='#a6adc8', stroke_width=1),
    Text('cy', x=20, y=85, font_size=12, fill='#a6adc8'),
)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/images/ellipse_params.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
