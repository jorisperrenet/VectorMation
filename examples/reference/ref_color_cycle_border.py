"""Animated color-cycling border (AnimatedBoundary)."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

rect = Rectangle(300, 200, fill='#1a1a2e', fill_opacity=0.9)
rect.center_to_pos(posx=960, posy=540)
border = AnimatedBoundary(rect, cycle_rate=0.5, buff=10, stroke_width=4)
v.add(rect, border)

v.show(end=4)
