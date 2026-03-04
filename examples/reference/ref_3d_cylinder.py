"""Cylinder3D on ThreeDAxes."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
cylinder = Cylinder3D(radius=1, height=2,
                      fill_color='#58C4DD', fill_opacity=0.8)
axes.add_surface(cylinder)

v.add(axes)

v.show(end=0)
