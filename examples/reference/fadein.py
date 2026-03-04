"""Compare fadein, write, and create side by side."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=80, cx=380, cy=540, fill='#58C4DD', fill_opacity=0.8)
c.fadein(start=0, end=1.5)

s = Square(side=160, x=800, y=540, fill='#E74C3C', fill_opacity=0.8)
s.center_to_pos()
s.write(start=0, end=1.5)

t = RegularPolygon(5, radius=85, cx=1540, cy=540, fill='#83C167', fill_opacity=0.8)
t.create(start=0, end=1.5)

v.add(c, s, t)

v.show(end=2)
