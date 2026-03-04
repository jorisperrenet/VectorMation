"""Histogram from data."""
from vectormation.objects import *
import random

v = VectorMathAnim()
v.set_background()

random.seed(42)
data = [random.gauss(5, 1.5) for _ in range(200)]

ax = Axes(x_range=(0, 10), y_range=(0, 50))
ax.add_coordinates()
ax.plot_histogram(data, bins=15, fill='#3498DB', fill_opacity=0.7)
ax.add_title('Normal Distribution (n=200)')

v.add(ax)

v.show(end=1)
