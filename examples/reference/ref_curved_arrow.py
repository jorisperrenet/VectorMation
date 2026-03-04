"""CurvedArrow with a bezier curve shaft."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

carrow = CurvedArrow(x1=560, y1=540, x2=1360, y2=540, angle=0.5,
                     stroke='#2ECC71', fill='#2ECC71')

v.add(carrow)

v.show(end=0)
