"""Timing model demo: sequential start/end animations."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

dot = Dot(cx=300, cy=540, r=20, fill='#58C4DD')
dot.fadein(start=0, end=0.5)

# Sequential animations using start= and end=
dot.shift(dx=300, start=0.5, end=1.5)   # move right
dot.shift(dy=-200, start=1.5, end=2.5)  # move up
dot.shift(dx=300, start=2.5, end=3.5)   # move right again
dot.shift(dy=200, start=3.5, end=4.5)   # move down

# Add time markers as text
for i, t in enumerate([0.5, 1.5, 2.5, 3.5, 4.5]):
    label = Text(f't={t}', x=300 + i * 150, y=900, font_size=24, fill='#666666')
    label.fadein(start=t - 0.2, end=t + 0.2)
    v.add(label)

v.add(dot)

v.show(end=5)
