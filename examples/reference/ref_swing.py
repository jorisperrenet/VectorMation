"""Pendulum-like swing oscillation."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Rectangle(width=40, height=180, fill='#1ABC9C', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.swing(start=0.3, end=2, amplitude=25)
v.add(c)

v.show(end=2.5)
