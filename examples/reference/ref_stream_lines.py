"""StreamLines for a swirl field."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

def swirl(x, y):
    dx, dy = x - 960, y - 540
    return (-dy, dx)

streams = StreamLines(swirl, n_steps=60, step_size=8,
                      stroke='#83C167', stroke_width=2)
v.add(streams)

v.show(end=0)
