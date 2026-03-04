"""Manim equivalent: RotationUpdater -- line rotating forward and backward."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()
l1 = Line(x1=760, y1=540, x2=960, y2=540)
l2 = Line(x1=760, y1=540, x2=960, y2=540, stroke=(255, 0, 0))
l2.p1.rotate_around(1, 3, l2.p2.at_time(0), degrees=130)
l2.p1.rotate_around(3, 5, l2.p2.at_time(0), degrees=130, clockwise=True)

canvas.add_objects(l1, l2)

canvas.show()
