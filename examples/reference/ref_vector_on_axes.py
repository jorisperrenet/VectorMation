"""Axes.add_vector: draw a vector on axes."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = Axes(x_range=(-4, 4), y_range=(-3, 3))
axes.add_coordinates()
axes.add_vector(2, 1, stroke='#FFFF00', fill='#FFFF00')
axes.add_vector(-1, 2, stroke='#58C4DD', fill='#58C4DD')

v.add(axes)

v.show(end=0)
