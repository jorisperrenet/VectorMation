"""Ghost trail following a moving object."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Dot(cx=300, cy=540, r=16, fill='#E67E22')
c.fadein(start=0, end=0.3)
c.shift(dx=1300, start=0.3, end=2.5)
ghosts = c.trail(start=0.3, end=2.5, n_copies=6, fade=True)
v.add(c)
v.add(*ghosts)

v.show(end=3)
