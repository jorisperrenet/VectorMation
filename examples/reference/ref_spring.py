"""Circle with spring effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=100, fill='#E74C3C', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.spring(start=0.5, end=2.5, amplitude=50, damping=5, frequency=4)

v.add(c)

v.show(end=3)
