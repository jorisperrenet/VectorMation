"""Countdown timer display."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

cd = Countdown(start_value=10, end_value=0, font_size=120, start=0, end=3)

v.add(cd)

v.show(end=0)
