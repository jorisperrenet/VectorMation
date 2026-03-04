"""Quadratic with annotations: vertex label and grid."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

func = lambda x: x**2 - 3
g = Graph(func, x_range=(-4, 4), y_range=(-4, 14))
g.add_coordinates()
g.add_grid()
g.add_dot_label(0, -3, label='min (0, -3)', dot_color='#E74C3C')
g.get_vertical_line(0, y_val=-3, stroke='#E74C3C', stroke_dasharray='6 4', stroke_width=2)

v.add(g)

v.show(end=0)
