"""Sinusoidal wave distortion."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Rectangle(width=220, height=100, fill='#3498DB', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.apply_wave(start=0.3, end=2, amplitude=35)
v.add(c)

v.show(end=2.5)
