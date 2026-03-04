"""Flickering opacity like a failing light."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Star(6, outer_radius=90, inner_radius=45, fill='#F1C40F', fill_opacity=0.9)
c.fadein(start=0, end=0.3)
c.flicker(start=0.3, end=2.5, frequency=6, min_opacity=0.15)
v.add(c)

v.show(end=3)
