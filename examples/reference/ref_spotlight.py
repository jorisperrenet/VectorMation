"""Animated spotlight (Spotlight with moving target)."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c1 = Circle(r=60, cx=400, cy=540, fill='#58C4DD', fill_opacity=0.8)
c2 = Circle(r=60, cx=960, cy=540, fill='#FF6B6B', fill_opacity=0.8)
c3 = Circle(r=60, cx=1520, cy=540, fill='#83C167', fill_opacity=0.8)
v.add(c1, c2, c3)

spot = Spotlight(target=c1, radius=100, opacity=0.75)
spot.set_target(c2, start=0.5, end=1.5)
spot.set_target(c3, start=2.0, end=3.0)
v.add(spot)

v.show(end=3.5)
