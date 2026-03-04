"""Save state, modify, then restore."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

c = Circle(r=60, cx=960, cy=540, fill='#58C4DD', fill_opacity=0.8)
c.fadein(start=0, end=0.5)
c.save_state()

c.shift(dx=300, start=1, end=2)
c.set_color(1, 2, fill='#FF0000')
c.scale(1.5, start=1, end=2)

c.restore(start=3, end=4)

label = Text('restore to saved state at t=3', x=960, y=700,
             font_size=28, fill='#888', text_anchor='middle')
label.fadein(start=0, end=0.5)

v.add(c, label)

v.show(end=5)
