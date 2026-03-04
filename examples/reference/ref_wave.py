"""Wave distortion effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Rectangle(width=200, height=120, fill='#58C4DD', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.wave(start=0.5, end=1.5, amplitude=25, n_waves=3)
v.add(c)

v.show(end=2)
