"""Arc shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

a = Arc(r=140, start_angle=0, end_angle=270, cx=960, cy=540,
        stroke='#1ABC9C', stroke_width=6, fill_opacity=0)
v.add(a)

v.show(end=0)
