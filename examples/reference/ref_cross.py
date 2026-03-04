"""Cross shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Cross(cx=960, cy=540, size=200, stroke='#E74C3C', stroke_width=6)
v.add(c)

v.show(end=0)
