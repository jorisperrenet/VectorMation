"""Attention-grabbing scale burst."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=80, fill='#E67E22', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.telegraph(start=0.5, end=1.2, scale_factor=1.5, shake_amplitude=10)
v.add(c)

v.show(end=2)
