"""Angle indicator with label."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

vertex = (960, 540)
p1 = (1260, 540)
p2 = (1160, 340)
l1 = Line(x1=vertex[0], y1=vertex[1], x2=p1[0], y2=p1[1], stroke='#aaa', stroke_width=3)
l2 = Line(x1=vertex[0], y1=vertex[1], x2=p2[0], y2=p2[1], stroke='#aaa', stroke_width=3)
angle = Angle(vertex, p1, p2, radius=70, label=True,
              stroke='#58C4DD', stroke_width=3)
v.add(l1, l2, angle)

v.show(end=0)
