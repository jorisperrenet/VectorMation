"""Opacity blink effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Star(5, outer_radius=90, inner_radius=40, fill='#F1C40F', fill_opacity=0.9)
c.fadein(start=0, end=0.3)
c.blink(start=0.3, end=2.3, count=4)
v.add(c)

v.show(end=2.5)
