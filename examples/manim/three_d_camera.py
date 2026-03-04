"""Demonstrate 3D camera rotation animation."""
from vectormation.objects import *
import math

canvas = VectorMathAnim()
canvas.set_background()

axes = ThreeDAxes(x_range=(-3, 3), y_range=(-3, 3), z_range=(-2, 2))

# Add a filled surface
def saddle(x, y):
    return (x**2 - y**2) / 6

axes.plot_surface(saddle, resolution=(20, 20),
                  fill_color='#58C4DD', fill_opacity=0.8)

# Rotate camera 360 degrees over 6 seconds
axes.set_camera_orientation(0, 6, theta=axes.theta.at_time(0) + math.tau)

canvas.add_objects(axes)

canvas.show(end=6)
