"""Combined flash and scale emphasis."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Rectangle(width=180, height=120, fill='#E67E22', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.emphasize(start=0.5, end=1.3, color='#FFFF00', scale_factor=1.2)
v.add(c)

v.show(end=2)
