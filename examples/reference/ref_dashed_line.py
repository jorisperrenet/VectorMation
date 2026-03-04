"""DashedLine shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

l = DashedLine(x1=560, y1=640, x2=1360, y2=440, dash='12,6', stroke='#F39C12', stroke_width=4)
v.add(l)

v.show(end=0)
