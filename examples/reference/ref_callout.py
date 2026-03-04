"""Callout pointing to a target position."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

dot = Dot(cx=960, cy=540, fill='#58C4DD')
callout = Callout('Look here!', target=(960, 540), direction='up', distance=80)

v.add(dot, callout)

v.show(end=0)
