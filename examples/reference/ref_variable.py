"""Variable display with numeric value."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

var = Variable(label='x', value=3.14, font_size=48)

v.add(var)

v.show(end=0)
