"""Slide to target while spinning."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = RegularPolygon(4, radius=60, cx=300, cy=540, fill='#9B59B6', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.skate(tx=1600, ty=540, start=0.5, end=2, degrees=720)
v.add(c)

v.show(end=2.5)
