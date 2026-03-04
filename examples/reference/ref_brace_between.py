"""Brace between two points."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

d1 = Dot(cx=500, cy=540, r=8, fill='#FF6B6B')
d2 = Dot(cx=1420, cy=540, r=8, fill='#FF6B6B')
line = DashedLine(x1=500, y1=540, x2=1420, y2=540, stroke='#aaa', stroke_width=2)
brace = brace_between_points((500, 540), (1420, 540),
                              direction='down', label='width')
v.add(line, d1, d2, brace)

v.show(end=0)
