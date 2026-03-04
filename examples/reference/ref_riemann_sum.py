"""Riemann sum rectangles under a curve."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

func = lambda x: x**2
g = Graph(func, x_range=(0, 3), y_range=(0, 10))
g.add_coordinates()
g.add_grid()
rects = g.get_riemann_rectangles(func, (0, 3), dx=0.3,
                                  fill='#3498DB', fill_opacity=0.4)

v.add(g, rects)

v.show(end=0)
