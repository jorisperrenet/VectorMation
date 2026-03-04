"""Manim equivalent: SinAndCosFunctionPlot -- sin and cos on axes."""
from vectormation.objects import *
import math

canvas = VectorMathAnim()
canvas.set_background()
axes = Axes(x_range=(-2 * math.pi, 2 * math.pi), y_range=(-1.5, 1.5),
            x_label='x', y_label='y')
axes.add_function(math.sin, label=r'$\sin(x)$', stroke='#58C4DD')
axes.add_function(math.cos, label=r'$\cos(x)$', stroke='#FC6255')

canvas.add_objects(axes)

canvas.show()
