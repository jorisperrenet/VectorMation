"""Simple sine curve on Graph axes."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

g = Graph(math.sin, x_range=(-2 * math.pi, 2 * math.pi), y_range=(-1.5, 1.5))
g.add_coordinates()
g.add_grid()

v.add(g)

v.show(end=0)
