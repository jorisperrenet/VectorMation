"""Curved arrow parameter diagram."""
from vectormation.objects import *

W, H = 440, 260
v = VectorMathAnim(width=W, height=H)
v.set_background(fill='#1e1e2e')

X1, Y1, X2, Y2 = 70, 170, 350, 170

v.add(DashedLine(x1=X1, y1=Y1, x2=X2, y2=Y2, dash='4,4', stroke='#45475a', stroke_width=1))

v.add(CurvedArrow(x1=X1, y1=Y1, x2=X2, y2=Y2, angle=0.6,
                  tip_length=14, tip_width=10,
                  stroke='#58C4DD', stroke_width=2.5))

v.add(
    Dot(r=5, cx=X1, cy=Y1, fill='#f38ba8', stroke_width=0),
    Text('(x1, y1)', x=X1 - 15, y=Y1 + 22, font_size=11, fill='#f38ba8'),
)

v.add(
    Dot(r=5, cx=X2, cy=Y2, fill='#f38ba8', stroke_width=0),
    Text('(x2, y2)', x=X2 - 15, y=Y2 + 22, font_size=11, fill='#f38ba8'),
)

mid_x = (X1 + X2) // 2
v.add(
    Arrow(x1=mid_x, y1=Y1, x2=mid_x, y2=Y1 - 70, tip_length=6, tip_width=5,
          stroke='#a6e3a1', stroke_width=1.2),
    Text('angle', x=mid_x + 8, y=Y1 - 45, font_size=12, fill='#a6e3a1'),
    Text('(curvature)', x=mid_x + 8, y=Y1 - 30, font_size=10, fill='#585b70'),
)

v.show(end=2)
