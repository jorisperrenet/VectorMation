"""Star parameter diagram."""
import sys, os, math; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

W, H = 400, 340
v = VectorMathAnim('_ref_out', verbose=args.verbose, width=W, height=H)
v.set_background(fill='#1e1e2e')

CX, CY = 200, 160
OUTER, INNER = 110, 44
N = 5

v.add(
    Circle(r=OUTER, cx=CX, cy=CY, fill_opacity=0, stroke='#45475a', stroke_width=0.8, stroke_dasharray='4,3'),
    Circle(r=INNER, cx=CX, cy=CY, fill_opacity=0, stroke='#45475a', stroke_width=0.8, stroke_dasharray='4,3'),
)

v.add(Star(n=N, outer_radius=OUTER, inner_radius=INNER, cx=CX, cy=CY,
           fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=2.5))

v.add(Dot(r=4, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))

v.add(
    DashedLine(x1=CX, y1=CY, x2=CX, y2=CY - OUTER, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Text('outer_radius', x=CX - 90, y=CY - OUTER//2, font_size=12, fill='#cdd6f4'),
)

angle = math.radians(90 + 360 / (2 * N))
ix = CX - INNER * math.cos(angle)
iy = CY - INNER * math.sin(angle)
v.add(
    DashedLine(x1=CX, y1=CY, x2=ix, y2=iy, dash='5,3', stroke='#a6e3a1', stroke_width=1.2),
    Text('inner_radius', x=30, y=CY - 5, font_size=12, fill='#a6e3a1'),
)

v.add(Text('n = 5 (number of points)', x=110, y=315, font_size=13, fill='#f9e2af'))

if args.for_docs:
    v.write_frame(filename='docs/source/_static/images/star_params.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
