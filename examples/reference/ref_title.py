"""Title with underline."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

title = Title('Introduction to Calculus')

v.add(title)

v.show(end=0)
