"""Paragraph example."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

p = Paragraph(
    'First line of text.',
    'Second line continues here.',
    'Third and final line.',
    alignment='center', font_size=44, fill='#fff', stroke_width=0,
)
p.center_to_pos()
v.add(p)

v.show(end=0)
