"""Dot3D in 3D space."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
axes.add_3d(Dot3D((1, 0, 0), radius=8, fill='#FC6255'))
axes.add_3d(Dot3D((0, 2, 0), radius=8, fill='#83C167'))
axes.add_3d(Dot3D((0, 0, 1.5), radius=8, fill='#58C4DD'))
axes.add_3d(Dot3D((-1, -1, 1), radius=6, fill='#FFFF00'))

v.add(axes)

v.show(end=0)
