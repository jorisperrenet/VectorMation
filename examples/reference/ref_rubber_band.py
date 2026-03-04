"""Circle with rubber_band effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=100, fill='#8E44AD', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.rubber_band(start=0.5, end=1.5)

v.add(c)

v.show(end=2)
