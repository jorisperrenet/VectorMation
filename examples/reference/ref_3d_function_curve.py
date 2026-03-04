"""3D function curve using get_graph_3d."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))
curve = axes.get_graph_3d(math.sin, plane='xz', stroke='#83C167', stroke_width=3)

v.add(axes)

v.show(end=0)
