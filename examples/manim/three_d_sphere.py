"""Manim equivalent: ThreeDLightSourcePosition -- sphere on 3D axes."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))

sphere = Sphere3D(radius=1.5, fill_color='#FC6255',
                  checkerboard_colors=('#FC6255', '#c44030'),
                  resolution=(16, 32), fill_opacity=0.9)
axes.add_surface(sphere)

canvas.add_objects(axes)

canvas.show()
