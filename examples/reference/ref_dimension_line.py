"""DimensionLine between two points."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

rect = Rectangle(400, 200, x=760, y=440, fill='#333', stroke='#58C4DD')
dim = DimensionLine(p1=(760, 440), p2=(1160, 440), label='400 px', offset=40)

v.add(rect, dim)

v.show(end=0)
