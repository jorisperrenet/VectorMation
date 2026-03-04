"""Ambient camera rotation around a 3D scene."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
sphere = Sphere3D(radius=1.5, checkerboard_colors=('#FC6255', '#c44030'))
axes.add_surface(sphere)
axes.begin_ambient_camera_rotation(start=0, rate=0.3)

v.add(axes)

v.show(end=4)
