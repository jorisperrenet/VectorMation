"""Text shape."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

t = Text('Hello, World!', x=960, y=540, font_size=72,
         fill='#fff', stroke_width=0, text_anchor='middle')
v.add(t)

v.show(end=0)
