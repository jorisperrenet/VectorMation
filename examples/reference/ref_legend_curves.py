"""Legend with multiple curves."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

ax = Axes(x_range=(-5, 5), y_range=(-2, 2))
ax.add_coordinates()
ax.add_grid()
ax.plot(math.sin, stroke='#E74C3C', stroke_width=3)
ax.plot(math.cos, stroke='#3498DB', stroke_width=3)
ax.add_legend([('sin(x)', '#E74C3C'), ('cos(x)', '#3498DB')])

v.add(ax)

v.show(end=0)
