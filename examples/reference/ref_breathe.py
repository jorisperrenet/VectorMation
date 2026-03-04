"""Gentle breathing scale oscillation."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=90, fill='#1ABC9C', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.breathe(start=0.2, end=3, amplitude=0.1, speed=0.8)
v.add(c)

v.show(end=3.5)
