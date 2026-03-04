"""Wedge/sector parameter diagram."""
import math
from vectormation.objects import *

W, H = 400, 320
v = VectorMathAnim(width=W, height=H)
v.set_background(fill='#1e1e2e')

CX, CY, R = 200, 165, 100
START, END = 30, 120

v.add(Wedge(cx=CX, cy=CY, r=R, start_angle=START, end_angle=END,
            fill='#58C4DD', fill_opacity=0.15, stroke='#58C4DD', stroke_width=2.5))

v.add(Dot(r=4, cx=CX, cy=CY, fill='#f38ba8', stroke_width=0))
v.add(Text('(cx, cy)', x=CX + 6, y=CY + 18, font_size=11, fill='#f38ba8'))

sx = CX + R * math.cos(math.radians(START))
sy = CY - R * math.sin(math.radians(START))
v.add(
    DashedLine(x1=CX, y1=CY, x2=sx, y2=sy, dash='5,3', stroke='#cdd6f4', stroke_width=1.2),
    Text('r', x=(CX + sx) / 2 + 8, y=(CY + sy) / 2 + 4, font_size=14, fill='#cdd6f4'),
)

v.add(DashedLine(x1=CX, y1=CY, x2=CX + R + 10, y2=CY, dash='3,2', stroke='#a6adc8', stroke_width=0.8))

v.add(
    Arc(cx=CX, cy=CY, r=40, start_angle=0, end_angle=START,
        stroke='#a6e3a1', stroke_width=1.5, fill_opacity=0),
    Text('start_angle', x=CX + 43, y=CY - 15, font_size=11, fill='#a6e3a1'),
)

v.add(
    Arc(cx=CX, cy=CY, r=50, start_angle=0, end_angle=END,
        stroke='#f9e2af', stroke_width=1.5, fill_opacity=0),
    Text('end_angle', x=CX - 115, y=CY - 65, font_size=11, fill='#f9e2af'),
)

v.add(Text('Wedge: arc closed through the centre', x=80, y=295, font_size=11, fill='#585b70'))

v.show(end=2)
