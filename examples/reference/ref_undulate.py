"""Decaying scale wave effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=90, fill='#E74C3C', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.undulate(start=0.3, end=2, amplitude=0.2, n_waves=3)
v.add(c)

v.show(end=2.5)
