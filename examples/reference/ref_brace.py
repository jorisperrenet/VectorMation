"""Brace annotation around a rectangle."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

rect = Rectangle(400, 150, fill='#3498DB', fill_opacity=0.4, stroke='#3498DB')
brace = Brace(rect, direction='down', label='400 px', stroke='#F39C12')

v.add(rect, brace)

v.show(end=0)
