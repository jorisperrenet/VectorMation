"""Line graph from data points."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

ax = Axes(x_range=(0, 10), y_range=(0, 100))
ax.add_coordinates()
ax.add_grid()
ax.plot_line_graph([1, 3, 5, 7, 9], [20, 45, 30, 80, 60], stroke='#E74C3C', stroke_width=3)

v.add(ax)

v.show(end=0)
