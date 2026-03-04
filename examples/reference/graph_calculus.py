"""Function with its derivative and antiderivative."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

func = lambda x: math.sin(x)
ax = Axes(x_range=(0, 2 * math.pi), y_range=(-2.5, 2.5))
ax.add_coordinates()
ax.add_grid()

ax.plot(func, stroke='#FFFFFF', stroke_width=3)
ax.plot_derivative(func, stroke='#E74C3C', stroke_width=2, stroke_dasharray='8 4')
ax.plot_antiderivative(func, stroke='#2ECC71', stroke_width=2, stroke_dasharray='8 4')
ax.add_legend([("sin(x)", '#FFFFFF'), ("cos(x)  [derivative]", '#E74C3C'),
               ("-cos(x) [integral]", '#2ECC71')])

v.add(ax)

v.show(end=1)
