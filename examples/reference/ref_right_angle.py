"""Right angle indicator."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

# Draw two perpendicular lines and a right angle marker
vertex = (960, 540)
p1 = (1260, 540)
p2 = (960, 240)
l1 = Line(x1=vertex[0], y1=vertex[1], x2=p1[0], y2=p1[1], stroke='#aaa', stroke_width=3)
l2 = Line(x1=vertex[0], y1=vertex[1], x2=p2[0], y2=p2[1], stroke='#aaa', stroke_width=3)
ra = RightAngle(vertex, p1, p2, size=30, stroke='#58C4DD', stroke_width=3)
v.add(l1, l2, ra)

v.show(end=0)
