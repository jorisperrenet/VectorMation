"""Basic canvas scene with shapes."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background(fill='#1a1a2e')

c = Circle(r=100, cx=600, cy=540, fill='#58C4DD', fill_opacity=0.8)
r = Rectangle(200, 140, x=1220, y=470, fill='#E74C3C', fill_opacity=0.8)
t = Text('Hello!', x=960, y=300, font_size=60, fill='#fff',
         stroke_width=0, text_anchor='middle')

v.add(c, r, t)

v.show(end=0)
