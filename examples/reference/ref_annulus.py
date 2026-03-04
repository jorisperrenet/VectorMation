"""Annulus shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

a = Annulus(inner_radius=80, outer_radius=160, cx=960, cy=540,
            fill='#E74C3C', fill_opacity=0.6, stroke='#E74C3C')
v.add(a)

v.show(end=0)
