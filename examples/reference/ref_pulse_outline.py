"""Pulsating outline glow."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = RegularPolygon(5, radius=100, fill='#9B59B6', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.pulse_outline(start=0.3, end=2, color='#F1C40F', max_width=10, cycles=3)
v.add(c)

v.show(end=2.5)
