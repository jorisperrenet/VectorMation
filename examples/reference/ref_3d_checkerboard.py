"""Checkerboard surface colours."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
surface = Surface(lambda x, y: math.sin(x) * math.cos(y),
                  u_range=(-3, 3), v_range=(-3, 3),
                  resolution=(20, 20))
surface.set_checkerboard('#FC6255', '#c44030')
axes.add_surface(surface)

v.add(axes)

v.show(end=0)
