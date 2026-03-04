"""Random offset glitch flickers."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Rectangle(width=200, height=120, fill='#2ECC71', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.glitch(start=0.3, end=1.5, intensity=15, n_flashes=6)
v.add(c)

v.show(end=2)
