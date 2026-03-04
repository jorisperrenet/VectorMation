"""next_to positioning diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

W, H = 440, 320
v = VectorMathAnim('_ref_out', verbose=args.verbose, width=W, height=H)
v.set_background(fill='#1e1e2e')

CX, CY = 220, 155
ref = Rectangle(70, 50, x=CX - 35, y=CY - 25,
                fill='#58C4DD', fill_opacity=0.2, stroke='#58C4DD', stroke_width=2)
v.add(ref)
v.add(Text('target', x=CX - 19, y=CY + 5, font_size=11, fill='#58C4DD'))

BUFF = 12
positions = [
    ('right', CX + 35 + BUFF,     CY,     '#a6e3a1'),
    ('left',  CX - 35 - BUFF - 50, CY,    '#f38ba8'),
    ('up',    CX,                  CY - 25 - BUFF - 25, '#89b4fa'),
    ('down',  CX,                  CY + 25 + BUFF,      '#f9e2af'),
]

for direction, px, py, color in positions:
    rx, ry = px - 25, py - 12
    if direction == 'left':
        rx = px
    v.add(Rectangle(50, 25, x=rx, y=ry,
                    fill=color, fill_opacity=0.2, stroke=color, stroke_width=1.5))

    label_offsets = {
        'right': (px + 30, py + 4),
        'left':  (px - 40, py + 4),
        'up':    (px + 30, py),
        'down':  (px + 30, py + 10),
    }
    lx, ly = label_offsets[direction]
    v.add(Text(f"'{direction}'", x=lx, y=ly, font_size=10, fill=color))

v.add(
    DashedLine(x1=CX + 35, y1=CY + 30, x2=CX + 35, y2=CY + 45, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    DashedLine(x1=CX + 35 + BUFF, y1=CY + 30, x2=CX + 35 + BUFF, y2=CY + 45, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    Text('buff', x=CX + 37, y=CY + 55, font_size=10, fill='#cdd6f4'),
)

v.add(Text("next_to(target, direction, buff)", x=100, y=270, font_size=13, fill='#cdd6f4'))
v.add(Text("obj.next_to(target, 'right', buff=12)", x=95, y=295, font_size=11, fill='#585b70'))

if args.for_docs:
    v.write_frame(filename='docs/source/_static/images/next_to.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
