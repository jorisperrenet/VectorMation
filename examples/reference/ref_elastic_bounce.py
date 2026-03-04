"""Bouncing with squash and stretch."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=50, fill='#2ECC71', fill_opacity=0.9)
c.fadein(start=0, end=0.3)
c.elastic_bounce(start=0.3, end=2.5, height=150, n_bounces=4, squash_factor=1.5)
v.add(c)

v.show(end=3)
