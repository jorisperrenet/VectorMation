"""NumberLine parameter diagram."""
from vectormation.objects import *

W, H = 500, 200
v = VectorMathAnim(width=W, height=H)
v.set_background(fill='#1e1e2e')

v.add(NumberLine(
    x_range=(-4, 3, 1), length=380, x=60, y=90,
    include_arrows=True, include_numbers=True,
    tick_size=10, font_size=12,
    stroke='#58C4DD', stroke_width=2, fill='#cdd6f4',
))

left_x, right_x = 60, 440
v.add(
    DashedLine(x1=left_x + 20, y1=118, x2=left_x + 20, y2=140, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    DashedLine(x1=right_x - 20, y1=118, x2=right_x - 20, y2=140, dash='3,2', stroke='#cdd6f4', stroke_width=0.8),
    Arrow(x1=left_x + 25, y1=138, x2=right_x - 20, y2=138, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Arrow(x1=right_x - 25, y1=138, x2=left_x + 20, y2=138, tip_length=5, tip_width=4, stroke='#cdd6f4', stroke_width=1.2),
    Text('x_range = (-4, 3, 1)', x=170, y=160, font_size=12, fill='#cdd6f4'),
)

tick_x = 330
v.add(
    Arrow(x1=tick_x, y1=68, x2=tick_x, y2=80, tip_length=4, tip_width=3, stroke='#a6e3a1', stroke_width=1.2),
    Text('tick_size', x=tick_x + 8, y=72, font_size=11, fill='#a6e3a1'),
)

v.add(Text('length controls total pixel width', x=130, y=185, font_size=11, fill='#585b70'))

v.show(end=2)
