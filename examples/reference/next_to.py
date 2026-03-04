"""next_to positioning diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

W, H = 440, 320
v = VectorMathAnim('_ref_out', verbose=args.verbose, width=W, height=H)
v.set_background(fill='#1e1e2e')

CX, CY = 220, 145
RW, RH = 70, 50  # reference rect size
SW, SH = 50, 25  # small rect size
BUFF = 12

ref = Rectangle(RW, RH, x=CX - RW // 2, y=CY - RH // 2,
                fill='#58C4DD', fill_opacity=0.2, stroke='#58C4DD', stroke_width=2)
v.add(ref)
v.add(Text('target', x=CX - 19, y=CY + 5, font_size=11, fill='#58C4DD'))

# Each positioned rect is placed using the same buff logic as next_to
positions = [
    ('right', CX + RW // 2 + BUFF,            CY - SH // 2,              '#a6e3a1'),
    ('left',  CX - RW // 2 - BUFF - SW,       CY - SH // 2,              '#f38ba8'),
    ('up',    CX - SW // 2,                    CY - RH // 2 - BUFF - SH,  '#89b4fa'),
    ('down',  CX - SW // 2,                    CY + RH // 2 + BUFF,       '#f9e2af'),
]

for direction, rx, ry, color in positions:
    v.add(Rectangle(SW, SH, x=rx, y=ry,
                    fill=color, fill_opacity=0.2, stroke=color, stroke_width=1.5))

    # Place labels outside the diagram
    label_map = {
        'right': (rx + SW + 6, ry + SH // 2 + 4),
        'left':  (rx - 42, ry + SH // 2 + 4),
        'up':    (rx + SW + 6, ry + SH // 2 + 4),
        'down':  (rx + SW + 6, ry + SH // 2 + 4),
    }
    lx, ly = label_map[direction]
    v.add(Text(f"'{direction}'", x=lx, y=ly, font_size=10, fill=color))

# buff annotation
bx = CX + RW // 2
by = CY + RH // 2 + 8
v.add(
    DashedLine(x1=bx, y1=by, x2=bx, y2=by + 18, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    DashedLine(x1=bx + BUFF, y1=by, x2=bx + BUFF, y2=by + 18, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    Text('buff', x=bx + 1, y=by + 30, font_size=10, fill='#cdd6f4'),
)

v.add(Text("obj.next_to(target, direction, buff)", x=80, y=275, font_size=13, fill='#cdd6f4'))
v.add(Text("obj.next_to(target, 'right', buff=12)", x=80, y=298, font_size=11, fill='#585b70'))

if args.for_docs:
    v.write_frame(filename='docs/source/_static/images/next_to.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
