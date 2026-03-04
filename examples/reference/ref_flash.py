"""Circle with flash effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=100, fill='#E74C3C', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.flash(start=0.5, end=1.5, color='#FFFF00')

v.add(c)

v.show(end=2)
