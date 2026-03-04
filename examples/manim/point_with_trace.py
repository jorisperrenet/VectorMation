"""Manim equivalent: PointWithTrace -- dot leaves a traced path as it moves."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()
point = Dot(cx=960, cy=540)
point.c.rotate_around(1, 2, (1060, 540), 180, clockwise=True)
point.c.move_to(2.5, 3.5, (1160, 440))
point.c.move_to(4, 5, (1060, 440))
trace = Trace(point.c, start=0, end=5, dt=1/60)

canvas.add_objects(trace, point)

canvas.show()
