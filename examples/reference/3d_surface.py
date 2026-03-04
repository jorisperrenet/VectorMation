"""3D surface with camera rotation."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-1, 2))
axes.plot_surface(lambda x, y: math.exp(-(x**2 + y**2) / 2),
                  resolution=(20, 20),
                  checkerboard_colors=('#FF862F', '#4488ff'))
axes.begin_ambient_camera_rotation(start=0, rate=0.3)

v.add(axes)

v.show(end=6)
