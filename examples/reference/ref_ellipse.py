"""Ellipse shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

e = Ellipse(rx=200, ry=100, fill='#58C4DD', fill_opacity=0.6, stroke='#58C4DD')
v.add(e)

v.show(end=0)
