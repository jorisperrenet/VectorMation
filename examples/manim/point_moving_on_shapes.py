"""Manim equivalent: PointMovingOnShapes -- dot moving along and around shapes."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()
cir = Circle(0, cx=960, cy=540, stroke='blue', fill_opacity=0)
cir.r.move_to(0, 1, 150)
dot = Dot(r=12, fill='#fff', fill_opacity=1)
dot.c.move_to(1, 2, (1110, 540))
dot.c.rotate_around(2, 4, (960, 540), 360)
dot.c.rotate_around(4, 5.5, (1260, 540), 360)
l = Line(960 + 3 * 150, 540, 960 + 5 * 150, 540)

canvas.add_objects(cir, dot, l)

canvas.show()
