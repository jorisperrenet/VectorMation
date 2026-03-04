"""Parametric Mobius strip surface."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))

def mobius(u, v):
    x = (1 + v / 2 * math.cos(u / 2)) * math.cos(u)
    y = (1 + v / 2 * math.cos(u / 2)) * math.sin(u)
    z = v / 2 * math.sin(u / 2)
    return (x, y, z)

surface = Surface(mobius, u_range=(0, math.tau), v_range=(-0.5, 0.5),
                  resolution=(40, 8), fill_color='#58C4DD')
axes.add_surface(surface)

v.add(axes)

v.show(end=0)
