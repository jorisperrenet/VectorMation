"""Zooming in on a 3D scene with set_camera_zoom."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
faces = Cube(side_length=2, fill_color='#58C4DD')
for face in faces:
    axes.add_surface(face)
axes.set_camera_zoom(2.0, start=0, end=2)

v.add(axes)

v.show(end=2)
