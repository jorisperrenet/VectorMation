"""Star with spiral_in effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Star(5, outer_radius=100, inner_radius=45, fill='#1ABC9C', fill_opacity=0.8)
c.spiral_in(start=0, end=2, n_turns=2)

v.add(c)

v.show(end=2.5)
