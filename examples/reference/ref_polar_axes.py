"""PolarAxes: polar coordinate system."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

pa = PolarAxes(r_range=(0, 3), max_radius=350)

v.add(pa)

v.show(end=0)
