"""Manim equivalent: PolygonOnAxes -- dynamic rectangle under a 1/x curve."""
from vectormation.objects import *
from vectormation import attributes

canvas = VectorMathAnim()
canvas.set_background()
ax = Axes(x_range=(0, 10), y_range=(0, 10), tex_ticks=True)

f = lambda x: 25 / x if x > 0.1 else 100
curve = ax.plot(f, stroke='yellow')

# Animated t from 5 -> 9 -> 2.5 -> 5
t_attr = attributes.Real(0, 5)
t_attr.move_to(0, 2, 9)
t_attr.move_to(2, 4, 2.5)
t_attr.move_to(4, 6, 5)

rect = ax.get_rect(0, 0, t_attr, t_attr.apply(f),
                   fill='blue', fill_opacity=0.4, stroke='yellow')

dot = Dot(fill='#fff')
dot.c.set_onward(0, ax.graph_position(f, t_attr))

# Also add final morphing because we can
star = Star(outer_radius=100, fill='green')
circle = Cross(200)
rect2 = Rectangle(200, 200, fill='green')
coll = VCollection(star, circle, rect2).arrange_in_grid(1, 3, buff=100).center_to_pos()
coll.spin(7, 8)
morph = MorphObject(rect, star, 6, 7)
morph2 = MorphObject(curve, circle, 6, 7)
morph3 = MorphObject(ax.axes, rect2, 6, 7)
dot.fadeout(6, 7)

canvas.add_objects(ax, dot)
canvas.add_objects(morph, morph2, morph3, coll)

canvas.show()
