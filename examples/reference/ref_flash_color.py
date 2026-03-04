"""Quick color flash effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = RegularPolygon(6, radius=100, fill='#3498DB', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.flash_color(color='#FF6B6B', start=0.5, end=1.2)
v.add(c)

v.show(end=2)
