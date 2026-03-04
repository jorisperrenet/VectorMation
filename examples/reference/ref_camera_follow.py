"""Camera follow example."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background(fill='#1a1a2e')

dot = Dot(cx=200, cy=540, r=14, fill='#58C4DD')
dot.fadein(start=0, end=0.3)
dot.shift(dx=1600, start=0.5, end=4.5)

line = Line(200, 540, 200, 540, stroke='#58C4DD', stroke_width=3)
line.p2.set_onward(0, dot.c.at_time)
v.camera_zoom(3, start=0, end=0.5)
v.camera_follow(dot, start=0.5, end=4.5)

v.add(line, dot)

v.show(end=5)
