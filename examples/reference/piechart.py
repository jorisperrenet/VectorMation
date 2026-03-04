"""Pie chart with highlighted sector."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

pie = PieChart([35, 25, 20, 20], labels=['Python', 'JS', 'Rust', 'Go'])
pie.add_percentage_labels()
pie.explode([0], distance=20)

v.add(pie)

v.show(end=2)
