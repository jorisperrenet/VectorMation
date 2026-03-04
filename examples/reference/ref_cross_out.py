"""Draw an X across the object."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Rectangle(width=180, height=120, fill='#3498DB', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
cross = c.cross_out(start=0.5, end=1.2, color='#FC6255', stroke_width=5)
v.add(c)
v.add(cross)

v.show(end=2)
