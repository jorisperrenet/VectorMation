"""Camera-like focus zoom."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = RegularPolygon(5, radius=90, fill='#9B59B6', fill_opacity=0.8)
c.fadein(start=0, end=0.3)
c.focus_zoom(start=0.3, end=1.5, zoom_factor=1.4)
v.add(c)

v.show(end=2)
