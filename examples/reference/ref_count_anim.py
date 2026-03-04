"""CountAnimation example."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

counter = CountAnimation(0, 100, start=0, end=2, fmt='{:.0f}',
                         font_size=80, fill='#58C4DD', stroke_width=0,
                         text_anchor='middle')
counter.center_to_pos()
v.add(counter)

v.show(end=2.5)
