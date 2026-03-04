"""Demonstrate ParametricCurve3D with a helix."""
from vectormation.objects import *
import math

canvas = VectorMathAnim()
canvas.set_background()

axes = ThreeDAxes(x_range=(-2, 2), y_range=(-2, 2), z_range=(-1, 2.5))

# A helix wrapping around the z-axis
def helix(t):
    return (math.cos(t), math.sin(t), t / (2 * math.pi))

curve = ParametricCurve3D(helix, t_range=(0, 4 * math.pi), num_points=200,
                          stroke='#FFFF00', stroke_width=3)
axes.add_3d(curve)

# A dot at the start
axes.add_3d(Dot3D((1, 0, 0), radius=6, fill='#FC6255'))

canvas.add_objects(axes)

canvas.show()
