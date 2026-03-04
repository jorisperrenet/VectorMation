"""Animate a circle's radius with move_to."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

circle = Circle(r=40, cx=960, cy=540, fill='#58C4DD', fill_opacity=0.8, stroke_width=3)
circle.fadein(start=0, end=0.5)

# Smoothly grow the radius from 40 to 200
circle.r.move_to(0.5, 2.5, 200)
# Then shrink it back
circle.r.move_to(2.5, 4.5, 40)

v.add(circle)

v.show(end=5)
