"""Brace parameter diagram."""
import sys, os; sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
from vectormation.objects import *
args = parse_args()

W, H = 440, 280
v = VectorMathAnim('_ref_out', verbose=args.verbose, width=W, height=H)
v.set_background(fill='#1e1e2e')

target = Rectangle(240, 60, x=220, y=105, rx=4, ry=4,
                   fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=2)
v.add(target)
v.add(Text('target object', x=148, y=112, font_size=13, fill='#58C4DD'))

brace = Brace(target, direction='down', label='label', buff=10,
              stroke='#cdd6f4', stroke_width=2, fill='#f9e2af')
v.add(brace)

rect_bottom = 105 + 30
v.add(
    DashedLine(x1=350, y1=rect_bottom, x2=375, y2=rect_bottom, dash='3,2', stroke='#a6e3a1', stroke_width=0.8),
    DashedLine(x1=350, y1=rect_bottom + 10, x2=375, y2=rect_bottom + 10, dash='3,2', stroke='#a6e3a1', stroke_width=0.8),
    Arrow(x1=370, y1=rect_bottom + 1, x2=370, y2=rect_bottom + 10, tip_length=3, tip_width=3, stroke='#a6e3a1', stroke_width=1.2),
    Text('buff', x=380, y=rect_bottom + 8, font_size=11, fill='#a6e3a1'),
)

v.add(
    Arrow(x1=50, y1=rect_bottom, x2=50, y2=rect_bottom + 45, tip_length=8, tip_width=6,
          stroke='#cdd6f4', stroke_width=1.2),
    Text('direction', x=25, y=rect_bottom - 10, font_size=11, fill='#cdd6f4'),
    Text("'down'", x=32, y=rect_bottom + 58, font_size=10, fill='#585b70'),
)

if args.for_docs:
    v.write_frame(filename='docs/source/_static/images/brace_params.svg')
if not args.for_docs:
    v.browser_display(fps=args.fps, port=args.port, hot_reload=True, end=2)
