"""Circle with indicate effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=100, fill='#58C4DD', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.indicate(start=0.5, end=1.5, scale_factor=1.3)

v.add(c)

v.show(end=2)
