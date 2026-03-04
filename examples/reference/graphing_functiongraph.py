"""FunctionGraph with draw_along animation."""
import math
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

curve = FunctionGraph(math.sin, x_range=(0, 2 * math.pi),
                      width=600, height=300, x=200, y=350)
curve.draw_along(start=0, end=2)

v.add(curve)

v.show(end=3)
