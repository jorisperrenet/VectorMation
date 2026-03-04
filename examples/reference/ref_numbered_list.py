"""NumberedList example."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

nl = NumberedList(
    'Define the problem',
    'Gather data',
    'Build a model',
    'Evaluate results',
    font_size=40, fill='#fff', stroke_width=0,
)
v.add(nl)

v.show(end=0)
