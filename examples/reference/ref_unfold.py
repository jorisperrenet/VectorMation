"""Unfold from zero width to full size."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Rectangle(width=240, height=140, fill='#1ABC9C', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.unfold(start=0.3, end=1.5, direction='right')
v.add(c)

v.show(end=2)
