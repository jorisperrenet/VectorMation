"""Double-pulse heartbeat effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=80, fill='#E74C3C', fill_opacity=0.9)
c.fadein(start=0, end=0.3)
c.heartbeat(start=0.2, end=2.5, beats=3, scale_factor=1.3)
v.add(c)

v.show(end=3)
