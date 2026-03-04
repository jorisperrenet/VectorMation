"""SampleSpace with horizontal division."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

space = SampleSpace(width=800, height=500, x=560, y=290)
space.divide_horizontally(0.6, colors=('#58C4DD', '#FC6255'), labels=['P(A) = 0.6', 'P(B) = 0.4'])

v.add(space)

v.show(end=0)
