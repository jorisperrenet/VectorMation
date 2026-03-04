"""Path shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

d = 'M 560,640 C 660,300 1260,300 1360,640'
p = Path(d, stroke='#E74C3C', stroke_width=5, fill_opacity=0)
v.add(p)

v.show(end=0)
