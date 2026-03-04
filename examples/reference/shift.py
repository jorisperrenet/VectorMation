"""Shift a circle across the screen."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

circle = Circle(r=60, cx=360, cy=540, fill='#58C4DD', fill_opacity=0.8)
circle.fadein(start=0, end=0.5)
circle.shift(dx=600, start=0.5, end=2.5)
circle.shift(dy=-200, start=2.5, end=3.5)

v.add(circle)

v.show(end=4)
