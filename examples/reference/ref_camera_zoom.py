"""Camera zoom example."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background(fill='#1a1a2e')

c1 = Circle(r=60, cx=500, cy=400, fill='#58C4DD', fill_opacity=0.8)
c2 = Circle(r=60, cx=1420, cy=640, fill='#E74C3C', fill_opacity=0.8)
c1.fadein(start=0, end=0.5)
c2.fadein(start=0, end=0.5)

v.camera_zoom(2.5, start=1, end=2.5, cx=500, cy=400)
v.camera_reset(3.5, 5)

v.add(c1, c2)

v.show(end=6)
