"""Icosahedron on ThreeDAxes."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
faces = Icosahedron(size=1.5, fill_color='#58C4DD')
for face in faces:
    axes.add_surface(face)

v.add(axes)

v.show(end=0)
