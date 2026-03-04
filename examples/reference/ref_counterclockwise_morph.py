"""counterclockwise_morph: circle to square morph."""
from vectormation.objects import *

v = VectorMathAnim()
v.set_background()

circle = Circle(r=120, cx=960, cy=540, fill='#58C4DD', stroke='#58C4DD')
square = Rectangle(240, 240, x=960, y=540, fill='#E74C3C', stroke='#E74C3C')

morph = counterclockwise_morph(circle, square, start=0, end=2)

v.add(morph)

v.show(end=2)
