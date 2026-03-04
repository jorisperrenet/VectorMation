"""Typewriter effect with cursor."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

title = Text('$ pip install vectormation', x=200, y=400,
             font_size=40, font_family='monospace', fill='#0f0')
title.typewrite(start=0, end=2, cursor='_')

subtitle = Text('Installation complete.', x=200, y=480,
                font_size=32, font_family='monospace', fill='#0f0')
subtitle.typewrite(start=2.5, end=3.5, cursor='_')

v.add(title, subtitle)

v.show(end=4)
