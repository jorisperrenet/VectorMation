"""Manim equivalent: MovingAngle -- angle arc between two lines, animated via updater."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()
cx, cy = 960, 540
l1 = Line(x1=cx, y1=cy, x2=cx + 200, y2=cy, stroke='#fff')
l2 = Line(x1=cx, y1=cy, x2=cx + 200, y2=cy, stroke='#FFFF00')
l2.p2.rotate_around(0, 2, (cx, cy), degrees=-110)
l2.p2.rotate_around(2, 3.5, (cx, cy), degrees=70)
l2.p2.rotate_around(3.5, 5, (cx, cy), degrees=-140)

angle = Angle(vertex=l1.p1, p1=l1.p2, p2=l2.p2, radius=40,
              label=r'$\theta$', label_font_size=36)

canvas.add_objects(l1, l2, angle)

canvas.show()
