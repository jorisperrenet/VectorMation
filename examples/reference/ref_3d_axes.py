"""ThreeDAxes: basic 3D coordinate system."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))

v.add(axes)

v.show(end=0)
