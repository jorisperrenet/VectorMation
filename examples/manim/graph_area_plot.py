"""Manim equivalent: GraphAreaPlot -- two curves with Riemann rects and area between curves."""
from vectormation.objects import *

canvas = VectorMathAnim()
canvas.set_background()
ax = Axes(x_range=(0, 5), y_range=(0, 6))

f1 = lambda x: 4 * x - x ** 2
f2 = lambda x: 0.8 * x ** 2 - 3 * x + 4
curve1 = ax.plot(f1, stroke='#58C4DD')
curve2 = ax.plot(f2, stroke='#83C167')

# Riemann rectangles under curve1 in x=[0.3, 0.6]
riemann = ax.get_riemann_rectangles(f1, x_range=(0.3, 0.6), dx=0.03,
                                    fill='#58C4DD', fill_opacity=0.5)

# Shaded area between curve2 and curve1 in x=[2, 3]
area = ax.get_area(curve2, x_range=(2, 3), bounded_graph=curve1,
                   fill='#888888', fill_opacity=0.5)

# Vertical reference lines at x=2 and x=3
vline1 = ax.get_vertical_line(2, y_val=f1(2))
vline2 = ax.get_vertical_line(3, y_val=f1(3))

canvas.add_objects(ax)

canvas.show()
