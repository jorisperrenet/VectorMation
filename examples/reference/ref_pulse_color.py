"""Periodic color pulsing."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=90, fill='#2ECC71', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.pulse_color(color='#E74C3C', start=0.3, end=2.5, n_pulses=4)
v.add(c)

v.show(end=3)
