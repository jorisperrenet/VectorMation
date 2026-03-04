"""Underline beneath a text object."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

txt = Text(text='Important Text', x=960, y=520, font_size=48, fill='#fff', stroke_width=0)
ul = Underline(txt, buff=4, stroke='#58C4DD', stroke_width=3)

v.add(txt, ul)

v.show(end=0)
