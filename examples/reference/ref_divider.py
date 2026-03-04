"""Divider with centered label."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

div = Divider(x=560, y=540, length=800, direction='horizontal',
              label='Section Break', stroke='#58C4DD')

v.add(div)

v.show(end=0)
