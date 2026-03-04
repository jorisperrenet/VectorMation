"""Flash the object border."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=90, fill='#3498DB', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.highlight_border(start=0.5, end=1.2, color='#FFFF00', width=6)
v.add(c)

v.show(end=2)
