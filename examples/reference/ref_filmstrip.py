"""Filmstrip storyboard display."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

strip = Filmstrip(
    labels=['Intro', 'Setup', 'Conflict', 'Climax', 'Resolution'],
    x=185, y=440, frame_width=260, frame_height=160, spacing=30,
)

v.add(strip)

v.show(end=0)
