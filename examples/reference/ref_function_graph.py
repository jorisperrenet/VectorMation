"""FunctionGraph shape."""
import math
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

g = Graph(math.sin, x_range=(-2*math.pi, 2*math.pi), y_range=(-1.5, 1.5))
v.add(g)

v.show(end=0)
