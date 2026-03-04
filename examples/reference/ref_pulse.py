"""Circle with pulse effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=100, fill='#9B59B6', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.pulse(start=0.5, end=1.5, scale_factor=1.5)

v.add(c)

v.show(end=2)
