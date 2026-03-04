"""PeriodicTable display."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

table = PeriodicTable(cell_size=52)

v.add(table)

v.show(end=0)
