"""Line3D segment in 3D space."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
axes.add_3d(Line3D((0, 0, 0), (2, 1, 1.5), stroke='#FFFF00', stroke_width=3))
axes.add_3d(Line3D((-2, -1, 0), (1, 2, -1), stroke='#FC6255', stroke_width=3))

v.add(axes)

v.show(end=0)
