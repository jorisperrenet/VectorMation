"""Star shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

s = Star(5, outer_radius=140, inner_radius=60, cx=960, cy=540,
         fill='#F1C40F', fill_opacity=0.7, stroke='#F1C40F')
v.add(s)

v.show(end=0)
