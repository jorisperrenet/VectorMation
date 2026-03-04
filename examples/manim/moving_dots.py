"""Manim equivalent: MovingDots -- two dots linked by a line, each moving independently."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()
d1, d2 = Dot(r=12, fill='#58C4DD', fill_opacity=1), Dot(r=12, fill='#83C167', fill_opacity=1)
l = Line(x1=960, y1=540, x2=860, y2=540, stroke='#FC6255')
d1.c.set_to(l.p1)
d2.c.set_to(l.p2)
l.p1.move_to(1.5, 3, (960, 240))
l.p2.move_to(1, 2.5, (1260, 540))

canvas.add_objects(l, d1, d2)

canvas.show()
