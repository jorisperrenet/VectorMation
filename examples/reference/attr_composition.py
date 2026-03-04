"""Chaining multiple attribute calls over time."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

dot = Dot(cx=360, cy=540, r=20, fill='#E74C3C')
dot.fadein(start=0, end=0.5)

# Chain: move right, then set a constant position, then move again
dot.c.move_to(0.5, 2, (960, 540))       # slide to centre
dot.c.set_onward(2, (960, 300))          # jump up instantly
dot.c.move_to(2.5, 4, (1560, 540))      # slide to right

v.add(dot)

v.show(end=4.5)
