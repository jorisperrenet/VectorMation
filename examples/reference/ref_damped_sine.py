"""Damped sine wave using FunctionGraph."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

curve = FunctionGraph(lambda x: math.sin(x) * math.exp(-x / 5),
                      x_range=(0, 20), stroke='#2ECC71', stroke_width=3)

v.add(curve)

v.show(end=0)
