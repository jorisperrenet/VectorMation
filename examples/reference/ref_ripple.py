"""Ripple rings emanating from object."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Dot(cx=960, cy=540, r=20, fill='#E74C3C')
c.fadein(start=0, end=0.3)
rings = c.ripple(start=0.5, end=1.5, count=4, max_radius=150, color='#58C4DD')
v.add(c)
v.add(rings)

v.show(end=2.5)
