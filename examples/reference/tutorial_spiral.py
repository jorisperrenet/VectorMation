"""Tutorial spiral example with rendered output."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

point = Dot(cx=960, cy=540)
trace = Trace(point.c, stroke_width=4)
point.c.set(start=0, end=5, func_inner=lambda t: (t * 80 + 960, 540))
point.c.rotate_around(0, 5, pivot_point=(960, 540), degrees=360 * 4)

v.add(trace, point)

v.show(end=5)
