"""Height-map surface (z = f(x, y))."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))

def paraboloid(x, y):
    return (x**2 + y**2) / 4

surface = Surface(paraboloid, u_range=(-2, 2), v_range=(-2, 2),
                  resolution=(20, 20), fill_color='#4488ff')
axes.add_surface(surface)

v.add(axes)

v.show(end=0)
