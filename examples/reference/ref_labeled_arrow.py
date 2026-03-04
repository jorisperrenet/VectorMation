"""LabeledArrow with midpoint text."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

la = LabeledArrow(x1=660, y1=540, x2=1260, y2=540, label='direction', stroke='#E74C3C')

v.add(la)

v.show(end=0)
