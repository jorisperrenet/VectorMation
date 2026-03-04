"""Polygon shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

pts = [(760, 640), (860, 400), (1060, 380), (1160, 600), (960, 700)]
p = Polygon(*pts, fill='#3498DB', fill_opacity=0.5, stroke='#3498DB', stroke_width=3)
v.add(p)

v.show(end=0)
