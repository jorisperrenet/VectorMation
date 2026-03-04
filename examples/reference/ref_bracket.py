"""Bracket decoration with label."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

rect = Rectangle(300, 60, x=810, y=500, fill='#333', stroke='#58C4DD')
bracket = Bracket(x=810, y=570, width=300, height=20, direction='down',
                  stroke='#F39C12', text='width = 300')

v.add(rect, bracket)

v.show(end=0)
