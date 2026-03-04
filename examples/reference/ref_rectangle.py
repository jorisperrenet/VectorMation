"""Rectangle shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

r = Rectangle(300, 180, fill='#E74C3C', fill_opacity=0.6, stroke='#E74C3C')
v.add(r)

v.show(end=0)
