"""LabeledLine with midpoint text."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

ll = LabeledLine(x1=660, y1=540, x2=1260, y2=540, label='600 px', stroke='#58C4DD')

v.add(ll)

v.show(end=0)
