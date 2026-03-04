"""Pullback then launch with overshoot."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Dot(cx=300, cy=540, r=20, fill='#E74C3C')
c.fadein(start=0, end=0.3)
c.slingshot(tx=1600, ty=540, start=0.5, end=2, pullback=0.4, overshoot=0.2)
v.add(c)

v.show(end=2.5)
