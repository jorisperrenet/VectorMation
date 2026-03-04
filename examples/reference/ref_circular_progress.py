"""CircularProgressBar indicator."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

chart = CircularProgressBar(
    value=73,
    radius=200,
    stroke_width=24,
    font_size=72,
)

v.add(chart)

v.show(end=0)
