"""Graph with area shading."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

g = Graph(math.sin, x_range=(0, 2 * math.pi), y_range=(-1.5, 1.5))
g.add_coordinates()
g.add_grid()
area = g.get_area(math.sin, x_range=(0, math.pi),
                  fill='#3498DB', fill_opacity=0.3)

v.add(g, area)

v.show(end=2)
