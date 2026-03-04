"""Torus3D on ThreeDAxes."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-4, 4), y_range=(-4, 4), z_range=(-2, 2))
torus = Torus3D(major_radius=2, minor_radius=0.5,
                checkerboard_colors=('#9B59B6', '#7D3C98'))
axes.add_surface(torus)

v.add(axes)

v.show(end=0)
