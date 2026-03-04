"""Gentle floating animation."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=80, fill='#9B59B6', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.float_anim(start=0.3, end=2.5, amplitude=15, speed=1.5)
v.add(c)

v.show(end=3)
