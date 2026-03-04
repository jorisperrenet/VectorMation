"""Manim equivalent: HeatDiagramPlot -- line graph from discrete data points."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()
ax = Axes(x_range=(0, 40), y_range=(-8, 32),
          x_label=r'$\Delta Q$', y_label=r'$T[^\circ C]$')

x_vals = [0, 8, 38, 39]
y_vals = [20, 0, 0, -5]
graph = ax.plot_line_graph(x_vals, y_vals, stroke='#FFFF00')
canvas.add_objects(ax)

canvas.show()
