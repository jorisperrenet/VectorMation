"""Scramble decode effect."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

code = Text('ACCESS GRANTED', x=960, y=500, font_size=64,
            fill='#0f0', text_anchor='middle', font_family='monospace')
code.scramble(start=0, end=2)

v.add(code)

v.show(end=3)
