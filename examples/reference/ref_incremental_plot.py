"""Incremental plot: add curves one by one."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

ax = Axes(x_range=(0, 10), y_range=(0, 100))
ax.add_grid()
ax.add_coordinates()
ax.fadein(start=0, end=0.5)

curve1 = ax.plot(lambda x: x**2, stroke='#E74C3C', stroke_width=3)
curve1.create(start=0.5, end=1.5)

curve2 = ax.plot(lambda x: 10 * x, stroke='#3498DB', stroke_width=3)
curve2.create(start=1.5, end=2.5)

ax.add_legend([('x\u00b2', '#E74C3C'), ('10x', '#3498DB')])

v.add(ax)

v.show(end=3)
