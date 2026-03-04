"""Complex function transformation on NumberPlane."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

plane = NumberPlane(x_range=(-5, 5), y_range=(-5, 5))

v.add(plane)

v.show(end=0)
