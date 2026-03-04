"""Tooltip near a target object."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

dot = Dot(cx=960, cy=540, fill='#58C4DD')
tip = Tooltip('Hover info', target=(960, 540), start=0, duration=2)

v.add(dot, tip)

v.show(end=0)
