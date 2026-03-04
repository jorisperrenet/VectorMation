"""Dot moving with a visible trail."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

dot = Dot(cx=300, cy=540, r=16, fill='#FF6B6B')
dot.fadein(start=0, end=0.3)
dot.shift(dx=400, start=0.3, end=1.5)
dot.shift(dy=-200, start=1.5, end=2.5)
dot.shift(dx=500, start=2.5, end=4)

trail = dot.trace_path(start=0.3, end=4, stroke='#FF6B6B', stroke_width=6)

v.add(trail, dot)

v.show(end=4.5)
