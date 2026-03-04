"""Annulus parameter diagram."""
from vectormation.objects import *

W, H = 400, 320
v = VectorMathAnim(width=W, height=H)
v.set_background(fill='#1e1e2e')

CX, CY = 200, 160
OUTER, INNER = 100, 50

v.add(Annulus(inner_radius=INNER, outer_radius=OUTER, cx=CX, cy=CY,
              fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=2.5))

v.add(Dot(r=4, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))
v.add(Text('(cx, cy)', x=CX + 8, y=CY + 18, font_size=11, fill='#f38ba8'))

v.add(
    DashedLine(x1=CX, y1=CY, x2=CX + OUTER, y2=CY, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Text('outer_radius', x=CX + 18, y=CY - 8, font_size=12, fill='#cdd6f4'),
)

v.add(
    DashedLine(x1=CX, y1=CY, x2=CX, y2=CY - INNER, dash='5,3', stroke='#a6e3a1', stroke_width=1.2),
    Text('inner_radius', x=CX + 10, y=CY - INNER//2 + 5, font_size=12, fill='#a6e3a1'),
)

v.add(Text('Ring/donut shape (even-odd fill)', x=95, y=295, font_size=11, fill='#585b70'))

v.show(end=2)
