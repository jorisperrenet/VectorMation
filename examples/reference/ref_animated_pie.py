"""Animated pie chart with value transitions."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

pie = PieChart([30, 20, 50], labels=['A', 'B', 'C'])
pie.fadein(start=0, end=1)
pie.animate_values([40, 40, 20], start=2, end=3)

v.add(pie)

v.show(end=4)
