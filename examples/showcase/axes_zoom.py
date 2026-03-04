"""Animated axis zoom and pan — showcasing animated Real ranges on Axes."""
from vectormation.objects import *
from vectormation import attributes
from vectormation import easings

canvas = VectorMathAnim()
canvas.set_background()

ax = Axes(x_range=(-5, 5), y_range=(-2, 26), x_label='x', y_label='y')
ax.add_coordinates(tex=True)

f = lambda x: x ** 2
curve = ax.plot(f, label='$f(x)=x^2$', stroke='#58C4DD', stroke_width=4)

# Draw the curve in
create_anim = curve.create(start=0, end=2)

# Zoom into x=[1, 4], y=[0, 18] to inspect the curve more closely
ax.set_ranges((1, 4), (0, 18), start=3, end=5)

# Add a shaded area that appears after zooming in
area = ax.get_area(f, x_range=(1.5, 3.5), fill='#58C4DD', fill_opacity=0.3)
area.fadein(5.5, 6.5)

# Zoom back out to full view
ax.set_ranges((-5, 5), (-2, 26), start=7, end=9)

# Pan to the right: shift window to x=[0, 10], y=[0, 100]
ax.set_ranges((0, 10), (0, 100), start=10, end=12)

# Add a dot tracking along the curve during the pan
dot = Dot(fill='#FFFF00')
x_val = attributes.Real(0, 2)
x_val.move_to(10, 14, 9)
dot.c.set_onward(10, ax.graph_position(f, x_val))
dot.fadein(10, 10.5)

canvas.add_objects(ax, create_anim, dot)

canvas.show(end=14)
