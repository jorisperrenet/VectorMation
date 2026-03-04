"""Manim equivalent: ArgMinExample -- dot moving along a parabola to its minimum."""
from vectormation.objects import *
from vectormation import easings, attributes

canvas = VectorMathAnim()
canvas.set_background()
ax = Axes(x_range=(0, 10), y_range=(0, 55), tex_ticks=True)

func = lambda x: 2 * (x - 5) ** 2
curve = ax.plot(func, stroke='#C55F73')

# Dot that travels along the curve to the minimum using graph_position
dot = Dot(fill='#FFFF00')
x_val = attributes.Real(0, 0)
x_val.move_to(0, 3, 5, easing=easings.smooth)
dot.c.set_onward(0, ax.graph_position(func, x_val))

canvas.add_objects(ax, dot)

canvas.show(end=3)
