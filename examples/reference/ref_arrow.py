"""Arrow between two points."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

arrow = Arrow(x1=560, y1=540, x2=1360, y2=540, stroke='#58C4DD', fill='#58C4DD')

v.add(arrow)

v.show(end=0)
