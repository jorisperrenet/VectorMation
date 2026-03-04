"""Indicate and flash effects on objects."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

circle = Circle(r=80, cx=600, cy=540, fill='#E74C3C', fill_opacity=0.8)
circle.fadein(start=0, end=0.5)
circle.indicate(start=1, end=2, scale_factor=1.3)

square = Square(side=160, x=1240, y=460, fill='#3498DB', fill_opacity=0.8)
square.fadein(start=0, end=0.5)
square.flash(start=1, end=2, color='#FFFF00')

v.add(circle, square)

v.show(end=3)
