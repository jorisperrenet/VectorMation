"""Adding a sphere surface via add_surface."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
sphere = Sphere3D(radius=1.5, checkerboard_colors=('#4488ff', '#2266cc'))
axes.add_surface(sphere)

v.add(axes)

v.show(end=0)
