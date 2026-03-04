"""2D vector field on axes."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

ax = Axes(x_range=(-4, 4), y_range=(-4, 4))
ax.add_coordinates()
ax.plot_vector_field(lambda x, y: (-y, x), x_step=1, y_step=1, stroke='#58C4DD')

v.add(ax)

v.show(end=1)
