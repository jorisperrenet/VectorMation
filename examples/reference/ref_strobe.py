"""Rapid on/off strobe blink."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=80, fill='#E74C3C', fill_opacity=0.9)
c.fadein(start=0, end=0.3)
c.strobe(start=0.3, end=2, n_flashes=8, duty=0.4)
v.add(c)

v.show(end=2.5)
