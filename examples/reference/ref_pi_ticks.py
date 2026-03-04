"""Pi-formatted tick labels on a sine graph."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

ax = Axes(x_range=(-2 * math.pi, 2 * math.pi), y_range=(-1.5, 1.5),
          x_tick_type='pi')
ax.plot(math.sin, stroke='#58C4DD', stroke_width=3)
ax.add_coordinates()
ax.add_grid()

v.add(ax)

v.show(end=0)
