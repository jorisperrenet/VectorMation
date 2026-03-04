"""TextBox with dark background."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

tb = TextBox('System Online', x=830, y=510, font_size=28, padding=16,
             box_fill='#1e1e2e', text_color='#58C4DD')

v.add(tb)

v.show(end=0)
