"""Label with rounded background."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

label = Label('Hello World', x=960, y=540, font_size=36, padding=14)

v.add(label)

v.show(end=0)
