"""Different light directions on a 3D surface."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
axes.set_light_direction(0, 0, 1)  # Light from directly above
sphere = Sphere3D(radius=1.5, fill_color='#58C4DD')
axes.add_surface(sphere)

v.add(axes)

v.show(end=0)
