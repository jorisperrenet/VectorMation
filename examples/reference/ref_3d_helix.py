"""ParametricCurve3D helix."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))

def helix(t):
    return (math.cos(t), math.sin(t), t / (2 * math.pi))

curve = ParametricCurve3D(helix, t_range=(0, 4 * math.pi),
                          num_points=200, stroke='#FFFF00', stroke_width=3)
axes.add_3d(curve)

v.add(axes)

v.show(end=0)
