"""Lines: open polyline through vertices."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

zigzag = Lines(
    (400, 700), (600, 380), (800, 700), (1000, 380), (1200, 700), (1400, 380), (1600, 700),
    stroke='#58C4DD', stroke_width=4, fill_opacity=0,
)

v.add(zigzag)

v.show(end=0)
