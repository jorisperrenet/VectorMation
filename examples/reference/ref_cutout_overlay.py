"""Rectangular cutout overlay (Cutout class)."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

title = Text('Important', x=960, y=400, font_size=72, fill='#FFFFFF', text_anchor='middle')
subtitle = Text('Focus here', x=960, y=700, font_size=36, fill='#aaa', text_anchor='middle')
v.add(title, subtitle)

cutout = Cutout(opacity=0.8, rx=12, ry=12)
cutout.surround(title, buff=30)
v.add(cutout)

v.show(end=0)
