"""Meter bar (vertical fill level)."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

meter = Meter(value=0.65, x=940, y=340, width=40, height=200,
              direction='vertical', fill_color='#2ECC71')

v.add(meter)

v.show(end=0)
