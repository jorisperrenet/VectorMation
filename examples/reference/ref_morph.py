"""MorphObject morphing a circle into a square."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

circle = Circle(r=120, fill='#58C4DD', fill_opacity=0.8, stroke='#58C4DD')
square = Rectangle(240, 240, fill='#E74C3C', fill_opacity=0.8, stroke='#E74C3C')

morph = MorphObject(circle, square, start=0.5, end=2.5)

v.add(morph)

v.show(end=3)
