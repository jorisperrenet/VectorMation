"""DoubleArrow with heads on both ends."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

darrow = DoubleArrow(x1=560, y1=540, x2=1360, y2=540, stroke='#E74C3C', fill='#E74C3C')

v.add(darrow)

v.show(end=0)
