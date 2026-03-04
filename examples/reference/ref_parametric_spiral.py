"""Parametric spiral using ParametricFunction."""
from vectormation.objects import *
import math

v = VectorMathAnim()
v.set_background()

spiral = ParametricFunction(
    lambda t: (960 + 200 * t * math.cos(6 * t), 540 + 200 * t * math.sin(6 * t)),
    t_range=(0, math.pi), num_points=300,
    stroke='#FC6255', stroke_width=3)

v.add(spiral)

v.show(end=0)
