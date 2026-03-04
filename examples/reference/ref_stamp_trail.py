"""Ghostly fading copies along path."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Dot(cx=200, cy=540, r=18, fill='#E74C3C')
c.fadein(start=0, end=0.2)
c.shift(dx=1500, start=0.3, end=2.5)
c.fadein(start=0, end=0.3)
ghosts = c.stamp_trail(start=0.3, end=2.5, count=6, fade_duration=0.6, opacity=0.5)
v.add(c)
v.add(*ghosts)

v.show(end=3)
