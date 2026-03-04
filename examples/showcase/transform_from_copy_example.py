"""Demonstrate transform_from_copy: morph a ghost copy while keeping the original."""
from vectormation.objects import *

v = VectorMathAnim()

# Source objects
circle = Circle(r=60, cx=400, cy=540, fill='#3498DB', fill_opacity=0.8, stroke_width=3)
circle.fadein(start=0, end=0.5)

square = Square(side=120, x=960, y=540, fill='#E74C3C', fill_opacity=0.8, stroke_width=3)
square.fadein(start=0, end=0.5)

star = Star(5, outer_radius=70, inner_radius=30, cx=1520, cy=540,
            fill='#F1C40F', fill_opacity=0.8, stroke_width=3)
star.fadein(start=0, end=0.5)

# Ghost copies morph between shapes (originals stay put)
ghost1 = circle.transform_from_copy(square, start=1, end=3)
ghost2 = square.transform_from_copy(star, start=2, end=4)
ghost3 = star.transform_from_copy(circle, start=3, end=5)

v.add(circle, square, star, ghost1, ghost2, ghost3)

v.show(end=6)
