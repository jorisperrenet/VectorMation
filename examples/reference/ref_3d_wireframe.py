"""Surface with wireframe mesh overlay using SurfaceMesh."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))

def saddle(x, y):
    return (x**2 - y**2) / 4

surface = Surface(saddle, resolution=(20, 20),
                  fill_color='#58C4DD', fill_opacity=0.8)
mesh = SurfaceMesh(surface, stroke_color='#ffffff', stroke_opacity=0.3)
axes.add_surface(surface)
axes.add_surface(mesh)

v.add(axes)

v.show(end=0)
