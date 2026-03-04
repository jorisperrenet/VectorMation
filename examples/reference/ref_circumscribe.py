"""Rectangle with circumscribe effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

r = Rectangle(200, 140, fill='#3498DB', fill_opacity=0.8)
r.fadein(start=0, end=0.3)
outline = r.circumscribe(start=0.5, end=2, buff=14, color='#FFFF00')

v.add(r, outline)

v.show(end=2.5)
