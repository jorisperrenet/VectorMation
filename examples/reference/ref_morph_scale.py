"""Spring-like scale with overshoot."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = RegularPolygon(6, radius=70, fill='#F39C12', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.morph_scale(target_scale=1.8, start=0.3, end=2, overshoot=0.4, oscillations=3)
v.add(c)

v.show(end=2.5)
