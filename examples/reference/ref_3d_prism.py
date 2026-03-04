"""Prism3D (hexagonal) on ThreeDAxes."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
faces = Prism3D(n_sides=6, radius=1.2, height=2, fill_color='#9B59B6')
for face in faces:
    axes.add_surface(face)

v.add(axes)

v.show(end=0)
