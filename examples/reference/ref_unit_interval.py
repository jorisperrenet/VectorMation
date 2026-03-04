"""UnitInterval: probability axis."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

ui = UnitInterval(x=360, y=540, length=1200, tick_step=0.1)

v.add(ui)

v.show(end=0)
