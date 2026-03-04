"""Gaussian surface plot on ThreeDAxes."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-1, 2))
axes.plot_surface(lambda x, y: 1.5 * math.exp(-(x**2 + y**2) / 2),
                  resolution=(24, 24),
                  checkerboard_colors=('#FF862F', '#4488ff'))

v.add(axes)

v.show(end=0)
