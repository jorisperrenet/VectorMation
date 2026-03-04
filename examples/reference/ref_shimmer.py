"""Shimmer opacity sweep effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Star(5, outer_radius=100, inner_radius=45, fill='#F1C40F', fill_opacity=0.9)
c.fadein(start=0, end=0.3)
c.shimmer(start=0.3, end=2, passes=3)
v.add(c)

v.show(end=2.5)
