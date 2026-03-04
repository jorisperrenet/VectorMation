"""RoundedRectangle shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

r = RoundedRectangle(300, 180, corner_radius=20, fill='#9B59B6', fill_opacity=0.6, stroke='#9B59B6')
v.add(r)

v.show(end=0)
