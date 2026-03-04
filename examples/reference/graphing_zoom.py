"""Axes zoom with animated ranges."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

ax = Axes(x_range=(-5, 5), y_range=(-2, 26))
curve = ax.plot(lambda x: x ** 2, stroke='#58C4DD')

# Zoom into x=[1, 4], y=[0, 18]
ax.set_ranges((1, 4), (0, 18), start=0, end=2)

v.add(ax)

v.show(end=3)
