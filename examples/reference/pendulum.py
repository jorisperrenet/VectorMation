"""Pendulum with trail."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

p = Pendulum(pivot_x=960, pivot_y=150, length=350, angle=45,
             period=1.5, damping=0.1, start=0, end=8)
trail = p.bob.trace_path(start=0, end=8, stroke='#FF6B6B',
                         stroke_width=1, stroke_opacity=0.5)

v.add(p, trail)

v.show(end=8)
