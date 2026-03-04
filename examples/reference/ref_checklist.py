"""Checklist with checked and unchecked items."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

cl = Checklist(
    ('Buy groceries', True),
    ('Walk the dog', True),
    'Write docs',
    'Deploy app',
    x=780, y=400,
)

v.add(cl)

v.show(end=0)
