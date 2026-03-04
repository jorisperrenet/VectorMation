"""Circle with wiggle effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=100, fill='#2ECC71', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.wiggle(start=0.5, end=1.5, amplitude=20, n_wiggles=4)

v.add(c)

v.show(end=2)
