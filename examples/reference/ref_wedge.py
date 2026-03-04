"""Wedge (Sector) shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

w = Wedge(r=160, start_angle=30, end_angle=150, cx=960, cy=540,
          fill='#E67E22', fill_opacity=0.7, stroke='#E67E22')
v.add(w)

v.show(end=0)
