"""Area between two curves using get_area_between."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

ax = Axes(x_range=(-3, 3), y_range=(-2, 10))
ax.add_coordinates()
ax.add_grid()
ax.plot(lambda x: x**2, stroke='#E74C3C', stroke_width=3)
ax.plot(lambda x: 2 * x + 1, stroke='#3498DB', stroke_width=3)
area = ax.get_area_between(lambda x: x**2, lambda x: 2 * x + 1,
                           x_range=(-1, 3), fill='#F39C12', fill_opacity=0.3)

v.add(ax, area)

v.show(end=0)
