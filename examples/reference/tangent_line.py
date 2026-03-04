"""Animated tangent line sliding along a curve."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

func = lambda x: x ** 3 - 3 * x
g = Graph(func, x_range=(-3, 3), y_range=(-5, 5))
g.add_coordinates()
g.add_grid()
g.fadein(start=0, end=1)

tangent = g.animated_tangent_line(func, -2.5, 2.5, start=1, end=4,
                                  length=350, stroke='#E74C3C', stroke_width=4)
tangent.fadein(start=1, end=1.3)

v.add(g, tangent)

v.show(end=5)
