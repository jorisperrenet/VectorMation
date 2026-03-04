"""Integer: animated whole-number display."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

n = Integer(0, font_size=96)
n.center_to_pos()
n.animate_value(42, start=0, end=2)

v.add(n)

v.show(end=2.5)
