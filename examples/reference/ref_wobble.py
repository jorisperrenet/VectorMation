"""Organic wobbling motion."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Rectangle(width=150, height=100, fill='#3498DB', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.wobble(start=0.3, end=2, amplitude=8, frequency=4)
v.add(c)

v.show(end=2.5)
