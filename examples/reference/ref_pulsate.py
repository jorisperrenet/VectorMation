"""Circle with pulsate effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=100, fill='#E67E22', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.pulsate(start=0.5, end=2.5, scale_factor=1.3, n_pulses=3)

v.add(c)

v.show(end=3)
