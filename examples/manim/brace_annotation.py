"""Manim equivalent: BraceAnnotation -- brace with text label."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()
# Manim: dot at [-2,-1] and [2,1] => centered on canvas
dot1 = Dot(cx=660, cy=690, fill='#fff', fill_opacity=1)
dot2 = Dot(cx=1260, cy=390, fill='#fff', fill_opacity=1)
line = Line(x1=660, y1=690, x2=1260, y2=390, stroke='#FF862F', stroke_width=8)
b1 = Brace(line, direction='down', label='Horizontal distance')
b2 = Brace(line, direction='right', label=r'$x-x_1$')

canvas.add_objects(line, dot1, dot2, b1, b2)

canvas.show()
