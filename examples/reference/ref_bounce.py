"""Circle with bounce effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=80, fill='#F39C12', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.bounce(start=0.5, end=2.5, height=80, n_bounces=3)

v.add(c)

v.show(end=3)
