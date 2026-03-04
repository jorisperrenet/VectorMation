"""Arc and wedge drawing."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

a = Arc(r=100, start_angle=0, end_angle=270, cx=600, cy=540,
        stroke='#58C4DD', stroke_width=5, fill_opacity=0)
w = Wedge(r=100, start_angle=30, end_angle=300, cx=1320, cy=540,
          fill='#E74C3C', fill_opacity=0.6, stroke_width=2)

l1 = Text('Arc', x=600, y=700, font_size=24, fill='#aaa', text_anchor='middle')
l2 = Text('Wedge', x=1320, y=700, font_size=24, fill='#aaa', text_anchor='middle')

v.add(a, w, l1, l2)

v.show(end=2)
