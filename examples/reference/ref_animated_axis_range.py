"""Animated axis range zoom."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

g = Graph(math.sin, x_range=(-5, 5), y_range=(-2, 2))
g.add_coordinates()
g.add_grid()
g.fadein(start=0, end=0.5)
g.animate_range(start=1, end=3, x_range=(-1, 1), y_range=(-1.5, 1.5))

v.add(g)

v.show(end=4)
