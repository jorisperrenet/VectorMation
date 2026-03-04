"""Line shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

l = Line(x1=560, y1=640, x2=1360, y2=440, stroke='#2ECC71', stroke_width=5)
v.add(l)

v.show(end=0)
