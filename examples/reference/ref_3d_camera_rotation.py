"""Animated camera rotation with set_camera_orientation."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
axes.plot_surface(lambda x, y: math.sin(x) * math.cos(y),
                  resolution=(20, 20), fill_color='#58C4DD')
axes.set_camera_orientation(0, 3, phi=math.radians(30), theta=math.radians(-120))

v.add(axes)

v.show(end=3)
