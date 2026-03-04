"""Rapid shaking jitter effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Rectangle(width=160, height=100, fill='#E74C3C', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.shake(start=0.5, end=1.5, amplitude=8, frequency=15)
v.add(c)

v.show(end=2)
