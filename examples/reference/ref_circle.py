"""Circle shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=120, fill='#58C4DD', fill_opacity=0.6, stroke='#58C4DD')
v.add(c)

v.show(end=0)
