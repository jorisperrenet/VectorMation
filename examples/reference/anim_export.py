"""Static composed scene for frame export."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

# A composed static scene
circle = Circle(r=100, cx=480, cy=440, fill='#58C4DD', fill_opacity=0.8, stroke_width=3)
rect = Rectangle(200, 140, x=860, y=370, fill='#E74C3C', fill_opacity=0.8, stroke_width=3)
star = Star(n=5, outer_radius=100, inner_radius=50, cx=1440, cy=440,
            fill='#F39C12', fill_opacity=0.8, stroke_width=3)
title = Text('Static Frame Export', x=700, y=700, font_size=56, fill='WHITE')

v.add(circle, rect, star, title)

v.show(end=1)
